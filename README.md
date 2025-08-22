# FuturIDE - Modern Web IDE

A futuristic, cross-platform web IDE for C, Python, HTML, and JavaScript with modern UI and enhanced security features.

## ✨ Features

### 🚀 Core Features
- **Multi-language Support**: Python, C, HTML, JavaScript
- **Real-time Code Execution**: Execute code directly in the browser
- **File Management**: Upload, download, and create new files
- **Theme Support**: Light and dark themes
- **Responsive Design**: Works on desktop and mobile devices

### 🔒 Security Enhancements
- **Input Validation**: Comprehensive code validation and sanitization
- **Rate Limiting**: Prevents abuse with configurable rate limits
- **Secure File Handling**: Safe temporary file creation and cleanup
- **Dangerous Code Detection**: Blocks potentially harmful code patterns
- **Session Security**: Secure session management with configurable settings

### 🛠️ Developer Experience
- **Code Templates**: Quick-start templates for each language
- **Auto-save**: Code is automatically saved to browser session storage
- **Error Handling**: Comprehensive error messages and logging
- **API Endpoints**: RESTful API for programmatic access
- **Logging**: Detailed application logging for debugging

### 🎨 User Interface
- **Modern Design**: Beautiful, rounded UI with smooth animations
- **Flash Messages**: User-friendly success and error notifications
- **Responsive Layout**: Adapts to different screen sizes
- **Accessibility**: Keyboard navigation and screen reader support

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- GCC (for C code execution)
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd futuride
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables (optional)**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export FLASK_ENV="development"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
futuride/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/           # HTML templates
│   ├── index.html      # Main IDE interface
│   ├── landing.html    # Landing page
│   ├── 404.html        # 404 error page
│   └── 500.html        # 500 error page
├── uploads/            # File upload directory
├── dist/              # Built executables (for downloads)
└── futuride.log       # Application logs
```

## ⚙️ Configuration

The application uses a flexible configuration system with environment-specific settings:

### Environment Variables
- `SECRET_KEY`: Secret key for session management
- `FLASK_ENV`: Environment mode (development/production/testing)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

### Configuration Classes
- `DevelopmentConfig`: Development settings with debug enabled
- `ProductionConfig`: Production settings with security hardening
- `TestingConfig`: Testing settings with relaxed limits

## 🔧 API Reference

### Code Execution API
```http
POST /api/execute
Content-Type: application/json

{
    "code": "print('Hello, World!')",
    "language": "python"
}
```

**Response:**
```json
{
    "output": "Hello, World!\n",
    "error": null,
    "success": true
}
```

### Error Responses
- `400`: Invalid input or unsupported language
- `413`: File too large
- `429`: Rate limit exceeded
- `500`: Internal server error

## 🛡️ Security Features

### Code Validation
The application validates all code input to prevent:
- Empty or excessively long code
- Dangerous system calls
- File system access
- Process manipulation

### Rate Limiting
- Configurable request limits per IP address
- Sliding window rate limiting
- Automatic rate limit reset

### File Security
- Restricted file type uploads
- Secure temporary file handling
- Automatic cleanup of temporary files
- Path traversal protection

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
For production deployment, consider using:
- **WSGI Server**: Gunicorn or uWSGI
- **Reverse Proxy**: Nginx or Apache
- **Process Manager**: Supervisor or systemd
- **HTTPS**: SSL/TLS certificates

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 🧪 Testing

Run tests with the testing configuration:
```bash
export FLASK_ENV=testing
python -m pytest tests/
```

## 📝 Logging

The application logs to both file and console:
- **File**: `futuride.log`
- **Console**: Standard output
- **Levels**: DEBUG, INFO, WARNING, ERROR

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- C code execution requires GCC to be installed
- JavaScript execution is limited to console output
- File uploads are limited to 16MB

## 🔮 Future Enhancements

- [ ] AI-powered code suggestions
- [ ] Real-time collaboration
- [ ] Git integration
- [ ] Plugin system
- [ ] More language support
- [ ] Advanced debugging features

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the logs for debugging information

---

**FuturIDE** - Building the future of web development, one line of code at a time. 
