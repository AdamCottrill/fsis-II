import unittest

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase
from django.conf import settings

from datetime import date

from fsis2.tests.factories import *
from cwts.tests.factories import CWT_RecoveryFactory, CWTFactory


class TestCWTDetailViews(TestCase):
    
    def setUp(self):
        self.cwt = CWTFactory(cwt='123456')
        
    def test_handle_cwt_without_events(self):
        '''If we try to access a cwt that does not have any stocking events
        associated with it, we should handle that gracefully.'''
        
        response = self.client.get(reverse('cwt_detail',
                                           kwargs={'cwt_number':
                                                   self.cwt.cwt}))
        self.assertEqual(response.status_code, 200)

        #print "response = %s" % response

        cwt = self.cwt.cwt
        cwt_number = "-".join([cwt[:2], cwt[2:4], cwt[4:]])
        self.assertContains(response, cwt_number)

        #self.assertContains(response, int(self.cwt.year_class), html=True)
        #self.assertContains(response, int(self.cwt.stock_year), html=True)
        #self.assertContains(response, self.cwt.strain, html=True)
        #self.assertContains(response, self.cwt.get_strain_display(), html=True)
        self.assertIn(self.cwt.get_strain_display(), response)
        self.assertContains(response, self.cwt.get_devlopment_stage_display())

        self.assertContains(response, self.cwt.tag_cnt, html=True)
        self.assertContains(response, self.cwt.clipa)
        self.assertContains(response, self.cwt.plant_site)

        self.assertContains(response, self.cwt.ltrz, html=True)
        self.assertContains(response, self.cwt.get_ltrz_display(), html=True)

        self.assertContains(response, self.cwt.agency)
        self.assertContains(response, self.cwt.hatchery)



        self.fail("Finish this test")



class TestLotList(TestCase):
    
    def setUp(self):
        self.lot1 = LotFactory(spawn_year=2010, fs_lot = '9999')
        self.lot2 = LotFactory(spawn_year=2009)
        self.lot3 = LotFactory(spawn_year=2008)
        self.lot4 = LotFactory(spawn_year=2005)

        
    def test_lot_list(self):
        pass


    def test_lot_list_query(self):
        pass


    def test_lot_query_non_existant(self):
        pass



class TestEventList(TestCase):
    
    def setUp(self):
        
        self.event1 = EventFactory(event_date=date(2012,4,1), fs_event = '9999')
        self.event2 = EventFactory(event_date=date(2012,6,1))
        self.event3 = EventFactory(event_date=date(2012,8,1))
        self.event4 = EventFactory(event_date=date(2012,10,1))

    def test_event_list(self):
        pass


    def test_event_list_query(self):
        pass


    def test_event_query_non_existant(self):
        pass

class TestSiteList(TestCase):
    
    def setUp(self):
        
        self.site1 = StockingSiteFactory(site_name='Owen Sound')
        self.site2 = StockingSiteFactory(site_name='Point Clark')
        self.site3 = StockingSiteFactory(site_name='Mary Ward Shoal')
        self.site4 = StockingSiteFactory(site_name='St. Mary')

    def test_site_list(self):
        pass


    def test_site_list_query_partial_match(self):
        pass

    def test_site_list_query_exact_match(self):
        pass

    def test_site_query_non_existant(self):
        pass


class TestCwtList(TestCase):
    
    def setUp(self):
        
        self.cwt1 = CWTFactory(cwt='631000')
        self.cwt2 = CWTFactory(cwt='632000')
        self.cwt3 = CWTFactory(cwt='635555')
        self.cwt4 = CWTFactory(cwt='632222')

    def test_cwt_list(self):
        pass

    def test_cwt_list_query_partial_match(self):
        pass

    def test_cwt_list_query_exact_match(self):
        pass

    def test_cwt_query_non_existant(self):
        pass



