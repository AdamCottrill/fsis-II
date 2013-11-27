import factory
from datetime import date
from django.contrib.gis.geos import Point

from fsis2.tests.factories import SpeciesFactory

from cwts.models import *


class CWTFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CWT

    stocked = True
    cwt = factory.Sequence(lambda n: '6311{0:02d}'.format(n))
    tag_cnt = 10000
    tag_type = 6
    cwt_mfr = 'NMT'
    spc = factory.SubFactory(SpeciesFactory)
    strain = "BS"
    development_stage = "51"
    year_class = 2005
    stock_year = 2006
    plant_site = "Owen Sound"
    ltrz = 10
    hatchery = "CWC"
    agency = "OMNR"
    clipa = 5


class CWT_RecoveryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CWT_recovery

    cwt = '631111'
    recovery_source = "CF"
    recovery_year = 2006
    recovery_date = date(2012, 11, 15)
    recovery_grid = "1234"
    composite_key = "LHA_CF12_001-1000-01-081-00-1"
    flen = 500
    age = 6
    geom = Point(-82.00, 45.00)
