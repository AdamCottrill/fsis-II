import unittest

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase
from django.conf import settings


from fsis2.tests.factories import *
from cwts.tests.factories import CWT_RecoveryFactory, CWTFactory


class CanViewEventList(TestCase):
    '''verify that we can view the complete event list and that it
    contains all of the current snippets.'''

    def setUp(self):
        pass
    
    def test_SnippetList(self):
        '''load the envent list'''
        pass

    def tearDown(self):
        pass


class TestCWTDetailViews(TestCase):
    
    def setUp(self):
        self.cwt = CWTFactory(cwt='123456')
        
    def test_handle_cwt_without_events(self):
        '''If we try to access a cwt that does not have any stocking events
        associated with it, we should handle that gracefully.'''
        
        response = self.client.get(reverse('cwt_detail',
                                           kwargs={'cwt_number': self.cwt.cwt}))
        self.assertEqual(response.status_code, 200)










