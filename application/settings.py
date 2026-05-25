

from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_FILE = os.getenv('ENV_FILE', '.env.local')
load_dotenv(BASE_DIR / ENV_FILE)


def get_bool_env(name, default=False):
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in ('true', '1', 'yes', 'on')


def get_list_env(name, default=''):
    value = os.getenv(name, default)

    return [
        item.strip()
        for item in value.split(',')
        if item.strip()
    ]


SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key')

DEBUG = get_bool_env('DEBUG', True)

ALLOWED_HOSTS = get_list_env(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost'
)


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'questions',
    'core',
]

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
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

if DEBUG:
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE


ROOT_URLCONF = 'application.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'questions' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'questions.context_processors.sidebar_data',
            ],
        },
    },
]


WSGI_APPLICATION = 'application.wsgi.application'


DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite')

if DB_ENGINE == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'qa_db'),
            'USER': os.getenv('DB_USER', 'qa_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'qa_password'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('DB_NAME', 'db.sqlite3'),
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


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'static'


MEDIA_URL = 'media/'

MEDIA_ROOT = BASE_DIR / 'media'


INTERNAL_IPS = [
    '127.0.0.1',
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'