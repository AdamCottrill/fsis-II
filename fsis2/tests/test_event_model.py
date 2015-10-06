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
                          event_date=stocking_date,
                          stkcnt = 10000,
                        )

@pytest.mark.django_db
def test_spc_code_proptery(db_setup):
    """the spc_code property of a stocking event should return the species
    code of the stocked fish.

    """
    event = Event.objects.all()[0]
    assert event.spc_code == 76


@pytest.mark.django_db
def test_hatchery_property(db_setup):
    """the hatchery property of a stocking event should return the abbreviation
    code for the hatchery/proponent who raised and stocked the fish.

    """
    event = Event.objects.all()[0]
    assert event.hatchery_code == 'ABC'


@pytest.mark.django_db
def test_strain_property(db_setup):
    """the strain property of a stocking event should return the strain code
    for fish stocked in this event.

    """
    event = Event.objects.all()[0]
    assert event.strain_code == 'WRT'


@pytest.mark.django_db
def test_get_popup_text(db_setup):
    """the get_popup_text() method of the stocking event is not intended
    to be called directly, but should contain all of the basic
    information about the stocking event in a html table.

    """
    event = Event.objects.all()[0]
    popup_text = event.get_popup_text()

    #html table tags:
    assert '<table>' in popup_text
    assert '</table>' in popup_text

    assert 'Rainbow Trout' in popup_text
    assert 'ABC Fishin Club'

    assert 'Site1' in popup_text
    assert 'October 15 2010' in popup_text

    assert '10,000' in popup_text
