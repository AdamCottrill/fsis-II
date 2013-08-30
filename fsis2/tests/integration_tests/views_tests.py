import unittest

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test.client import Client
from django_webtest import WebTest
#from django.test import TestCase
from django.conf import settings

from .tests.factories import *

class CanViewEventList(WebTest):
    '''verify that we can view the complete event list and that it
    contains all of the current snippets.'''

    def setUp(self):
        pass
    
    def test_SnippetList(self):
        '''load the envent list'''
        pass

    def tearDown(self):
        pass
