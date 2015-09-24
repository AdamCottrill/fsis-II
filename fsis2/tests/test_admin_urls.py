'''Some simple tests to quickly verify that all of the urls work and
that the admin contains interfaces to the models taht we need.'''

from django.core.urlresolvers import reverse
from fsis2.tests import DemoTestCase
from fsis2.tests.factories import *


class TestUrls(DemoTestCase):

    def setUp(self):
        pass

        
    def test_urls(self):
        '''Verify that all of the pages exist.  Can\'t use template_used
        because all views require login.  They are re-directed to the
        login'''
        URLS = (

            (reverse('login'),
             {'status_code':200}),
            
            (reverse('logout'),
             {'status_code':302}),

        )
        #self._test_urls(URLS)


    def tearDown(self):
        pass


class TestAdmin(DemoTestCase):
  
    def test_admin(self):
        self.create_user('super', super=True)
        self.login('super')
        self._test_admin((Lot, Event, Proponent, Species))

