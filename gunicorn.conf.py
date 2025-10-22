# Minimal gunicorn config for the Django project
bind = '0.0.0.0:8000'
workers = 3
threads = 2
user = None

# You can add timeout, logging, preload_app, etc. as needed.
