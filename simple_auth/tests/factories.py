import factory
#from datetime import datetime
from django.contrib.auth.models import User

#from ..models import *


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

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
