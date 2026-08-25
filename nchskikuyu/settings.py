"""
Django settings for nchskikuyu project.
"""

import os
from pathlib import Path

# Provide minimal drop-in replacements for python-decouple's config and Csv so a .env file is not required.
# These read from environment variables and return sensible defaults where needed.
def Csv():
    return 'csv'

def config(key, default=None, cast=None):
    # Prefer environment variable; fall back to provided default, then apply cast.
    raw = os.environ.get(key)
    if raw is None:
        val = default
    else:
        val = raw

    # Boolean cast
    if cast == bool:
        return str(val).lower() in ('1', 'true', 'yes', 'on')

    # Integer cast
    if cast == int:
        try:
            return int(val)
        except Exception:
            return default

    # CSV cast: support passing cast=Csv() which returns 'csv' or the literal string 'csv'
    cast_is_csv = (cast == 'csv') or (callable(cast) and cast() == 'csv')
    if cast_is_csv:
        if isinstance(val, (list, tuple)):
            return list(val)
        if not val:
            return []
        return [p.strip() for p in str(val).split(',') if p.strip()]

    return val

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Embedded from .env so the project can run without a .env file.
SECRET_KEY = config('SECRET_KEY', default='your-real-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# If running Django's development server, enable DEBUG for local testing
if 'runserver' in os.sys.argv or os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
    DEBUG = True

# If you need to enable DEBUG locally override with environment variable DEBUG=1
# (kept explicit to avoid accidental developer_override in production)

# Normalize ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS to avoid [''] when empty
_raw_allowed = config('ALLOWED_HOSTS', default='139.162.161.28,kikuyu-campus-website.onrender.com,.onrender.com,kikuyu.nakurucollegeofhealth.ac.ke,127.0.0.1,localhost', cast=str)
if _raw_allowed:
    ALLOWED_HOSTS = [h.strip() for h in _raw_allowed.split(',') if h.strip()]
else:
    ALLOWED_HOSTS = []

# Always allow local hosts for development convenience
for local_host in ('127.0.0.1', 'localhost'):
    if local_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(local_host)

# If DEBUG is enabled, allow all hosts to avoid DisallowedHost during local testing
if DEBUG:
    ALLOWED_HOSTS = ['*']

_raw_csrf = config('CSRF_TRUSTED_ORIGINS', default='https://kikuyu-campus-website.onrender.com,https://kikuyu.nakurucollegeofhealth.ac.ke,http://127.0.0.1:8000,http://localhost:8000', cast=str)
if _raw_csrf:
    CSRF_TRUSTED_ORIGINS = [u.strip() for u in _raw_csrf.split(',') if u.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []

# If running on Render, automatically add the external hostname if not present
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    # add https scheme for CSRF trusted origins
    origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

# Ensure the official production host is allowed
PRODUCTION_HOST = 'kikuyu.nakurucollegeofhealth.ac.ke'
if PRODUCTION_HOST not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(PRODUCTION_HOST)
# also add https variant to CSRF trusted origins
prod_origin = f"https://{PRODUCTION_HOST}"
if prod_origin not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append(prod_origin)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    
    # Local apps
    'core.apps.CoreConfig',
    'website.apps.WebsiteConfig',
    'dashboard.apps.DashboardConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nchskikuyu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'nchskikuyu.wsgi.application'
ASGI_APPLICATION = 'nchskikuyu.asgi.application'

# Database
# Default to SQLite for local/manage.py commands. Enable production DB (Postgres/MySQL) only by setting USE_PROD_DB=1 or DJANGO_PRODUCTION=1 in the environment.
USE_PROD_DB = os.environ.get('USE_PROD_DB') == '1' or os.environ.get('DJANGO_PRODUCTION') == '1'
if USE_PROD_DB:
    # DB engine and credentials embedded from previous .env values as defaults
    DB_ENGINE = config('DB_ENGINE', default='django.db.backends.postgresql')
    if 'postgres' in DB_ENGINE or 'postgresql' in DB_ENGINE:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': config('DB_NAME', default='School_DB'),
                'USER': config('DB_USER', default='postgres'),
                'PASSWORD': config('DB_PASSWORD', default='Chris6658'),
                'HOST': config('DB_HOST', default='localhost'),
                'PORT': config('DB_PORT', default='5432'),
            }
        }
    elif 'mysql' in DB_ENGINE:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': config('DB_NAME', default='nchsmcok_kikuyu'),
                'USER': config('DB_USER', default='nchsmcok_kikuyu'),
                'PASSWORD': config('DB_PASSWORD', default='Nchsm@Kikuyu2025'),
                'HOST': config('DB_HOST', default='localhost'),
                'PORT': config('DB_PORT', default='3306'),
                'OPTIONS': {
                    'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
                }
            }
        }
    else:
        # Unknown/unsupported engine: fall back to sqlite with a clear name
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Ensure the staticfiles directory exists to avoid runtime warnings and allow collectstatic to work
try:
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000', cast=Csv())

# Email Configuration
# Read SMTP settings; use SMTP backend only when credentials are provided, otherwise fall back to console backend for safe local testing.
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)

# Credentials (empty by default)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='nchsmnairobicampus@gmail.com')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='khzy yuqe ohsd rpkq')

# Choose backend: SMTP only when both user and password are provided
if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Helpful defaults
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'webmaster@localhost'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)

# Security Settings
# Only force HTTPS and secure cookies when the site is running in production (DEBUG=False).
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    # Disable these during local development to avoid HTTPS redirects and cookie issues
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=False, cast=bool)
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# WhiteNoise Static Files
if not DEBUG:
    # Use CompressedStaticFilesStorage (non-manifest) in production to avoid Manifest errors
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # during development use default storage so collectstatic isn't required
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Logging
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
