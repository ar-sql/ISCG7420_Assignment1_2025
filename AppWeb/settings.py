import os
from pathlib import Path

# ─── BASE ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key')
DEBUG      = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# ─── INSTALLED APPS ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reservations',
]

# ─── MIDDLEWARE ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ─── URL CONFIG ───────────────────────────────────────────────────────────────
ROOT_URLCONF = 'AppWeb.urls'

# ─── TEMPLATES ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
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

# ─── WSGI ─────────────────────────────────────────────────────────────────────
WSGI_APPLICATION = 'AppWeb.wsgi.application'

# ─── DATABASE ─────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':   BASE_DIR / 'db.sqlite3',
    }
}

# ─── AUTH PASSWORD VALIDATORS ─────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── INTERNATIONALISATION ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'UTC'
USE_I18N      = True
USE_TZ        = True

# ─── STATIC FILES ──────────────────────────────────────────────────────────────
STATIC_URL         = '/static/'
STATIC_ROOT        = BASE_DIR / 'staticfiles'
STATICFILES_DIRS   = [ BASE_DIR / 'static' ]
WHITENOISE_USE_FINDERS = True

# ─── AUTH REDIRECTS ────────────────────────────────────────────────────────────
LOGIN_REDIRECT_URL  = 'room_list'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL           = 'login'

# ─── EMAIL CONFIGURATION ──────────────────────────────────────────────────────
# During development – write emails to files under sent_emails/
EMAIL_BACKEND   = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'



# In production, you might instead use SMTP:
# EMAIL_BACKEND      = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST         = os.environ.get('EMAIL_HOST', 'smtp.example.com')
# EMAIL_PORT         = int(os.environ.get('EMAIL_PORT', 587))
# EMAIL_HOST_USER    = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD= os.environ.get('EMAIL_HOST_PASSWORD', '')
# EMAIL_USE_TLS      = True
# DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'no-reply@example.com')
