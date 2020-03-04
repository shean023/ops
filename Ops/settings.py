"""
Django settings for Ops project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e02$n$tpsi&rvjj7=5y!pi7b2$ku-+@5+6%#va7=oypuglxkn#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

ASGI_APPLICATION = "Ops.routing.application"

# channel配置
CHANNEL_LAYERS = {
    "default": {
        # This example app uses the Redis channel layer implementation channels_redis
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [('192.168.238.129', 6379)],
        },
    },
}

# celery配置
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']
CELERYD_MAX_TASKS_PER_CHILD = 40
CELERY_TRACK_STARTED = True

CELERY_ROUTES = {
    'users.tasks.*': {'queue': 'default', 'routing_key': 'default'},
    'assets.tasks.*': {'queue': 'default', 'routing_key': 'default'},
    'task.tasks.*': {'queue': 'ansible', 'routing_key': 'ansible'},
    'fort.tasks.*': {'queue': 'fort', 'routing_key': 'fort'},
    'commons.tasks.*': {'queue': 'commons', 'routing_key': 'commons'},
}

# 执行ansible命令使用的redis信息
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 2
REDIS_PASSWORD = None

# mongodb配置信息
MONGODB_HOST = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_USER = 'root'
MONGODB_PASS = '123456'
RECORD_DB = 'test'
RECORD_COLL = 'ops'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_celery_beat',
    'django_celery_results',
    'api.apps.ApiConfig',
    'channels',
    'assets.apps.AssetsConfig',
    'users.apps.UsersConfig',
    'task.apps.TaskConfig',
    'fort.apps.FortConfig',
    'projs.apps.ProjsConfig',
    'plan.apps.PlanConfig',
    'wiki.apps.WikiConfig',
    'haystack.apps.HaystackConfig',
    'dbmanager.apps.DbmanagerConfig',
    'commons.apps.CommonsConfig',
    'confd.apps.ConfdConfig',
    'ticket.apps.TicketConfig',
]

# 全局搜索配置
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'wiki.whoosh_cn_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'wiki', 'whoosh_index'),
    }
}
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': '/var/tmp/django_cache',
#     }
# }
#
# CACHE_MIDDLEWARE_KEY_PREFIX = ''
# CACHE_MIDDLEWARE_SECONDS = 30
# CACHE_MIDDLEWARE_ALIAS = 'default'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middleware.UserLoginMiddleware',
    'utils.middleware.RecordMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}


ROOT_URLCONF = 'Ops.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Ops.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ops_ops',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1'
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 5,
    'MARGIN_PAGES_DISPLAYED': 2,
    'SHOW_FIRST_PAGE_WHEN_INVALID': True,
}

AUTH_USER_MODEL = 'users.UserProfile'

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

LOGIN_URL = '/login/'

TIME_FORMAT = '%Y-%m-%d %X'

# zabbix配置
ZABBIX_INFO = {
    'api_url': 'http://127.0.0.1/zabbix/api_jsonrpc.php',
    'graph_url': 'http://127.0.0.1/zabbix/chart2.php',
    'login_url': 'http://127.0.0.1/zabbix/index.php',
    'username': 'admin',
    'password': '123456'
}

# ANSIBLE_ROLE_PATH = os.path.join(MEDIA_ROOT, 'roles')
ANSIBLE_ROLE_PATH = '/usr/share/ansible/roles'

GUACD_HOST = '127.0.0.1'
GUACD_PORT = 4822

# email配置
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'XXXXXXXXXXXX'
EMAIL_HOST_PASSWORD = 'XXXXXXXXXXX'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 数据库管理用户,该用户需要有grant option权限,并且只能赋予该用户所拥有的权限
MYSQL_USER = 'root'
MYSQL_PASS = '123456'

GATEONE_API_KEY = 'ZDQxNDMzY2E2NTYyNDZjZmExOWI3OWI3OWM2YjU5ZWNjM'
GATEONE_API_SECRET = b'NGVlYzg2OTJmYjYyNGQ2Njg2YWMxMjY2MTU2NmU5ZDdkN'
GATEONE_SERVER_ADDR = 'http://192.168.238.128:10443'


GUACD_HOST = '192.168.100.16'
GUACD_PORT = '4822'
ADMIN_USERNAME = 'guacadmin'
ADMIN_PASSWORD = 'asf23#!ds'
GUACAMOLE_HOST = '192.168.100.16'
GUACAMOLE_PORT = 8080
GUACAMOLE_SERVER_PATH = 'guacamole'

ETCD_HOST = '127.0.0.1'
ETCD_PORT = '2379'
