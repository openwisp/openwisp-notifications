import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'openwisp_notfications.db')
    }
}

SECRET_KEY = 'fn)t*+$)ugeyip6-#txyy$5wf2ervc0d2n#h)qb)y5@ly$t*@w'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'openwisp_notifications.apps.OpenwispNotificationsConfig',
    # 'django.contrib.sites',
    
 


    # 'openwisp_utils.admin_theme',
    'django.contrib.admin',
    # 'django_filters',
    # 'django_extensions',
    # admin theme
    'openwisp_utils.admin_theme',
    'notifications',
    # 'rest_framework',
    'django.contrib.sites',
    'django_extensions',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'openwisp_users',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'openwisp_utils.staticfiles.DependencyFinder',
]

AUTH_USER_MODEL = 'openwisp_users.User'
SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TIME_ZONE = 'Europe/Rome'
LANGUAGE_CODE = 'en-gb'
USE_TZ = True
USE_I18N = False
USE_L10N = False
STATIC_URL = '/static/'
CORS_ORIGIN_ALLOW_ALL = True
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
EMAIL_PORT = '1025'


# during development only
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# change this to something secret in production
# DJANGO_FREERADIUS_API_TOKEN = 'djangofreeradiusapitoken'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'openwisp_utils.loaders.DependencyLoader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# LOGGING = {
#     'version': 1,
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         }
#     }
# }

# SOCIALACCOUNT_PROVIDERS = {
#     'facebook': {
#         'METHOD': 'oauth2',
#         'SCOPE': ['email', 'public_profile'],
#         'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
#         'INIT_PARAMS': {'cookie': True},
#         'FIELDS': [
#             'id',
#             'email',
#             'name',
#             'first_name',
#             'last_name',
#             'verified',
#         ],
#         'VERIFIED_EMAIL': True,
#     }
# }
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False



# local settings must be imported before test runner otherwise they'll be ignored
try:
    from local_settings import *
except ImportError:
    pass