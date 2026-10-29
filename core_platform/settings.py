import os
from pathlib import Path


# CORE PATH AND SECURITY CONFIGURATIONS
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-custom-mvp-platform-secret-key-cs360'

DEBUG = True

ALLOWED_HOSTS = []


# CORE MODULE REGISTRATION (INSTALLED APPS)
# =====================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',  # Corrected with .contrib package path
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your custom multi-tenant restaurant application module:
    'restaurant_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core_platform.urls'

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

WSGI_APPLICATION = 'core_platform.wsgi.application'


# LIVE POSTGRESQL DATABASE BACKEND CONFIGURATION
# =====================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'restaurant_saas',       # Maps to your custom PostgreSQL cluster database
        'USER': 'postgres',              # Your verified database master user
        'PASSWORD': 'password',          # The database access password we set
        'HOST': '127.0.0.1',             # Local loopback machine network point
        'PORT': '5432',                  # Standard Postgres port
    }
}


# SECURITY STRATEGIES, INTERNATIONALIZATION, AND FILES
# =====================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Brisbane'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =====================================================================
# EMAIL NOTIFICATIONS (Proposal deliverable 4)
# =====================================================================
# Console backend prints emails in the terminal instead of sending them.
# This is how the proposal's synthetic-data rule is met: no real emails go out.

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'bookings@restaurant-saas.test'


# =====================================================================
# LOGIN REDIRECTS (used when the staff dashboard is built)
# =====================================================================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'