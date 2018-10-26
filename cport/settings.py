"""
Django settings for cport project.

Generated by 'django-admin startproject' using Django 1.11.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

DATETIME_FORMAT = '%d-%m-%Y %H:%M:S'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1)okaxma)q9&7&ug_o0kshex%tto=zubp2r8tq^m803y#0)7$+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = 'DEPLOY' not in os.environ or int(os.environ['DEPLOY']) == 0

ALLOWED_HOSTS = ['*']

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
#CELERY_IGNORE_RESULT = False
CELERY_IMPORTS = (
    'command.lib.tasks.experiment_public',
    'command.lib.tasks.experiment_local',
    'command.lib.tasks.uncompress_file',
    'command.lib.tasks.run_file_assignment_script',
    'command.lib.tasks.run_parsing_script',
    'command.lib.tasks.parse_bio_feature_file',
    'command.lib.tasks.run_platform_mapper',
    'command.lib.tasks.import_experiment',
    'command.lib.tasks.import_platform_mapping',
    'command.lib.tasks.export_data',
    'command.lib.tasks.ontology',
)

#: Only add pickle to this list if your broker is secured
#: from unwanted access (see userguide/security.html)
CELERY_RESULT_BACKEND = 'django-db'

CELERY_BROKER_URL = 'amqp://guest:guest@' + os.environ['RABBITMQ_HOST'] + ':5672/'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.environ['REDIS_HOST'], 6379)],
        },
        "ROUTING": "cport.routing.channel_routing",
    }
}


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'command.apps.CommandConfig',
    'django_celery_results',
    'channels'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.gzip.GZipMiddleware'
]

ROOT_URLCONF = 'cport.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'cport.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASS'],
        'HOST': os.environ['DB_SERVICE'],
        'PORT': os.environ['DB_PORT']
    }
}

DATABASE_ROUTERS = ['command.routers.DatabaseRouter']

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

JUPYTER_TOKEN = os.environ['JUPYTER_TOKEN']
