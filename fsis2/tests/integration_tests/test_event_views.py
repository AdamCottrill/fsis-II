'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_event_views.py
Created: 06 Oct 2015 13:29:50


DESCRIPTION:

The tests in this script verfy that the views assoicated with events
render as expected.  Views tested in this script include event list,
event detail and find_event using complete and partial event numbers.
Views with more complicated subsets of event data are tested in
dedicated files.


Event List
- uses 'fsis2/event_detail.html'
- contains
  - list of events in the database
  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name (and acronym)
  - Find Event quick search

Event List <Year>
- same as Event List but only for events stocked in a given year are returned
- NOT IMPLEMTNED

Find Event Partial
- uses 'fsis2/event_detail.html'
- contains
  - list of events in the database that partially match criteria
  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name(and acronym)
  - Find Event quick search
- if no events match the criteria, an appropriate message should appear


Find Event Complete
- uses 'fsis2/event_detail.html'
- contains
  - list of events in the database that match criteria perfectly.
    Partial Matches should be excluded.
  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name (and acronym)
  - Find Event quick search
- if no events match the criteria, an appropriate message should appear

Event Detail
- uses 'fsis2/event_detail.html'
- contains
  - fSIS Event number
  - FSIS Lot Number
  - species names
  - strain
  - stocking date (and default if missing date)
  - number stocked
  - life stage
  - transit method
  - stocking location - name, lat, lon and ID
  - basin and grid number

  - if tags are assoiciated with this stocking event, they should be
    presented as a table.  The table should contain: tag numbers year
    class, stocking year, speceis, strain, lifestage, agency and
    stocking location.


- if no events match the id, an appropriate message should appear


A. Cottrill
=============================================================

'''


import pytest
from django.core.urlresolvers import reverse

from fsis2.tests.factories import *


@pytest.fixture(scope='function')
def db_setup(db):
    """For the tests in this file, we will need three different species,
    two different hatcheries, and several events.

    """

    BuildDateFactory.create()
    ReadmeFactory.create()

    rainbow = SpeciesFactory.create(common_name='Rainbow Trout',
                                    species_code=76)

    wild = StrainFactory(species=rainbow, strain_name='wild')

    hatchery1 = ProponentFactory(abbrev='ABC',
                                 proponent_name='ABC Fishin Club')

    rainbow_lot = LotFactory(species=rainbow, strain=wild,
                             spawn_year=2011,
                             proponent=hatchery1,
                             fs_lot=7576)

    site1 = StockingSiteFactory(site_name='Site1')
    site2 = StockingSiteFactory(site_name='Site2')
    site3 = StockingSiteFactory(site_name='Site3')
    site4 = StockingSiteFactory(site_name='Site4')
    site5 = StockingSiteFactory(site_name='Site5')

    stocking_date = datetime(2010,10,15)
    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(site=site1, lot=rainbow_lot,
                          stkcnt = 11111, fs_event = '998877',
                          event_date=stocking_date)

    event2 = EventFactory(site=site2, lot=rainbow_lot,
                          stkcnt = 22222, fs_event = '887766',
                          event_date=stocking_date)

    event3 = EventFactory(site=site3, lot=rainbow_lot,
                          stkcnt = 33333, fs_event = '776655',
                          event_date=stocking_date)

    event4 = EventFactory(site=site4, lot=rainbow_lot,
                          stkcnt = 44444, fs_event = '665544',
                          event_date=stocking_date)

    event5 = EventFactory(site=site5, lot=rainbow_lot,
                          stkcnt = 55555,  fs_event = '554433',
                          event_date=stocking_date)

    #need to add some tags here:
    tagging_event = TaggingEventFactory.create(stocking_event=event1)
    tags = ['631234','635555','639999']
    for tag in tags:
        CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=tag)


@pytest.mark.django_db
def test_event_list_status_and_template(client, db_setup):
    """verify that the event list url returns a status code of 200 and uses
    the template we think it does

    """

    url = reverse('event_list')
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/event_list.html' in templates


@pytest.mark.django_db
def test_event_list_contains_quick_search(client, db_setup):
    """the event list should contain an input box allowing the user to
    quickly find an event by FSIS Event id.

    """

    url = reverse('event_list')
    response = client.get(url)
    content = str(response.content)

    #these are some strings unique to the search box
    assert '<input type="text" class="form-control" name="event"' in content
    assert 'placeholder="Stocking Event Number">' in content


@pytest.mark.django_db
def test_event_list_contains_expected_data(client, db_setup):
    """verify that the event list url returns a status code of 200 and uses
    the template we think it does

  - the of stocking events should contain basic infomation such as:
    - fsis event numbers
    - species
    - strain
    - number stocked
    - event date
    - site name
    - clip code
    - development stage

    """

    url = reverse('event_list')
    response = client.get(url)
    content = str(response.content)

    #the event list should contain inforamtion from all of our events above;

    stkcnts = ['11,111','22,222','33,333','44,444','55,555']
    for cnt in stkcnts:
        assert cnt in content

    elements = ['Rainbow Trout', 'Wild', 'Site1', 'Site2', 'Site3', 'Site4',
                'Site5', 'Yearling (10-19 months)']

    for element in elements:
        assert element in content

    #finally check the links to fsis event numbers
    events = Event.objects.all()
    ids = [x.id for x in events]
    for item in ids:
        assert '/fsis2/events/detail/{}'.format(item) in content

    fs_events = [str(x.fs_event) for x in events]
    for item in fs_events:
        assert item in content



@pytest.mark.django_db
def test_event_list_contains_expected_data_partial(client, db_setup):
    """verify that the event list url returns records for the events that
    partially match the pattern and does not contain information
    assoicated with events/records that we know do not match.

  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name (and acronym)

    """

    url = reverse('event_list')
    response = client.get(url,{'event':'8877'})
    content = str(response.content)

    #only the first two events should match *8877*
    #these are elements that are unique to records that should be returned
    stkcnts = ['11,111','22,222']
    for cnt in stkcnts:
        assert cnt in content
    sites = ['Site1', 'Site2']
    for site in sites:
        assert site in content

    #these are elements that are unique to records that should *NOT* be returned
    stkcnts = ['33,333','44,444','55,555']
    for cnt in stkcnts:
        assert cnt not in content
    sites = ['Site3', 'Site4','Site5']
    for site in sites:
        assert site not in content





@pytest.mark.django_db
def test_event_list_partial_no_match(client, db_setup):
    """If the partial event id submitted does not match any event in the
    database, an appropriate message should be thrown. 'No records match
    that criteria'

    """

    url = reverse('event_list')
    response = client.get(url,{'event':'999'})
    content = str(response.content)

    msg = "Sorry no events match that criteria."
    assert msg in content


@pytest.mark.django_db
def test_event_detail_status_and_template(client, db_setup):
    """verify that the event detail url returns a status code of 200 and uses
    the template we think it does

    """

    event = Event.objects.all()[0]
    url = reverse('event_detail', kwargs={'pk':event.id})
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/event_detail.html' in templates



@pytest.mark.django_db
def test_event_detail_expected_content(client, db_setup):
    """verify that the lot detail page contains the information we think
    it does.  Specifically:
    - lot id
    - species names
    - proponent
    - spawn year
    - a map of associated stocking events
    - a table of associated stocking events

    verify that it does not contain information about events
    associated with other lots of fish.

    """

    event = Event.objects.get(fs_event=998877)

    url = reverse('event_detail', kwargs={'pk':event.id})
    response = client.get(url)

    content = str(response.content)

    assert '998877' in content
    assert event.lot.fs_lot in content
    assert 'Rainbow Trout' in content
    assert event.lot.species.scientific_name in content
    assert event.lot.strain.strain_name in content
    assert '{:,}'.format(event.stkcnt) in content
    assert 'Yearling (10-19 months)' in content
    assert 'Site1' in content
    assert 'Latitude:' in content
    assert 'Longitude:' in content
    assert event.site.grid in content


@pytest.mark.django_db
def test_event_detail_without_tags(client, db_setup):
    """Most events won't have any tags associated with them.  In this
    case, the details page should state:

    There do not appear to be any tags associated with this event

    """
    #use the 5th stocking event - no tags associated with it
    event = Event.objects.get(fs_event=554433)

    url = reverse('event_detail', kwargs={'pk':event.id})
    response = client.get(url)
    content = str(response.content)

    msg = 'There do not appear to be any tags associated with this event'
    assert msg in content

    tag_ids = ['63-12-34','63-55-55','63-99-99']
    for tag in tag_ids:
        assert tag not in content



@pytest.mark.xfail
@pytest.mark.django_db
def test_event_detail_with_tags(client, db_setup):
    """if tags are assoiciated with this stocking event, they should
    be presented as a table.  The table should contain: tag numbers
    year class, stocking year, speceis, strain, lifestage, agency and
    stocking location.

    This tests currently fails because cwt's displayed on the template
    are drawn from the cwt application, not from cwts applied in FSIS.
    Is this really what we want to do here?  Perhaps we could compare
    the two sources and issue a warning if there is a discrepancy.

    """

    #the first stocking event does have some tags associated with it:
    event = Event.objects.get(fs_event=998877)

    url = reverse('event_detail', kwargs={'pk':event.id})
    response = client.get(url)
    content = str(response.content)

    #this fails because these tag number as in CWTS applied, but not
    #in the CWT application tables.
    tag_ids = ['63-12-34','63-55-55','63-99-99']
    for tag in tag_ids:
        assert tag in content

    msg = 'There do not appear to be any tags associated with this event'
    assert msg not in content



@pytest.mark.django_db
def test_event_detail_no_matching_id(client, db_setup):
    """ If the event id submitted does not match any event in the database, an
    appropriate message should be thrown. 'No records match that
    criteria'
    """

    url = reverse('event_detail', kwargs={'pk':'54321'})
    response = client.get(url)
    assert response.status_code == 404

    #content = str(response.content)
    #assert 'Event with id 54321 does not exist.' in content
