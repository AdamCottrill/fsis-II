# Django settings for main project.

import os
from django.core.exceptions import ImproperlyConfigured
import sys


def get_env_variable(var_name):
    """Get the environment variable or return exception (from page 39 of
    2-scoops"""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
DJ_PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_PROJECT_DIR)
WSGI_DIR = os.path.dirname(BASE_DIR)
REPO_DIR = os.path.dirname(WSGI_DIR)

sys.path.append(os.path.join(REPO_DIR, 'libs'))

DATA_DIR = BASE_DIR

PROJECT_ROOT =  os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..'))

#these are from Kennith Love's best practices
here = lambda * x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)
root = lambda * x: os.path.join(os.path.abspath(PROJECT_ROOT), *x)


SECRET_KEY = get_env_variable('SECRET_KEY')
DEBUG = True

ADMINS = (
    ('Adam Cottrill', 'racottrill@bmts.com'),
)
MANAGERS = ADMINS


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
# not supposed to use * in production, but nothing else seems to work:
#ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Detroit'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''
#MEDIA_ROOT = root("uploads/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
#MEDIA_URL = 'http://fsis2/uploads/'
MEDIA_URL = '/media/'

ADMIN_MEDIA_PREFIX = '/admin/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
#STATIC_ROOT = ''
#STATIC_ROOT = root("static_root/")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'


#STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip("/"))
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "staticfiles"),
    root('static'),
)
ALLOWED_HOSTS = ['*']
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

## Additional locations of static files
#STATICFILES_DIRS = (
#    # Put strings here, like "/home/html/static" or "C:/www/django/static".
#    # Always use forward slashes, even on Windows.
#    # Don't forget to use absolute paths, not relative paths
#    #os.path.join(PROJECT_ROOT, 'staticfiles'),
#    os.path.join(PROJECT_ROOT, 'static'),
#)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    #'main.middleware.LoginRequiredMiddleware',
]


ROOT_URLCONF = 'main.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'main.wsgi.application'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':[
            root('templates'),
            root('fsis2/templates'),
            root('simple_auth/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


LOGIN_REDIRECT_URL = "/"

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.gis',
)

THIRDPARTY_APPS = (
    'crispy_forms',
    'djgeojson',
    'leaflet',
    )

CRISPY_FAIL_SILENTLY = not DEBUG
CRISPY_TEMPLATE_PACK = 'bootstrap3'

MY_APPS =(
    'fsis2',
    'cwts',
    )

INSTALLED_APPS = DJANGO_APPS + THIRDPARTY_APPS + MY_APPS

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

POSTGIS_VERSION = (2, 1, 8)

LEAFLET_CONFIG = {
    #minx, miny, maxx,maxy
    #'SPATIAL_EXTENT': (-84.0, 43.0,-80.0, 47.0),
    'DEFAULT_CENTER': (45.0,-82.0),
    'DEFAULT_ZOOM': 7,
    #'MIN_ZOOM': 3,
    #'MAX_ZOOM': 18,
    'RESET_VIEW': True,

}
