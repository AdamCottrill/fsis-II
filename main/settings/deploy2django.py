from main.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': '142.143.160.56',
        'NAME': 'fsis2',
        'USER': 'adam',
        'PASSWORD': 'django',
    }

}

