'''
=============================================================
c:/1work/Python/djcode/fsis2/cwts/tests/test_models.py
Created: 09 Oct 2015 13:30:16


DESCRIPTION:

tests of model methods in cwt application.

A. Cottrill
=============================================================
'''

from django.contrib.gis.geos import Point

from cwts.models import CWT

from cwts.tests.factories import *
from fsis2.tests.factories import SpeciesFactory

import pytest

from datetime import datetime


@pytest.mark.django_db
def test_cwt_age_at_capture():
    """The age at capture method of the cwt model object should return a
    list of tuples resprenting the age that the fish would be for each
    year since its release.

    """
    cwt = CWTFactory(year_class=2000)

    aac = cwt.age_at_capture()

    this_year = datetime.today().year
    yrs = range(2000,this_year + 1)
    ages = range(len(yrs))
    should_be = zip(ages,yrs)

    for age_year in aac:
        assert age_year in should_be



@pytest.mark.django_db
def test_cwt_age_at_capture_is_None():
    '''age at capture should be none if the year class is empty or occurs
    in the future.'''

    #year classes that are empty should be return none
    cwt = CWTFactory(year_class=None)
    assert cwt.age_at_capture() is None

    #year classes in the future should be None too
    cwt = CWTFactory(year_class=2201)
    assert cwt.age_at_capture() is None



@pytest.mark.django_db
def test_cwt_get_popup_text():
    '''get_popup_text() should return basic information about the cwt
       + including:
       + stocking agency,
       + species
       + strain,
       + year_class
       + development_stage
       + plant_site
       + clip code '''

    species = SpeciesFactory(common_name='Rainbow Trout',
                             scientific_name='O. mykiss')

    cwt_number = 654321

    cwt = CWTFactory(
        cwt = cwt_number,
        tag_cnt = 10000,
        tag_type = 6,
        cwt_mfr = 'NMT',
        spc = species,
        strain = "BS",
        development_stage = "51",
        year_class = 2005,
        stock_year = 2006,
        plant_site = "Thunder Beach",
        ltrz = 8,
        hatchery = "CWC",
        agency = "OMNR",
        clipa = 5,
    )

    popup_text = cwt.get_popup_text()

    assert species.common_name in popup_text
    assert species.scientific_name in popup_text

    assert '65-43-21' in popup_text
    assert '{:,}'.format(cwt.tag_cnt) in popup_text
    assert cwt.get_tag_type_display() in popup_text
    assert cwt.get_cwt_mfr_display() in popup_text
    assert cwt.get_strain_display() in popup_text
    assert cwt.strain in popup_text
    assert cwt.get_development_stage_display() in popup_text
    assert str(cwt.year_class) in popup_text
    assert str(cwt.stock_year) in popup_text
    assert cwt.plant_site in popup_text
    assert cwt.hatchery in popup_text
    assert cwt.agency in popup_text
    assert str(cwt.clipa) in popup_text

    assert "Sequence Range:" not in popup_text



@pytest.mark.django_db
def test_cwt_get_popup_text_sequential_cwt():
    '''If the cwt is a serquential type, it should include the range in
    the popup text.'''

    start = 1000
    end = 1234

    cwt = CWTFactory(tag_type=17, seq_start=start, seq_end=end)

    popup_text = cwt.get_popup_text()

    assert "Sequence Range:" in popup_text
    assert '{} - {}'.format(start, end) in popup_text



@pytest.mark.django_db
def test_cwt_unicode():
    '''verify that the string method of the cwt objects returns as
    expected - dashes bentween the second and third and fourth and fifth
    digits.'''

    cwt = CWTFactory(cwt=654321)
    assert str(cwt) == '65-43-21'



@pytest.mark.django_db
def test_cwtrecovery_get_popup_text():
    '''get_popup_text() should return basic information about the cwt_recovery
    including:
        + cwt number
        + composite key
        + recovery source
        + fork length
        + age

    '''

    cwt_number = 631111
    cwt = CWT_RecoveryFactory(
        cwt = cwt_number,
        recovery_source = "CF",
        recovery_year = 2006,
        recovery_date = date(2012, 11, 15),
        recovery_grid = "1234",
        composite_key = "LHA_CF12_001-1000-01-081-00-1",
        flen = 500,
        age = 9,
    )

    popup_text = cwt.get_popup_text()

    assert str(cwt_number) in popup_text
    assert cwt.get_recovery_source_display() in popup_text
    assert cwt.recovery_date.strftime('%b. %d, %Y') in popup_text
    assert cwt.composite_key in popup_text
    assert str(cwt.flen) in popup_text
    assert str(cwt.age) in popup_text



@pytest.mark.django_db
def test_cwtrecovery_get_popup_text_no_date():
    '''If a recovery date is not available, use the recovery year in
    get_popup_text() instead.

    '''
    cwt_number = 631111
    cwt = CWT_RecoveryFactory(
        recovery_year = 2006,
        recovery_date = None,
    )

    popup_text = cwt.get_popup_text()
    assert "2006" in popup_text


@pytest.mark.django_db
def test_cwtrecovery_unicode():
    '''the string representation of a cwt recovery should be it's composite key.
    '''
    key = "LHA_CF12_001-1000-01-081-00-1"
    cwt = CWT_RecoveryFactory(
        composite_key = key,
    )

    assert str(cwt) in key



@pytest.mark.django_db
def test_cwtrecovery_save():
    '''The popup_text field will be empty for a new cwt_recovery.  It is
    only created after the recovery object is saved.

    '''

    species = SpeciesFactory()

    recovery = CWT_recovery(
        cwt = '631111',
        spc = species,
        recovery_source = "CF",
        recovery_year = 2006,
        recovery_date = date(2012, 11, 15),
        recovery_grid = "1234",
        composite_key = "LHA_CF12_001-1000-01-081-00-1",
        flen = 500,
        age = 6,
        geom = Point(-82.00, 45.00)
    )

    assert str(recovery.popup_text) is ''
    recovery.save()
    assert str(recovery.popup_text) is not ''



@pytest.mark.django_db
def test_cwt_save():
    '''The popup_text field will be empty for a new cwt.  It is
    only created after the cwt object is saved.
    '''

    species = SpeciesFactory()
    cwt = CWT(
        cwt = 654321,
        tag_cnt = 10000,
        tag_type = 6,
        cwt_mfr = 'NMT',
        spc = species,
        strain = "BS",
        development_stage = "51",
        year_class = 2005,
        stock_year = 2006,
        plant_site = "Thunder Beach",
        ltrz = 8,
        hatchery = "CWC",
        agency = "OMNR",
        clipa = 5,)

    assert str(cwt.popup_text) is ''
    cwt.save()
    assert str(cwt.popup_text) is not ''
