import unittest

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase
from django.conf import settings

from datetime import date

from fsis2.tests.factories import *
from cwts.tests.factories import CWT_RecoveryFactory, CWTFactory



class CWTDetailView(TestCase):
    '''Normal cwt detail - omnr tag with some stocking events and some
    recoveries.'''
    def setUp(self):
        pass
    
    def test_first_test(self):
        pass



class TestCWTDetailViewWithoutRecoveriesOrStocking(TestCase):
    '''A tag that appears in our cwt inventory but does not have any
    stocking evnnts.  This situation occured several times during the mid
    1980s to mid 1990s - the stocking events need to be added to our
    database, but until they are, handle the problem gracefully and issue
    an appropriate warning.

    '''
    def setUp(self):
        self.cwt = CWTFactory(cwt='123456')
        
    def test_handle_cwt_without_events(self):
        '''If we try to access a cwt that does not have any stocking
        events associated with it, we should handle that gracefully
        and issue an appropriate warning.'''
        
        response = self.client.get(reverse('cwt_detail',
                                           kwargs={'cwt_number':
                                                   self.cwt.cwt}))
        self.assertEqual(response.status_code, 200)

        print "response = %s" % response
        #print "response.context = %s" % response.context

        self.assertEqual(response.context['cwt'], self.cwt)
        self.assertItemsEqual(response.context['event_list'], [])
        self.assertItemsEqual(response.context['recovery_list'], [])

        cwt = self.cwt.cwt
        cwt_number = "-".join([cwt[:2], cwt[2:4], cwt[4:]])
        self.assertContains(response, cwt_number)

        self.assertContains(response, str(self.cwt.year_class))
        self.assertContains(response, str(self.cwt.stock_year))
        self.assertContains(response, str(self.cwt.strain))
        self.assertContains(response, str(self.cwt.get_strain_display()))

        self.assertContains(response, "{:,}".format(self.cwt.tag_cnt))
        self.assertContains(response, str(self.cwt.clipa))
        self.assertContains(response, str(self.cwt.plant_site))

        shouldbe = "{0} ({1})".format(self.cwt.get_ltrz_display(),
                                      self.cwt.ltrz)
        self.assertContains(response, shouldbe)

        self.assertContains(response, str(self.cwt.agency))
        self.assertContains(response, str(self.cwt.hatchery))

        #this is an ontario tag so the messaage should be an alert
        msg = '<div class="alert alert-danger">'
        self.assertContains(response, msg)

        msg = "There are no Ontario stocking events associated with cwt {0}."
        msg = msg.format(cwt_number)
        self.assertContains(response, msg)

        msg = "According to the Agency code there should be."
        self.assertContains(response, msg)

        msg = "This cwt has not been recovered (yet)"
        self.assertContains(response, msg)




class CWTDetailViewNotRecovered(TestCase):
    '''Normal cwt detail - omnr tag with some stocking events but without
    recoveries.'''
    def setUp(self):
        pass
    
    def test_first_test(self):
        pass

class CWTDetailViewUSTagNotRecovered(TestCase):
    '''Normal cwt detail - US tag without recoveries and without stocking
    events.'''
    def setUp(self):
        pass
    
    def test_first_test(self):
        pass


class CWTDetailViewUSTagWithRecoveries(TestCase):
    '''Normal cwt detail - US tag with recoveries and without stocking
    events.'''
    def setUp(self):
        pass
    
    def test_first_test(self):
        pass
        
