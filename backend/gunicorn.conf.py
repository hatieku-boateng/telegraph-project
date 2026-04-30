"""Gunicorn configuration for production deployment."""

import multiprocessing
import os

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Workers: (2 × CPU cores) + 1 is the standard recommendation
workers = multiprocessing.cpu_count() * 2 + 1

# Use gevent or sync worker; sync is safe for this CPU-light app
worker_class = "sync"

# Timeouts
timeout = 120
keepalive = 5

# Logging
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"   # stdout
errorlog = "-"    # stderr

# Security
limit_request_line = 4096
limit_request_fields = 100
