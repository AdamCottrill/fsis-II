'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/test_event_model.py
Created: 25 Sep 2015 11:11:18


DESCRIPTION:

The tests in this script verify that the methods and properties of the
event model work as expected.

A. Cottrill
=============================================================

'''






import pytest
from django.core.urlresolvers import reverse

from fsis2.models import Event
from fsis2.tests.factories import *

from datetime import datetime

@pytest.fixture(scope='class')
def db_setup():
    """For the tests in this file, we will need three different species,
    two different hatcheries, and several events.

    """

    strain = StrainFactory(strain_code='WRT') #wild rainbow trout
    rainbow = SpeciesFactory.create(common_name='Rainbow Trout',
                                    species_code='076')

    hatchery1 = ProponentFactory(abbrev='ABC',
                                 proponent_name='ABC Fishin Club')

    rainbow_lot = LotFactory(species=rainbow,
                             proponent=hatchery1,
                             strain=strain)

    site1 = StockingSiteFactory(site_name='Site1')

    stocking_date = datetime(2010,10,15)
    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(site=site1, lot=rainbow_lot,
                          prj_cd='LHA_FS03_001',
                          event_date=stocking_date,
                          stkcnt = 10000,
                          fs_event = 9988
                        )


    #no tags for event 2
    event2 = EventFactory(site=site1, lot=rainbow_lot,fs_event=1122,
                          prj_cd='LHA_FS98_001', )

    #need to add some tags here:
    tagging_event = TaggingEventFactory.create(stocking_event=event1)
    tags = ['631234','635555','639999']
    for tag in tags:
        CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=tag)



@pytest.mark.django_db
def test_spc_code_proptery(db_setup):
    """the spc_code property of a stocking event should return the species
    code of the stocked fish.

    """
    event = Event.objects.get(fs_event=9988)
    assert event.spc_code == 76


@pytest.mark.django_db
def test_hatchery_property(db_setup):
    """the hatchery property of a stocking event should return the abbreviation
    code for the hatchery/proponent who raised and stocked the fish.

    """
    event = Event.objects.get(fs_event=9988)
    assert event.hatchery_code == 'ABC'


@pytest.mark.django_db
def test_strain_property(db_setup):
    """the strain property of a stocking event should return the strain code
    for fish stocked in this event.

    """
    event = Event.objects.get(fs_event=9988)
    assert event.strain_code == 'WRT'


@pytest.mark.django_db
def test_get_popup_text(db_setup):
    """the get_popup_text() method of the stocking event is not intended
    to be called directly, but should contain all of the basic
    information about the stocking event in a html table.

    """
    event = Event.objects.get(fs_event=9988)
    popup_text = event.get_popup_text()

    #html table tags:
    assert '<table>' in popup_text
    assert '</table>' in popup_text

    assert 'Rainbow Trout' in popup_text
    assert 'ABC Fishin Club'

    assert 'Site1' in popup_text
    assert 'October 15 2010' in popup_text

    assert '10,000' in popup_text


@pytest.mark.django_db
def test_language_unicode(db_setup):
    '''The unicode method of a stocking event should be formated to
    include the fsis event number.'''

    event = Event.objects.get(fs_event=9988)
    assert str(event) == 'fsis event : 9988'


@pytest.mark.django_db
def test_get_cwts(db_setup):
    """the get cwts method of a stocking event should return all of the
    cwts associated with fish stocked in this event.

    """

    event = Event.objects.get(fs_event=9988)
    cwts = event.get_cwts()
    assert len(cwts) == 3
    should_be = ['631234','635555','639999']
    tag_ids = [x.cwt for x in cwts]
    for tag in tag_ids:
        assert tag in should_be


@pytest.mark.django_db
def test_get_cwts_no_tags(db_setup):
    """the get cwts method of a stocking event should return all of the
    cwts associated with fish stocked in this event.  If there
    were no tags associated with this event, it should return None

    """

    event = Event.objects.get(fs_event=1122)
    assert len(event.get_cwts()) == 0


@pytest.mark.django_db
def test_get_year(db_setup):
    """the get_year() method of a stocking event parses the year out of
    proejct code and returns a formatted year - either 19XX or 20XX.

    """
    event = Event.objects.get(fs_event=9988)
    assert event.get_year() == 2003

    event = Event.objects.get(fs_event=1122)
    assert event.get_year() == 1998


@pytest.mark.django_db
def test_event_save(db_setup):
    """The save method populates geom from dd_lat and dd_lon and updates
    the popup text.
    """

    lot = Lot.objects.all()[0]
    site = StockingSite.objects.all()[0]

    event1 = EventFactory.build(site=site, lot=lot)

    #before we save teh object, the geom and popup text attributes are empty
    assert event1.geom is None
    assert event1.popup_text == ''

    event1.save()

    #now they are not
    assert event1.geom is not None
    assert event1.popup_text != ''
