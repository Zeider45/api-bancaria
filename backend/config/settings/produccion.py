from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# SUDEBAN VPN Configuration
SUDEBAN_API_URL = os.environ.get('SUDEBAN_API_URL', 'https://transacciones-demo.sudeban.gob.ve/api/transmission')
SUDEBAN_USERNAME = os.environ.get('SUDEBAN_USERNAME')
SUDEBAN_PASSWORD = os.environ.get('SUDEBAN_PASSWORD')
SUDEBAN_WEBHOOK_URL = os.environ.get('SUDEBAN_WEBHOOK_URL')

# Security settings
DJANGO_FORCE_SSL = os.environ.get('DJANGO_FORCE_SSL', 'true').strip().lower() in ('1', 'true', 'yes', 'on')
SECURE_SSL_REDIRECT = DJANGO_FORCE_SSL
SESSION_COOKIE_SECURE = DJANGO_FORCE_SSL
CSRF_COOKIE_SECURE = DJANGO_FORCE_SSL
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/sib_bridge.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
import os
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# --- Celery (production) ---
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_WORKER_PREFETCH_MULTIPLIER = int(os.environ.get('CELERY_WORKER_PREFETCH_MULTIPLIER', '1'))
CELERY_WORKER_MAX_TASKS_PER_CHILD = int(os.environ.get('CELERY_WORKER_MAX_TASKS_PER_CHILD', '200'))
CELERY_TASK_TIME_LIMIT = int(os.environ.get('CELERY_TASK_TIME_LIMIT', str(60 * 10)))
CELERY_TASK_SOFT_TIME_LIMIT = int(os.environ.get('CELERY_TASK_SOFT_TIME_LIMIT', str(60 * 9)))
