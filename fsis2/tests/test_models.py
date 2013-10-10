from django.test import TestCase
from datetime import datetime

from fsis2.models import *
from fsis2.tests.factories import *


class TestLot(TestCase):
    '''verify that the unicode, get_url, and slug of Lot work as
       expected'''
    def setUp(self):
        pass

    def test_language_unicode(self):
        pass
            
    def tearDown(self):
        pass


class TestReadme(TestCase):
    '''verify that the get_download_date, functions works as
       expected'''
    def setUp(self):

        self.comment1 = "good date with slashes 08/20/2012."
        self.readme1 = ReadmeFactory(comment = self.comment1)

        self.comment2 = "good date with slashes 20-Aug-2012."        
        self.readme2 = ReadmeFactory(comment = self.comment2)

        self.comment3 = "Bad date with  20-20-2012."                
        self.readme3 = ReadmeFactory(comment = self.comment3)

        self.comment4 = "No date."
        self.readme4 = ReadmeFactory(comment = self.comment4)

        self.comment5 = ""
        self.readme5 = ReadmeFactory(comment = self.comment5)
        
    def test_download_date_unicode(self):

        '''Verify that the get download date method on readme objects
        can handle the two expected formats properly and if another
        format is encountered, that it returns none.

        '''
        
        shouldbe = datetime.strptime("08/20/2012","%m/%d/%Y")
        download_date = self.readme1.get_download_date()
        self.assertEqual(download_date,shouldbe)

        download_date = self.readme2.get_download_date()
        self.assertEqual(download_date,shouldbe)

        download_date = self.readme3.get_download_date()
        self.assertEqual(download_date,None)

        download_date = self.readme4.get_download_date()
        self.assertEqual(download_date,None)

        download_date = self.readme5.get_download_date()
        self.assertEqual(download_date,None)
        
        
    def tearDown(self):
        pass

        