'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_hatchery_annual_events.py
Created: 24 Sep 2015 10:28:44


DESCRIPTION:

This script contains tests that verify that the view to render annual
stocking events by hatchery contains the expected data.

Specifically, the view should contain the proponents name and
accronym, the year, a leaflet map a table for each species that should
contain details about each event, as well as the number of events for
that species.

The view should not contain information about stocking events in
different years or by different proponents.


A. Cottrill
=============================================================

'''
import pytest
from django.core.urlresolvers import reverse

from fsis2.models import Proponent
from fsis2.tests.factories import *

from datetime import datetime

@pytest.fixture(scope='function')
def db_setup(db):
    """For the tests in this file, we will need three different species,
    two different hatcheries, and several events.

    """

    BuildDateFactory.create()
    ReadmeFactory.create()

    laketrout = SpeciesFactory.create()
    chinook = SpeciesFactory.create(common_name='Chinook Salmon')
    rainbow = SpeciesFactory.create(common_name='Rainbow Trout')


    hatchery1 = ProponentFactory(abbrev='ABC',
                                 proponent_name='ABC Fishin Club')

    hatchery2 = ProponentFactory(abbrev='OFG',
                                 proponent_name='Old Fishin Geezers')

    laketrout_lot = LotFactory(species=laketrout,proponent=hatchery2)

    chinook_lot = LotFactory(species=chinook, proponent=hatchery1)
    rainbow_lot = LotFactory(species=rainbow, proponent=hatchery1)

    site1 = StockingSiteFactory(site_name='Site1')
    site2 = StockingSiteFactory(site_name='Site2')
    site3 = StockingSiteFactory(site_name='Site3')
    site4 = StockingSiteFactory(site_name='Site4')
    site5 = StockingSiteFactory(site_name='Site5')

    stocking_date = datetime(2010,10,15)
    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(site=site1, lot=laketrout_lot,
                          event_date=stocking_date)

    #These are events associated with hatchery 1 - two rainbow and one
    #chinook event in 2010, two chinook events inthe spring of 2011.
    #stocking in 2010
    event2 = EventFactory(site=site2, lot=rainbow_lot,
                          event_date=stocking_date)
    event3 = EventFactory(site=site3, lot=rainbow_lot,
                          event_date=stocking_date)

    event4 = EventFactory(site=site2, lot=chinook_lot,
                          event_date=stocking_date)

    #Stocking events in the spring of 2011
    stocking_date = datetime(2011,4,15)
    event6 = EventFactory(site=site4, lot=chinook_lot,
                          event_date=stocking_date)
    event7 = EventFactory(site=site5, lot=chinook_lot,
                          event_date=stocking_date)



@pytest.mark.django_db
def test_ahe_nonexistant_proponent(client, db_setup):
    """If we try to access a list of stocking events for a hatchery
    that does exists, the vuew should return a meaningful message to taht
    effect.

    Arguments:
    - `db_setup`:

    """

    url = reverse('hatchery_annual_events', kwargs={'hatchery':'XYZ',
                                                    'year':2001})
    response = client.get(url)
    assert response.status_code == 404

    content = str(response.content)

    assert 'Proponent with abbreviation XYZ does not exist.' in content


@pytest.mark.django_db
def test_ahe_proponent_without_events(client, db_setup):
    """If we access a url that corresponse to an actual proponent but they
    didn't stock in that year, the template should return a meaningful
    message to that effect.'

    Arguments:
    - `db_setup`:

    """

    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2001

    url = reverse('hatchery_annual_events', kwargs={'hatchery':proponent.abbrev,
                                                    'year':yr})
    response = client.get(url)
    content = str(response.content)

    msg_base = '{} ({}) did not stock any fish in {}'
    msg = msg_base.format(proponent.proponent_name, proponent.abbrev, yr)

    assert msg in content



@pytest.mark.django_db
def test_ahe_future_year_throws_404(client, db_setup):
    """If someone specifies a year in the future, we should show the 404
    page - no records could be found.

    Arguments:
    - `db_setup`:

    """
    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2100

    url = reverse('hatchery_annual_events', kwargs={'hatchery':proponent.abbrev,
                                                   'year':yr})
    response = client.get(url)
    assert response.status_code == 404

    content = str(response.content)
    assert "Dates in the future not allowed!!" in content
    assert 'Page Not Found' in content





@pytest.mark.django_db
def test_ahe_contains_proponent_name(client, db_setup):
    """The annual report for a particular hatchery must include the
    hatcheries name.

    Arguments:
    - `db_setup`:

    """

    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2010

    url = reverse('hatchery_annual_events', kwargs={'hatchery':proponent.abbrev,
                                                    'year':yr})
    response = client.get(url)
    content = str(response.content)

    msg_base = '{} ({})'
    msg = msg_base.format(proponent.proponent_name, proponent.abbrev)
    assert msg in content


@pytest.mark.django_db
def test_ahe_contains_year(client, db_setup):
    """The annual report for a particular hatchery must include the
    year.

    Arguments:
    - `db_setup`:
    """
    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2010

    url = reverse('hatchery_annual_events', kwargs={'hatchery':proponent.abbrev,
                                                    'year':yr})
    response = client.get(url)
    content = str(response.content)

    msg_base = 'in {}:'
    msg = msg_base.format(yr)
    assert msg in content



@pytest.mark.django_db
def test_ahe_contains_spc_names(client, db_setup):
    """The annual report for a particular hatchery must include the names
    of the species they stocked. But should not include the names of
    species they did not stock.

    Arguments:
    - `db_setup`:

    """
    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2010

    url = reverse('hatchery_annual_events', kwargs={'hatchery':proponent.abbrev,
                                                    'year':yr})
    response = client.get(url)
    content = str(response.content)

    assert "Lake Trout" not in content
    assert "Rainbow Trout" in content
    assert "Chinook Salmon" in content


@pytest.mark.django_db
def test_ahe_contains_event_counts(client, db_setup):
    """The tables should contain the number of stocking events by species.

    Arguments:
    - `db_setup`:
    """
    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2010

    url = reverse('hatchery_annual_events', kwargs={'hatchery':proponent.abbrev,
                                                    'year':yr})
    response = client.get(url)
    content = str(response.content)

    assert "(N=1)" in content
    assert "(N=2)" in content
    assert "Site2" in content
    assert "Site3" in content

    #site 1 was stocked with lake trout by the old geezers - should
    #not appear in the response.
    assert "Site1" not in content


@pytest.mark.django_db
def test_ahe_not_contain_events_different_year(client, db_setup):
    """The view should not contain details of events that occurred in a
    different year. Events that occured in 2010 should not appear in
    the summary of events in 2009.

    Arguments:
    - `db_setup`:

    """
    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2010

    url = reverse('hatchery_annual_events', kwargs={'hatchery':proponent.abbrev,
                                                    'year':yr})
    response = client.get(url)
    content = str(response.content)

    #sites 4 and 5 were stocked in 2011 and should not appear here:
    assert "Site4" not in content
    assert "Site5" not in content


@pytest.mark.django_db
def test_ahe_not_contain_events_different_hatchery(client, db_setup):
    """The view should not contain details of events that were conducted
    by a different proponent.  For example, events that where
    associated with Blue Jay should not appear in the summaries for
    Chatsworth.

    Arguments:
    - `db_setup`:

    """
    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2010

    url = reverse('hatchery_annual_events', kwargs={'hatchery':proponent.abbrev,
                                                    'year':yr})
    response = client.get(url)
    content = str(response.content)

    assert "Site1" not in content
    assert "Lake Trout" not in content
    assert "OFG" not in content
    assert "Old Fishin Geezers" not in content
