'''Some basic tests to verify that the factories for cwt and recovery
objects are being produced properly.'''


from django.test import TestCase
from datetime import date

from fsis2.tests.factories import SpeciesFactory
from cwts.tests.factories import *


class TestCWTfactory(TestCase):
    '''verify that the default values for a cwt are being populated properly'''
    def setUp(self):
        self.spc = SpeciesFactory(species_code='081')
        self.cwt = CWTFactory(spc=self.spc)

    def test_cwt_factory(self):
        
        self.assertEqual(self.cwt.stocked, True)
        self.assertEqual(self.cwt.cwt, '631111')
        self.assertEqual(self.cwt.tag_cnt, 10000)
        self.assertEqual(self.cwt.tag_type, 6)
        self.assertEqual(self.cwt.cwt_mfr, 'NMT')
        self.assertEqual(self.cwt.spc.species_code, "081")
        self.assertEqual(self.cwt.strain, "BS")
        self.assertEqual(self.cwt.development_stage, "51")
        self.assertEqual(self.cwt.year_class, 2005)
        self.assertEqual(self.cwt.stock_year, 2006)
        self.assertEqual(self.cwt.plant_site, "Owen Sound")
        self.assertEqual(self.cwt.ltrz, 10)
        self.assertEqual(self.cwt.hatchery, "CWC")
        self.assertEqual(self.cwt.agency, "OMNR")
        self.assertEqual(self.cwt.clipa, 5)


class TestRecoveryfactory(TestCase):
    '''verify that the default values for a recovery are being populated
    properly'''
    def setUp(self):

        self.recovery = CWT_RecoveryFactory()

    def test_recovery_factory(self):

        self.assertEqual(self.recovery.cwt, '631111')
        self.assertEqual(self.recovery.recovery_source, "CF")
        self.assertEqual(self.recovery.recovery_year, 2006)
        self.assertEqual(self.recovery.recovery_date, date(2012, 11, 15))
        self.assertEqual(self.recovery.recovery_grid, "1234")
        self.assertEqual(self.recovery.composite_key,
                         "LHA_CF12_001-1000-01-081-00-1")
        self.assertEqual(self.recovery.flen, 500)
        self.assertEqual(self.recovery.age, 6)


