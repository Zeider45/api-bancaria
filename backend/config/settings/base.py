import os
from pathlib import Path
from datetime import timedelta

try:
    import environ
except Exception:  # pragma: no cover
    environ = None

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-dev-key-change-in-production')

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'corsheaders',
    'django_extensions',
    
    # Local apps
    'apps.core',
    'apps.intervencion_bancaria',
    'apps.subasta_privada',
    'apps.resultados_subasta',
    'apps.operaciones_mesa_de_cambio',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL and DATABASE_URL.startswith('sqlite:///'):
    sqlite_path = DATABASE_URL.removeprefix('sqlite:///')

    if sqlite_path in (':memory:', './:memory:'):
        sqlite_name = ':memory:'
    else:
        # Treat as a path relative to BASE_DIR when not absolute.
        # Examples:
        # - sqlite:///./db.sqlite3 -> BASE_DIR/db.sqlite3
        # - sqlite:////app/db.sqlite3 -> /app/db.sqlite3
        if sqlite_path.startswith('/'):
            sqlite_name = sqlite_path
        else:
            sqlite_name = str(BASE_DIR / sqlite_path.lstrip('./'))

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': sqlite_name,
        }
    }
elif DATABASE_URL:
    if environ is None:
        raise RuntimeError('DATABASE_URL está configurado pero falta django-environ')

    env = environ.Env()
    DATABASES = {
        'default': env.db('DATABASE_URL'),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'sib_bridge'),
            'USER': os.environ.get('POSTGRES_USER', 'sib_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'sib_password'),
            'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://frontend:3000",
]

CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_DEFAULT_QUEUE = os.environ.get('CELERY_TASK_DEFAULT_QUEUE', 'default')
CELERY_RESULT_EXPIRES = int(os.environ.get('CELERY_RESULT_EXPIRES', str(60 * 60 * 24)))  # 24h
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', '').strip().lower() in ('1', 'true', 'yes', 'on')
CELERY_TASK_EAGER_PROPAGATES = os.environ.get('CELERY_TASK_EAGER_PROPAGATES', 'true').strip().lower() in ('1', 'true', 'yes', 'on')

# Redis transport tuning (safe defaults)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'visibility_timeout': int(os.environ.get('CELERY_VISIBILITY_TIMEOUT', str(60 * 60))),
}

# SUDEBAN configuration (shared)
# Default points to the demo environment. Override via SUDEBAN_API_URL.
SUDEBAN_API_URL = os.environ.get('SUDEBAN_API_URL', 'https://transacciones-demo.sudeban.gob.ve/api/transmission')
SUDEBAN_USERNAME = os.environ.get('SUDEBAN_USERNAME')
SUDEBAN_PASSWORD = os.environ.get('SUDEBAN_PASSWORD')
SUDEBAN_WEBHOOK_URL = os.environ.get('SUDEBAN_WEBHOOK_URL')
# Optional module-specific webhooks (fallback to SUDEBAN_WEBHOOK_URL)
# API-01: Intervención Cambiaria
SUDEBAN_WEBHOOK_URL_API01 = os.environ.get('SUDEBAN_WEBHOOK_URL_API01', SUDEBAN_WEBHOOK_URL)
# API-02: Subasta Privada (solicitudes)
SUDEBAN_WEBHOOK_URL_API02 = os.environ.get('SUDEBAN_WEBHOOK_URL_API02', SUDEBAN_WEBHOOK_URL)
# API-03: Resultados Subasta
SUDEBAN_WEBHOOK_URL_API03 = os.environ.get('SUDEBAN_WEBHOOK_URL_API03', SUDEBAN_WEBHOOK_URL)
# API-04: Mesa de Cambio
SUDEBAN_WEBHOOK_URL_API04 = os.environ.get('SUDEBAN_WEBHOOK_URL_API04', SUDEBAN_WEBHOOK_URL)
SUDEBAN_ID_ENTIDAD_BANCARIA = os.environ.get('SUDEBAN_ID_ENTIDAD_BANCARIA')

# --- Security / SSL ---
# Django's development server does not terminate TLS. In production you should run
# behind a reverse proxy (nginx/ingress) that provides HTTPS and sets
# X-Forwarded-Proto=https.
DJANGO_FORCE_SSL = os.environ.get('DJANGO_FORCE_SSL', '').strip().lower() in ('1', 'true', 'yes', 'on')
SECURE_SSL_REDIRECT = DJANGO_FORCE_SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow internal service-to-service communication over HTTP.
# The frontend and internal services consume the internal API under /api/internal/*.
# When DJANGO_FORCE_SSL=true, Django would otherwise redirect HTTP->HTTPS and break
# calls to the backend container (which serves HTTP inside the docker network).
SECURE_REDIRECT_EXEMPT = [
    r'^/api/internal/',
    r'^api/internal/',
]

SESSION_COOKIE_SECURE = SECURE_SSL_REDIRECT
CSRF_COOKIE_SECURE = SECURE_SSL_REDIRECT
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'

# HSTS should only be enabled when HTTPS is actually in place.
SECURE_HSTS_SECONDS = 31536000 if SECURE_SSL_REDIRECT else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_SSL_REDIRECT
SECURE_HSTS_PRELOAD = SECURE_SSL_REDIRECT

# Require HTTPS for outbound SUDEBAN transmission URL (recommended).
SUDEBAN_REQUIRE_HTTPS = os.environ.get('SUDEBAN_REQUIRE_HTTPS', 'true').strip().lower() in ('1', 'true', 'yes', 'on')