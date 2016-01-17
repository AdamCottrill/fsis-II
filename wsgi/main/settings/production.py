from main.settings.base import *
from socket import gethostname

if ON_OPENSHIFT:

    ALLOWED_HOSTS = [
        gethostname(),
        os.environ.get('OPENSHIFT_APP_DNS'),
    ]

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'fsis2',
            'USER': os.getenv('OPENSHIFT_POSTGRESQL_DB_USERNAME'),
            'PASSWORD': os.getenv('OPENSHIFT_POSTGRESQL_DB_PASSWORD'),
            'HOST': os.environ.get('OPENSHIFT_POSTGRESQL_DB_HOST', '127.0.0.1'),
            'PORT': os.environ.get('OPENSHIFT_POSTGRESQL_DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'fsis2',
    ***REMOVED***
    ***REMOVED***
            'HOST': '',
            'PORT': '',
        }
    }
