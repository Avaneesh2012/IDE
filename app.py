import os
import tempfile
import subprocess
import logging
import secrets
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from io import BytesIO
from functools import wraps
from datetime import datetime, timedelta

from flask import (
    Flask, render_template, request, send_from_directory, 
    session, redirect, url_for, send_file, make_response,
    flash, abort, jsonify
)
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('futuride.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'.py', '.c', '.html', '.txt', '.js', '.css'}
    EXECUTION_TIMEOUT = 10  # seconds
    MAX_CODE_LENGTH = 50000  # characters
    RATE_LIMIT_REQUESTS = 50  # requests per hour
    RATE_LIMIT_WINDOW = 3600  # seconds

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

# Rate limiting storage (in production, use Redis)
rate_limit_storage = {}

def rate_limit(f):
    """Simple rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.config.get('TESTING'):
            return f(*args, **kwargs)
        
        client_ip = request.remote_addr
        now = datetime.now()
        
        if client_ip in rate_limit_storage:
            requests, window_start = rate_limit_storage[client_ip]
            if now - window_start > timedelta(seconds=app.config['RATE_LIMIT_WINDOW']):
                rate_limit_storage[client_ip] = (1, now)
            elif requests >= app.config['RATE_LIMIT_REQUESTS']:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
            else:
                rate_limit_storage[client_ip] = (requests + 1, window_start)
        else:
            rate_limit_storage[client_ip] = (1, now)
        
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in app.config['ALLOWED_EXTENSIONS']

def validate_code(code: str, language: str) -> Tuple[bool, Optional[str]]:
    """Validate code input"""
    if not code or not code.strip():
        return False, "Code cannot be empty"
    
    if len(code) > app.config['MAX_CODE_LENGTH']:
        return False, f"Code too long. Maximum {app.config['MAX_CODE_LENGTH']} characters allowed."
    
    # Basic security checks
    dangerous_patterns = [
        'import os', 'import sys', 'import subprocess', 'eval(', 'exec(',
        '__import__', 'globals()', 'locals()', 'open(', 'file(',
        'system(', 'popen(', 'spawn(', 'fork(', 'kill('
    ]
    
    code_lower = code.lower()
    for pattern in dangerous_patterns:
        if pattern in code_lower:
            return False, f"Potentially dangerous code detected: {pattern}"
    
    return True, None

def execute_python_code(code: str) -> Tuple[Optional[str], Optional[str]]:
    """Execute Python code safely"""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        # Run in a restricted environment
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=app.config['EXECUTION_TIMEOUT'],
            cwd=tempfile.gettempdir(),
            env={'PYTHONPATH': '', 'PATH': '/usr/bin:/bin'}
        )
        
        return result.stdout, result.stderr if result.stderr else None
        
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"
    except Exception as e:
        logger.error(f"Python execution error: {e}")
        return None, f"Execution error: {str(e)}"
    finally:
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file)
            except OSError:
                pass

def execute_c_code(code: str) -> Tuple[Optional[str], Optional[str]]:
    """Execute C code safely"""
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(code)
            c_file = f.name
        
        exe_file = c_file[:-2] + '.exe' if os.name == 'nt' else c_file[:-2]
        
        # Compile
        compile_result = subprocess.run(
            ['gcc', c_file, '-o', exe_file, '-Wall', '-Wextra'],
            capture_output=True,
            text=True,
            timeout=app.config['EXECUTION_TIMEOUT']
        )
        
        if compile_result.returncode != 0:
            return None, compile_result.stderr
        
        # Execute
        run_result = subprocess.run(
            [exe_file],
            capture_output=True,
            text=True,
            timeout=app.config['EXECUTION_TIMEOUT'],
            cwd=tempfile.gettempdir()
        )
        
        return run_result.stdout, run_result.stderr if run_result.stderr else None
        
    except subprocess.TimeoutExpired:
        return None, "Execution timed out"
    except FileNotFoundError:
        return None, "GCC compiler not found. Please install GCC to run C code."
    except Exception as e:
        logger.error(f"C execution error: {e}")
        return None, f"Execution error: {str(e)}"
    finally:
        # Cleanup
        for file_path in ['c_file', 'exe_file']:
            if file_path in locals():
                try:
                    os.unlink(locals()[file_path])
                except (OSError, KeyError):
                    pass

def get_language_info() -> Dict[str, Dict[str, Any]]:
    """Get supported languages information"""
    return {
        'python': {
            'name': 'Python',
            'extension': '.py',
            'syntax': 'python',
            'template': 'print("Hello, World!")'
        },
        'c': {
            'name': 'C',
            'extension': '.c',
            'syntax': 'c',
            'template': '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}'
        },
        'html': {
            'name': 'HTML',
            'extension': '.html',
            'syntax': 'html',
            'template': '<!DOCTYPE html>\n<html>\n<head>\n    <title>Hello World</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n</body>\n</html>'
        },
        'javascript': {
            'name': 'JavaScript',
            'extension': '.js',
            'syntax': 'javascript',
            'template': 'console.log("Hello, World!");'
        }
    }

@app.route('/')
def landing():
    """Landing page"""
    return render_template('landing.html')

@app.route('/ide', methods=['GET', 'POST'])
@rate_limit
def index():
    """Main IDE interface"""
    output = error = html_preview = None
    theme = session.get('theme', 'light')
    code = session.get('code', '')
    language = session.get('language', 'python')
    
    if request.method == 'POST':
        try:
            # Handle theme switching
            if request.form.get('theme_only') == '1':
                theme = request.form.get('theme', 'light')
                session['theme'] = theme
                return redirect(url_for('index'))
            
            # Handle file operations
            file_action = request.form.get('file_action')
            if file_action:
                return handle_file_action(file_action, request)
            
            # Handle code execution
            return handle_code_execution(request, theme, code, language)
            
        except Exception as e:
            logger.error(f"Error in IDE: {e}")
            error = "An unexpected error occurred. Please try again."
    
    languages = get_language_info()
    return render_template('index.html', 
                         output=output, 
                         error=error, 
                         html_preview=html_preview, 
                         theme=theme, 
                         code=code,
                         language=language,
                         languages=languages)

def handle_file_action(file_action: str, request) -> Any:
    """Handle file upload, new file, and download actions"""
    if file_action == 'upload' and 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            if not allowed_file(file.filename):
                flash('Invalid file type. Allowed: .py, .c, .html, .txt, .js, .css', 'error')
                return redirect(url_for('index'))
            
            try:
                content = file.read().decode('utf-8', errors='replace')
                session['code'] = content
                session['language'] = get_language_from_filename(file.filename)
                flash('File uploaded successfully!', 'success')
            except Exception as e:
                logger.error(f"File upload error: {e}")
                flash('Error reading file. Please try again.', 'error')
    
    elif file_action == 'new':
        session['code'] = ''
        session['language'] = 'python'
        flash('New file created!', 'success')
    
    elif file_action == 'download':
        code = request.form.get('code', '')
        if code:
            response = make_response(code)
            response.headers['Content-Type'] = 'text/plain'
            response.headers['Content-Disposition'] = 'attachment; filename=code.txt'
            return response
    
    return redirect(url_for('index'))

def handle_code_execution(request, theme: str, code: str, language: str) -> Any:
    """Handle code execution"""
    language = request.form.get('language', language)
    code = request.form.get('code', code)
    
    # Update session
    session['language'] = language
    session['code'] = code
    
    # Validate code
    is_valid, error_msg = validate_code(code, language)
    if not is_valid:
        return render_template('index.html', 
                             error=error_msg, 
                             theme=theme, 
                             code=code,
                             language=language,
                             languages=get_language_info())
    
    # Execute code based on language
    output = error = html_preview = None
    
    if language == 'python':
        output, error = execute_python_code(code)
    elif language == 'c':
        output, error = execute_c_code(code)
    elif language == 'html':
        html_preview = code
    elif language == 'javascript':
        # For JavaScript, we'll show it in a console-like output
        output = f"JavaScript code:\n{code}\n\n(JavaScript execution in browser console)"
    else:
        error = f'Unsupported language: {language}'
    
    return render_template('index.html', 
                         output=output, 
                         error=error, 
                         html_preview=html_preview, 
                         theme=theme, 
                         code=code,
                         language=language,
                         languages=get_language_info())

def get_language_from_filename(filename: str) -> str:
    """Get language from filename extension"""
    ext = Path(filename).suffix.lower()
    language_map = {
        '.py': 'python',
        '.c': 'c',
        '.html': 'html',
        '.js': 'javascript'
    }
    return language_map.get(ext, 'python')

@app.route('/download/windows')
def download_windows():
    """Download Windows executable"""
    exe_path = Path('dist') / 'futuride_desktop.exe'
    if exe_path.exists():
        return send_file(exe_path, as_attachment=True, download_name='FuturIDE.exe')
    else:
        abort(404, description="Windows installer not found. Please build the executable first.")

@app.route('/download/mac')
def download_mac():
    """Download Mac executable (placeholder)"""
    return send_file(
        BytesIO(b'FuturIDE Mac installer coming soon!'), 
        as_attachment=True, 
        download_name='FuturIDE_Mac.txt'
    )

@app.route('/api/execute', methods=['POST'])
@rate_limit
def api_execute():
    """API endpoint for code execution"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        # Validate input
        is_valid, error_msg = validate_code(code, language)
        if not is_valid:
            return jsonify({'error': error_msg}), 400
        
        # Execute code
        output = error = None
        if language == 'python':
            output, error = execute_python_code(code)
        elif language == 'c':
            output, error = execute_c_code(code)
        elif language == 'html':
            return jsonify({'html_preview': code})
        else:
            return jsonify({'error': f'Unsupported language: {language}'}), 400
        
        return jsonify({
            'output': output,
            'error': error,
            'success': error is None
        })
        
    except Exception as e:
        logger.error(f"API execution error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {e}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
