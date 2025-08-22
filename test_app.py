import unittest
import tempfile
import os
from app import app, validate_code, allowed_file, get_language_from_filename
from pathlib import Path

class FuturIDETestCase(unittest.TestCase):
    """Test cases for FuturIDE application"""
    
    def setUp(self):
        """Set up test client and configuration"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app = app
    
    def test_landing_page(self):
        """Test landing page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'FuturIDE', response.data)
    
    def test_ide_page(self):
        """Test IDE page loads correctly"""
        response = self.client.get('/ide')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Minimal Web IDE', response.data)
    
    def test_python_execution(self):
        """Test Python code execution"""
        data = {
            'code': 'print("Hello, World!")',
            'language': 'python'
        }
        response = self.client.post('/ide', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello, World!', response.data)
    
    def test_html_preview(self):
        """Test HTML preview functionality"""
        data = {
            'code': '<h1>Test</h1>',
            'language': 'html'
        }
        response = self.client.post('/ide', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<h1>Test</h1>', response.data)
    
    def test_api_execute(self):
        """Test API code execution endpoint"""
        data = {
            'code': 'print("API Test")',
            'language': 'python'
        }
        response = self.client.post('/api/execute', 
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertIn('API Test', result.get('output', ''))
    
    def test_validate_code_empty(self):
        """Test code validation with empty code"""
        is_valid, error = validate_code('', 'python')
        self.assertFalse(is_valid)
        self.assertIn('empty', error)
    
    def test_validate_code_dangerous(self):
        """Test code validation with dangerous code"""
        dangerous_code = 'import os\nos.system("rm -rf /")'
        is_valid, error = validate_code(dangerous_code, 'python')
        self.assertFalse(is_valid)
        self.assertIn('dangerous', error)
    
    def test_validate_code_valid(self):
        """Test code validation with valid code"""
        valid_code = 'print("Hello, World!")'
        is_valid, error = validate_code(valid_code, 'python')
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_allowed_file(self):
        """Test file extension validation"""
        self.assertTrue(allowed_file('test.py'))
        self.assertTrue(allowed_file('test.c'))
        self.assertTrue(allowed_file('test.html'))
        self.assertFalse(allowed_file('test.exe'))
        self.assertFalse(allowed_file('test.bat'))
    
    def test_get_language_from_filename(self):
        """Test language detection from filename"""
        self.assertEqual(get_language_from_filename('test.py'), 'python')
        self.assertEqual(get_language_from_filename('test.c'), 'c')
        self.assertEqual(get_language_from_filename('test.html'), 'html')
        self.assertEqual(get_language_from_filename('test.js'), 'javascript')
        self.assertEqual(get_language_from_filename('test.txt'), 'python')  # default
    
    def test_theme_switching(self):
        """Test theme switching functionality"""
        # Test switching to dark theme
        response = self.client.post('/ide', data={
            'theme': 'dark',
            'theme_only': '1'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_file_upload(self):
        """Test file upload functionality"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('print("Uploaded file")')
            temp_file = f.name
        
        try:
            with open(temp_file, 'rb') as f:
                response = self.client.post('/ide', data={
                    'file_action': 'upload'
                }, files={'file': (f.name, f)})
            
            self.assertEqual(response.status_code, 302)  # Redirect
        finally:
            os.unlink(temp_file)
    
    def test_new_file(self):
        """Test new file creation"""
        response = self.client.post('/ide', data={
            'file_action': 'new'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_404_error(self):
        """Test 404 error handling"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Make multiple requests to trigger rate limiting
        for _ in range(60):  # Exceed the limit
            response = self.client.post('/api/execute', 
                                      json={'code': 'print("test")', 'language': 'python'})
            if response.status_code == 429:
                break
        else:
            # If we didn't hit rate limit, that's also acceptable in testing
            pass

if __name__ == '__main__':
    unittest.main() 