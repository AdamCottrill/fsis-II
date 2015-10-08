import factory
from datetime import datetime
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.contrib.gis.geos import GEOSGeometry

from fsis2.models import *


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
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


class BuildDateFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BuildDate
    build_date = datetime.now()


class ReadmeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Readme
    date = datetime.now()
    initials = "hs" #Homer Simpson
    comment = "Database compiled with FSIS data downloaded on 08/20/2013."


class LakeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Lake
    lake = "Lake Huron"


class SpeciesFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Species
    #species_code = '81'
    species_code = factory.Sequence(lambda n: n)
    common_name = 'Lake Trout'
    scientific_name = 'Salvelinus nameychush'


class StrainFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Strain

    species = factory.SubFactory(SpeciesFactory)
    sto_code = "SNCW"
    strain_code = "SN"
    strain_name = "Seneca"


class ProponentFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Proponent

    abbrev = factory.Sequence(lambda n: "MH-{0:02d}".format(n))
    proponent_name = 'My Hatchery'


class StockingSiteFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StockingSite

    fsis_site_id = factory.Sequence(lambda n: "12{0:02d}".format(n))
    site_name = 'Honey Hole'
    stkwby = 'Lake Huron'
    stkwby_lid = 'what is this'
    utm = '123456'
    grid = '2456'
    dd_lat = 45.25
    dd_lon = -81.50
    basin = 'Main Basin'
    deswby_lid = '12345'
    deswby = 'Lake Huron'
    #geom = GEOSGeometry('POINT(-81.50 45.25)')


class LotFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Lot
    pass

    fs_lot = factory.Sequence(lambda n: "1{0:03d}".format(n))
    species = factory.SubFactory(SpeciesFactory)
    strain = factory.SubFactory(StrainFactory)
    spawn_year = 2010
    rearloc = 'My Place'
    rearloc_nm = 'My Backyard'
    proponent = factory.SubFactory(ProponentFactory)
    proponent_type = 'OMNR'


class EventFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Event

    lot = factory.SubFactory(LotFactory)
    prj_cd = 'LHA_FS11_111'
    fs_event = factory.Sequence(lambda n: "1{0:02d}".format(n))
    lotsam = '789'
    event_date = datetime.now()
    clipa = 5
    fish_age = 12
    stkcnt = 9999
    fish_wt = 125
    record_biomass_calc = 12345.2
    reartem = 7.8
    sitem = 4.5
    transit_mortality_count = 10
    site = factory.SubFactory(StockingSiteFactory)
    dd_lat = 45.25
    dd_lon = -81.5
    #geom = GEOSGeometry('POINT(-81.50 45.25)')
    development_stage = 51
    transit = 'TUG'
    stocking_method = 'SURFACE'
    stocking_purpose = 'UNKN'

    @factory.lazy_attribute
    def year(a):
        year = a.event_date.year
        return(year)



class TaggingEventFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TaggingEvent

    stocking_event = factory.SubFactory(EventFactory)
    fs_tagging_event_id = factory.Sequence(lambda n: "1{0:02d}".format(n))
    retention_rate_pct = 90
    retention_rate_sample_size = 100
    retention_rate_pop_size = 100
    comments = 'this is a fake tagging event'


class CWTsAppliedFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CWTs_Applied

    tagging_event = factory.SubFactory(TaggingEventFactory)
    fs_tagging_event_id =  factory.Sequence(lambda n: "1{0:02d}".format(n))
    cwt = factory.Sequence(lambda n: '63-01-{0:02d}'.format(n))


class ManagementUnitFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ManagementUnit


    label = '10'
    lake = factory.SubFactory(LakeFactory)
    mu_type = 'ltrz'

    #grid 2030
    geom = GEOSGeometry(
        "MULTIPOLYGON(((-81.6666641580675 44.6666679086515,"
                       "-81.7500000331451 44.6666679086515,"
                       "-81.7500000331451 44.7499999712291,"
                       "-81.6666641580675 44.7499999712292,"
                       "-81.6666641580675 44.6666679086515)))")
