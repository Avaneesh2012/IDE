# Gunicorn configuration file for FuturIDE
import os
import multiprocessing

# Server socket
bind = "0.0.0.0:" + os.environ.get("PORT", "8000")
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "futuride"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (not needed on Render as they handle SSL)
keyfile = None
certfile = None

# Preload app for better performance
preload_app = True

# Worker timeout for graceful shutdown
graceful_timeout = 30

# Enable auto-reload in development
reload = os.environ.get("FLASK_ENV") == "development" 