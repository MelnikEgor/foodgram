import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'no_secret_key')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(', ')

ROOT_HOST = 'fooodgram.hopto.org'

# DEBUG = os.getenv('DEBUG', True) is True

DEBUG = True

DJANGO_SUPERUSER_EMAIL = 'admin@lst.net'
DJANGO_SUPERUSER_USERNAME = 'admin'
DJANGO_SUPERUSER_FIRST_NAME = 'admin'
DJANGO_SUPERUSER_LAST_NAME = 'admin'
DJANGO_SUPERUSER_PASSWORD = 'admin'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',

    'api',
    'foods',
    'users',
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

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'


DEFAULT_DBMS = 'django.db.backends.sqlite3'
# DBMS_USING = os.getenv('DBMS_POSTGRES', DEFAULT_DBMS)
# if DBMS_USING == DEFAULT_DBMS:
#     DATABASES = {
#         'default': {
#             'ENGINE': DBMS_USING,
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }
#     }
# else:
#     DATABASES = {
#         'default': {
#             'ENGINE': DBMS_USING,
#             'NAME': os.getenv('POSTGRES_DB', 'django'),
#             'USER': os.getenv('POSTGRES_USER', 'django'),
#             'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
#             'HOST': os.getenv('DB_HOST', ''),
#             'PORT': os.getenv('DB_PORT', 5432)
#         }
#     }

DATABASES = {
    'default': {
        'ENGINE': DEFAULT_DBMS,
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CSRF_TRUSTED_ORIGINS = 'localhost'  # 'fooodgram.hopto.org'

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


LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.User'

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DJOSER = {
    'LOGIN_FIELD': 'email'
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'api.v1.pagination.CustomPagination',
    'PAGE_SIZE': 6,

    'SEARCH_PARAM': 'name'
}
