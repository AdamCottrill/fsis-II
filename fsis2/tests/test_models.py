from django.test import TestCase
from datetime import datetime

from django.db import IntegrityError

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


class TestSpecies(TestCase):
    '''verify that the unicode of species works as expected'''
    def setUp(self):

        self.common_name = "Gold Fish"
        self.scientific_name = 'fishicus goldicus'

        self.spc1 = SpeciesFactory(common_name=self.common_name,
                                   scientific_name=self.scientific_name)

        self.spc2 = SpeciesFactory(common_name=self.common_name,
                                   scientific_name=None)

    def test_species_name_unicode(self):
        '''If there is a scientific name, the unicode method should return the
        common name followed by the scientific_name in brackets, if there is
        no scientific_name, just return the common name as is.'''

        shouldbe = "{0} ({1})".format(self.common_name, self.scientific_name)
        self.assertEqual(str(self.spc1), shouldbe)

        self.assertEqual(str(self.spc2), self.common_name)

    def tearDown(self):
        pass


class TestStrain(TestCase):
    '''verify that the unicode of strain works as expected'''
    def setUp(self):

        self.common_name = "Gold Fish"
        self.scientific_name = 'fishicus goldicus'

        self.strain_name = 'Homers choice'
        self.strain_code = 'HC'
        self.sto_code = 'wtf'

        self.spc = SpeciesFactory(common_name=self.common_name,
                                  scientific_name=self.scientific_name)

        self.strain = StrainFactory(species=self.spc, sto_code=self.sto_code,
                                    strain_name=self.strain_name,
                                    strain_code=self.strain_code)

    def test_strain_name_unicode(self):
        '''The unicode method for strain should be the strain name prefixed
        ahead of the species name.'''

        shouldbe = "{0} {1}".format( self.strain_name, self.common_name)
        self.assertEqual(str(self.strain), shouldbe)

    def tearDown(self):
        pass


class TestProponent(TestCase):
    '''verify that the unicode of proponent works as expected'''
    def setUp(self):

        self.abbrev = "HJS"
        self.proponent_name = "Homer J. Simpson"

        self.proponent = ProponentFactory(proponent_name=self.proponent_name,
                                        abbrev=self.abbrev)

    def test_proponent_name_unicode(self):
        '''The unicode method for proponent should be the propent name
        followed by their abbreviation in brackets.'''

        shouldbe = "{0} ({1})".format(self.proponent_name, self.abbrev)
        self.assertEqual(str(self.proponent), shouldbe)

    def tearDown(self):
        pass



class TestLot(TestCase):
    '''verify that the unicode, get_url, and slug of Lot work as
       expected'''
    def setUp(self):
        pass

    def test_language_unicode(self):
        pass

    def tearDown(self):
        pass


class TestManagementUnit(TestCase):
    """verify that the unicode, name, and get_slug methods of ManagementUnit returns a string of the correct format.  Additionally, verify that if a duplicate slug is created, an error is thown.
    """

    def setUp(self):
        self.lake = LakeFactory()

    def test_management_unit_slug(self):

        mu = ManagementUnit(mu_type='ltrz', lake=self.lake, label='8')
        shouldbe = "huron_ltrz_8"
        self.assertEqual(mu.get_slug(), shouldbe)

        mu = ManagementUnit(mu_type='ltrz', lake=self.lake, label='14')
        shouldbe = "huron_ltrz_14"
        self.assertEqual(mu.get_slug(), shouldbe)

        mu = ManagementUnit(mu_type='qma', lake=self.lake, label='4-1')
        shouldbe = "huron_qma_4-1"
        self.assertEqual(mu.get_slug(), shouldbe)

    def test_management_unit_unicode(self):

        mu = ManagementUnit(mu_type='ltrz', lake=self.lake, label='8')
        shouldbe = "Lake Huron LTRZ 8"
        self.assertEqual(str(mu), shouldbe)

        mu = ManagementUnit(mu_type='ltrz', lake=self.lake, label='14')
        shouldbe = "Lake Huron LTRZ 14"
        self.assertEqual(str(mu), shouldbe)

        mu = ManagementUnit(mu_type='qma', lake=self.lake, label='4-1')
        shouldbe = "Lake Huron QMA 4-1"
        self.assertEqual(str(mu), shouldbe)

    def test_management_unit_name(self):

        mu = ManagementUnit(mu_type='ltrz', lake=self.lake, label='8')
        shouldbe = "Lake Huron LTRZ 8"
        self.assertEqual(mu.name(), shouldbe)

        mu = ManagementUnit(mu_type='ltrz', lake=self.lake, label='14')
        shouldbe = "Lake Huron LTRZ 14"
        self.assertEqual(mu.name(), shouldbe)

        mu = ManagementUnit(mu_type='qma', lake=self.lake, label='4-1')
        shouldbe = "Lake Huron QMA 4-1"
        self.assertEqual(mu.name(), shouldbe)

    def test_duplicate_slug_throws_error(self):
        '''an error should be thrown if we try to create a management unit
        that already exists'''
        mu1 = ManagementUnitFactory(mu_type='ltrz', lake=self.lake, label='8')
        mu1.save()
        #mu2 = ManagementUnitFactory.create(mu_type='ltrz', lake=self.lake,
        #                                   label='8')
        #self.assertRaises(IntegrityError, mu2.save())

        with self.assertRaises(IntegrityError):
            mu2 = ManagementUnitFactory(mu_type='ltrz', lake=self.lake,
                                        label='8')

    def test_update_to_duplicate_slug_throws_error(self):
        '''an error should be thrown if we try to update a management unit
        to one already exists'''
        mu1 = ManagementUnitFactory(mu_type='ltrz', lake=self.lake, label='8')
        mu2 = ManagementUnitFactory(mu_type='ltrz', lake=self.lake,
                                        label='9')
        mu2.label = '8'
        with self.assertRaises(IntegrityError):
            mu2.save()
