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
            'NAME': os.getenv('POSTGRES_DB', 'qa_db'),
            'USER': os.getenv('POSTGRES_USER', 'qa_user'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'qa_password'),
            'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
            'PORT': os.getenv('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv('POSTGRES_DB', 'db.sqlite3'),
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

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_CACHE_DB = os.getenv('REDIS_CACHE_DB', '1')
REDIS_BROKER_DB = os.getenv('REDIS_BROKER_DB', '2')
REDIS_BEAT_DB = os.getenv('REDIS_BEAT_DB', '3')


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CACHE_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': 60 * 10,
    }
}


CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BROKER_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}'

CELERY_BEAT_SCHEDULER = 'redbeat.RedBeatScheduler'
CELERY_REDBEAT_REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_BEAT_DB}'

CELERY_TASK_ALWAYS_EAGER = get_bool_env('CELERY_TASK_ALWAYS_EAGER', False)

CELERY_BEAT_SCHEDULE = {
    'update-popular-tags-cache': {
        'task': 'questions.tasks.update_popular_tags_cache',
        'schedule': 60 * 10,
    },
    'update-best-users-cache': {
        'task': 'questions.tasks.update_best_users_cache',
        'schedule': 60 * 10,
    },
}
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '1025'))
EMAIL_USE_TLS = get_bool_env('EMAIL_USE_TLS', False)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@kittens.local')

SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')

POPULAR_TAGS_CACHE_TIMEOUT = int(os.getenv('POPULAR_TAGS_CACHE_TIMEOUT', str(60 * 60)))
BEST_USERS_CACHE_TIMEOUT = int(os.getenv('BEST_USERS_CACHE_TIMEOUT', str(60 * 60)))