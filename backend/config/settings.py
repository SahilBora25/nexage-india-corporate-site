import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')

DEBUG = env_bool('DJANGO_DEBUG', False)
SECRET_KEY = (os.getenv('DJANGO_SECRET_KEY') or '').strip()
_KNOWN_UNSAFE_SECRET_KEYS = {
    '',
    'local-development-only-change-before-deployment',
    'replace-with-a-long-random-secret',
    'change-me',
    'changeme',
}
_UNSAFE_SECRET_MARKERS = ('replace-', 'your-', 'change-me', 'changeme', 'local-development-only')
if DEBUG and not SECRET_KEY:
    # A fresh, process-local key keeps local setup simple without shipping a fixed default.
    import secrets
    SECRET_KEY = secrets.token_urlsafe(50)
elif not DEBUG and (
    SECRET_KEY.lower() in _KNOWN_UNSAFE_SECRET_KEYS
    or any(marker in SECRET_KEY.lower() for marker in _UNSAFE_SECRET_MARKERS)
    or len(SECRET_KEY) < 50
):
    raise RuntimeError('Set a unique, random DJANGO_SECRET_KEY of at least 50 characters before production startup.')

_raw_allowed_hosts = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,web,backend').strip()
ALLOWED_HOSTS = [h.strip() for h in _raw_allowed_hosts.split(',') if h.strip()]
if not DEBUG:
    if not os.getenv('DJANGO_ALLOWED_HOSTS', '').strip():
        raise RuntimeError('Set DJANGO_ALLOWED_HOSTS explicitly to the real production hostname(s).')
    if any('your-domain.example' in host.lower() or host.lower().endswith('.example') for host in ALLOWED_HOSTS):
        raise RuntimeError('Replace placeholder values in DJANGO_ALLOWED_HOSTS before production startup.')
    _development_hosts = {'localhost', '127.0.0.1', '::1', 'web', 'backend'}
    if not any(host.lower() not in _development_hosts for host in ALLOWED_HOSTS):
        raise RuntimeError('Include the real public hostname in DJANGO_ALLOWED_HOSTS before production startup.')

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions',
    'django.contrib.messages', 'django.contrib.staticfiles', 'corsheaders', 'rest_framework', 'core',
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
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': ['django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']},
}]
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

if os.getenv('DATABASE_URL'):
    # Keep PostgreSQL credentials in environment variables; do not place them in frontend code.
    import urllib.parse
    db = urllib.parse.urlparse(os.environ['DATABASE_URL'])
    db_password = urllib.parse.unquote(db.password or '')
    if db.scheme not in ('postgres', 'postgresql') or not db.hostname or not db.path.strip('/') or not db.username:
        raise RuntimeError('DATABASE_URL must be a valid PostgreSQL URL including database name, user, host, and password.')
    if not DEBUG and (
        len(db_password) < 16
        or any(marker in db_password.lower() for marker in ('replace-', 'your-', 'change-me', 'changeme', 'password'))
    ):
        raise RuntimeError('Set a unique PostgreSQL DATABASE_URL password of at least 16 characters before production startup.')
    DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': db.path.lstrip('/'), 'USER': urllib.parse.unquote(db.username), 'PASSWORD': db_password, 'HOST': db.hostname, 'PORT': db.port or 5432, 'CONN_MAX_AGE': 60, 'OPTIONS': {'sslmode': os.getenv('DB_SSLMODE', 'prefer')}}}
else:
    _db_password = os.getenv('POSTGRES_PASSWORD', 'replace-this-db-password')
    if not DEBUG and (
        len(_db_password) < 16
        or any(marker in _db_password.lower() for marker in ('replace-', 'your-', 'change-me', 'changeme', 'password'))
    ):
        raise RuntimeError('Set a unique POSTGRES_PASSWORD of at least 16 characters before production startup.')
    DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': os.getenv('POSTGRES_DB', 'nexage'), 'USER': os.getenv('POSTGRES_USER', 'nexage'), 'PASSWORD': _db_password, 'HOST': os.getenv('POSTGRES_HOST', 'localhost'), 'PORT': os.getenv('POSTGRES_PORT', '5432'), 'CONN_MAX_AGE': 60}}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = Path(os.getenv('PRIVATE_MEDIA_ROOT', BASE_DIR / 'private_media'))
# Uploaded project documents deliberately are not served using a public MEDIA_URL.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_URL = os.getenv('REDIS_URL', '')
if REDIS_URL:
    CACHES = {'default': {'BACKEND': 'django_redis.cache.RedisCache', 'LOCATION': REDIS_URL, 'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'}, 'KEY_PREFIX': 'nexage'}}
else:
    CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'nexage-local-cache'}}

CORS_ALLOWED_ORIGINS = [x.strip() for x in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173' if DEBUG else '').split(',') if x.strip()]
CORS_ALLOW_CREDENTIALS = True
_raw_csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173' if DEBUG else '').strip()
CSRF_TRUSTED_ORIGINS = [x.strip() for x in _raw_csrf_origins.split(',') if x.strip()]
if not DEBUG and (
    not CSRF_TRUSTED_ORIGINS
    or any(
        not origin.lower().startswith('https://')
        or 'your-domain.example' in origin.lower()
        or origin.lower().endswith('.example')
        for origin in CSRF_TRUSTED_ORIGINS
    )
):
    raise RuntimeError('Set CSRF_TRUSTED_ORIGINS to real HTTPS production origin(s) before production startup.')
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = env_bool('COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = env_bool('COOKIE_SECURE', not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', True)
    if not env_bool('COOKIE_SECURE', True):
        raise RuntimeError('Set COOKIE_SECURE=true before production startup.')
    if not SECURE_SSL_REDIRECT:
        raise RuntimeError('Set SECURE_SSL_REDIRECT=true before production startup; use the documented HTTPS proxy setup.')
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle', 'rest_framework.throttling.UserRateThrottle'],
    # Nginx overwrites X-Forwarded-For with the address it observed. The backend
    # therefore trusts exactly one proxy hop. If an ingress sits before Nginx,
    # configure its real client IP range at that edge; do not trust arbitrary XFF.
    'NUM_PROXIES': 1,
    'DEFAULT_THROTTLE_RATES': {'anon': os.getenv('API_ANON_RATE', '100/day'), 'user': '1200/hour', 'contact': '10/hour', 'quote': '10/hour', 'auth': '10/hour'},
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'] if not DEBUG else ['rest_framework.renderers.JSONRenderer', 'rest_framework.renderers.BrowsableAPIRenderer'],
}

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost' if DEBUG else '').strip()
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
EMAIL_USE_SSL = env_bool('EMAIL_USE_SSL', False)
EMAIL_TIMEOUT = int(os.getenv('EMAIL_TIMEOUT', '10'))
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost' if DEBUG else '').strip()
SALES_ENQUIRY_EMAIL = os.getenv('SALES_ENQUIRY_EMAIL', 'webmaster@localhost' if DEBUG else '').strip()
SEND_CUSTOMER_CONFIRMATION = env_bool('SEND_CUSTOMER_CONFIRMATION', False)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'enquiry_notifications_console': {
            'class': 'logging.StreamHandler',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'core.views': {
            'handlers': ['enquiry_notifications_console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise RuntimeError('Set only one of EMAIL_USE_TLS or EMAIL_USE_SSL to true.')
if bool(EMAIL_HOST_USER) != bool(EMAIL_HOST_PASSWORD):
    raise RuntimeError('Set both EMAIL_HOST_USER and EMAIL_HOST_PASSWORD, or leave both empty for an approved unauthenticated relay.')
if not DEBUG:
    if EMAIL_BACKEND != 'django.core.mail.backends.smtp.EmailBackend':
        raise RuntimeError('Use the SMTP email backend in production.')
    if not EMAIL_HOST or EMAIL_HOST.lower() in {'localhost', '127.0.0.1'} or EMAIL_HOST.lower().endswith('.example'):
        raise RuntimeError('Set EMAIL_HOST to the real SMTP host before production startup.')
    if not 1 <= EMAIL_PORT <= 65535:
        raise RuntimeError('Set EMAIL_PORT to a valid SMTP port.')
    for setting_name, email_address in (
        ('DEFAULT_FROM_EMAIL', DEFAULT_FROM_EMAIL),
        ('SALES_ENQUIRY_EMAIL', SALES_ENQUIRY_EMAIL),
    ):
        email_domain = email_address.rsplit('@', 1)[-1].lower() if '@' in email_address else ''
        if (
            not email_address
            or '@' not in email_address
            or email_address.lower().endswith('.example')
            or email_domain in {'example.com', 'example.org', 'example.net', 'example.invalid'}
            or 'your-' in email_address.lower()
            or 'replace-' in email_address.lower()
        ):
            raise RuntimeError(f'Set {setting_name} to a real approved email address before production startup.')

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100

# Named scopes are used by the public contact, quote and authentication endpoints.
REST_FRAMEWORK = globals().get('REST_FRAMEWORK', {})
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    **REST_FRAMEWORK.get('DEFAULT_THROTTLE_RATES', {}),
    'anon': os.getenv('API_ANON_RATE', '100/day'),
    'user': '1000/day',
    'contact': '5/hour',
    'quote': '3/hour',
    'auth': '10/hour',
}
