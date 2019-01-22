'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_annual_events.py
Created: 30 Sep 2015 07:26:10


DESCRIPTION:

This file contains tests to verify that the view that returns all of
the events in a particular year renders as expected.

Specifically, the view should contain the year, a leaflet map, and a
table for each species that should contain details about each event,
as well as the number of events for that species.

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
    brown = SpeciesFactory.create(common_name='Brown Trout')
    rainbow = SpeciesFactory.create(common_name='Rainbow Trout')

    hatchery1 = ProponentFactory(abbrev='ABC',
                                 proponent_name='ABC Fishin Club')

    hatchery2 = ProponentFactory(abbrev='OFG',
                                 proponent_name='Old Fishin Geezers')

    laketrout_lot = LotFactory(species=laketrout,proponent=hatchery2)

    brown_lot = LotFactory(species=brown, proponent=hatchery1)
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
    #brown event in 2010, two brown events inthe spring of 2011.
    #stocking in 2010
    event2 = EventFactory(site=site2, lot=rainbow_lot,
                          event_date=stocking_date)
    event3 = EventFactory(site=site3, lot=rainbow_lot,
                          event_date=stocking_date)

    event4 = EventFactory(site=site2, lot=brown_lot,
                          event_date=stocking_date)

    #Stocking events in the spring of 2011
    stocking_date = datetime(2011,4,15)
    event6 = EventFactory(site=site4, lot=brown_lot,
                          event_date=stocking_date)
    event7 = EventFactory(site=site5, lot=brown_lot,
                          event_date=stocking_date)


@pytest.mark.django_db
def test_annual_events_view(client, db_setup):
    """Verify that the url returns an appropriate status code and that the
    template is the one we think it is.

    Arguments:
    - `db_setup`:

    """

    yr = 2010
    url = reverse('annual_events', kwargs={'year':yr})

    print('url={}'.format(url))

    response = client.get(url)
    content = str(response.content)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/annual_events.html' in templates



@pytest.mark.django_db
def test_annual_events_year_without_events(client, db_setup):
    """If we access a url that corresponse to a year that had no stocking
    events (e.g. - 1955), the template should return a meaningful
    message to that effect.'

    Arguments:
    - `db_setup`:

    """

    yr = 1955

    url = reverse('annual_events', kwargs={'year':yr})
    response = client.get(url)
    content = str(response.content)

    msg_base = 'There do not appear to have been any fish stocked in {}.'
    msg = msg_base.format(yr)

    assert msg in content


@pytest.mark.django_db
def test_annual_events_future_year_throws_404(client, db_setup):
    """If someone specifies a year in the future, we should show the 404
    page - no records could be found.

    Arguments:
    - `db_setup`:

    """
    yr = 2100

    url = reverse('annual_events', kwargs={'year':yr})
    response = client.get(url)
    assert response.status_code == 404

    content = str(response.content)
    assert "Dates in the future not allowed!!" in content
    assert 'Page Not Found' in content



@pytest.mark.django_db
def test_annual_events_contains_year(client, db_setup):
    """The annual report for a particular hatchery must include the
    year.

    Arguments:
    - `db_setup`:
    """
    yr = 2010

    url = reverse('annual_events', kwargs={'year':yr})
    response = client.get(url)
    content = str(response.content)

    msg_base = 'Stocking events for {}:'
    msg = msg_base.format(yr)
    assert msg in content


@pytest.mark.django_db
def test_annual_events_contains_spc_names(client, db_setup):
    """The annual report for a particular hatchery must include the names
    of the species they stocked in that year but should not include the names of
    species that were stocked in other years.

    Arguments:
    - `db_setup`:

    """
    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2011

    url = reverse('annual_events', kwargs={'year':yr})
    response = client.get(url)
    content = str(response.content)

    #only Brown were stocked in 2011
    assert "Brown Trout" in content

    #lake trout and rainbow were stocked only in 2010
    assert "Lake Trout" not in content
    assert "Rainbow Trout" not in content


@pytest.mark.django_db
def test_annual_events_contains_event_counts(client, db_setup):
    """The tables should contain the number of stocking events by species.

    Arguments:
    - `db_setup`:
    """

    yr = 2010

    url = reverse('annual_events', kwargs={'year':yr})
    response = client.get(url)
    content = str(response.content)

    assert "(N=1)" in content
    assert "(N=2)" in content

    assert "Site1" in content
    assert "Site2" in content
    assert "Site3" in content


@pytest.mark.django_db
def test_annual_events_not_contain_events_different_year(client, db_setup):
    """The view should not contain details of events that occurred in a
    different year. Events that occured in 2010 should not appear in
    the summary of events in 2009.

    Arguments:
    - `db_setup`:

    """
    yr = 2010

    url = reverse('annual_events', kwargs={'year':yr})
    response = client.get(url)
    content = str(response.content)

    #sites 4 and 5 were stocked in 2011 and should not appear here:
    assert "Site4" not in content
    assert "Site5" not in content


@pytest.mark.django_db
def test_annual_events_contains_hatchery_acronym(client, db_setup):
    """The view should contain the acronym of the hatchery associated with
    each stocking event.

    Arguments:
    - `db_setup`:

    """

    proponent = Proponent.objects.get(abbrev='ABC')
    yr = 2011

    url = reverse('annual_events', kwargs={'year':yr})
    response = client.get(url)
    content = str(response.content)

    assert "ABC" in content
    #the old fishin' geezers only stocked in 2010
    assert "OFG" not in content



@pytest.mark.django_db
def test_most_recent_events_contains_last_year_only(client, db_setup):
    """The view for most recent event should only contain only those
    events conducted in the most recent year.

    Arguments:
    - `db_setup`:

    """

    url = reverse('most_recent_events')
    response = client.get(url)

    content = str(response.content)

    assert "Site4" in content
    assert "Site5" in content
    assert "ABC" in content
    assert "ABC Fishin Club" in content
    assert "Brown Trout" in content

    #these should not be in the response
    sites =  ["Site1", "Site2", "Site3"]
    for site in sites:
        assert site not in content
    assert 'Rainbow Trout' not in content
    assert 'Lake Trout' not in content

    assert 'OFG' not in content
    assert 'Old Fishin Geezers' not in content
