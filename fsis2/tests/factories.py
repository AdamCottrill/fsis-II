import factory
from datetime import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from fsis2.models import *


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    first_name = 'John'
    last_name = 'Doe'
    username = 'johndoe'
    email = 'johndoe@hotmail.com'    
    #admin = False
    password = 'Abcdef12'

    #from: http://www.rkblog.rk.edu.pl/w/p/using-factory-boy-django-application-tests/
    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class ReadmeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Readme
    date = datetime.now()
    initials = "hs" #Homer Simpson
    comment = "Database compiled with FSIS data downloaded on 08/20/2013."

        
class SpeciesFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Species
    pass

class StrainFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Strain
    pass

class LotFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Lot
    pass

class EventFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Event



