'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_site_views.py
Created: 06 Oct 2015 13:29:50

DESCRIPTION:

The tests in this script verfy that the views assoicated with stocking sites
render as expected.  Views tested in this script include site list,
site detail and find_site using complete and partial site names.
Views with more complicated subsets of site data are tested in
dedicated files.


Site List
- uses 'fsis2/site_list.html'
- contains
  - list of sites in the database
  - the list should contain basic infomation such as:
    + FSIS Site ID
    + site name,
    + basin,
    + grid and
    + Latitude and longitude
  - Find Site quick search


Find Site Partial
- uses 'fsis2/site_list.html'
- contains
  - list of sites in the database that partially match criteria
  - the list should contain basic infomation such as:
    + FSIS Site ID
    + site name,
    + basin,
    + grid and
    + Latitude and longitude
- sites that do not match the criteria should not be returned by the list
- if no sites match the criteria, an appropriate message should appear


Site Detail
- uses 'fsis2/site_detail.html'
- contains
  - FSIS Site number
  - site name
  - basin,
  - grid and
  - Latitude and longitude
  - utm
  - a table of stocking events that have occured at that site that
    should contain:
      + FSIS Event
      + Number Stocked
      + Event Date
      + Species
      + Strain
      + Clip Applied
      + Development Stage

- if no sites match the id, an appropriate message should appear


A. Cottrill
=============================================================

'''


import pytest
from django.core.urlresolvers import reverse

from fsis2.tests.factories import *


@pytest.fixture(scope='function')
def db_setup(db):
    """For the tests in this file, we will need three different species,
    two different hatcheries, and several sites.

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

    NotStocked = StockingSiteFactory(site_name='Not Stocked')
    site1 = StockingSiteFactory(site_name='My Creek',
                                grid = '0101', basin='North Channel',
                                dd_lat = 45.5, dd_lon=-81.25)

    site2 = StockingSiteFactory(site_name='Your Creek',
                                grid = 2046, basin='Georgian Bay')
    site3 = StockingSiteFactory(site_name='Site3')
    site4 = StockingSiteFactory(site_name='Site4')
    site5 = StockingSiteFactory(site_name='Site5')

    stocking_date = datetime(2010,10,15)
    #we need an site for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(site=site1, lot=rainbow_lot,
                          stkcnt = 11111, fs_event = '998877',
                          event_date=stocking_date)

    event2 = EventFactory(site=site1, lot=rainbow_lot,
                          stkcnt = 22222, fs_event = '887766',
                          event_date=stocking_date)

    event3 = EventFactory(site=site1, lot=rainbow_lot,
                          stkcnt = 33333, fs_event = '776655',
                          event_date=stocking_date)

    event4 = EventFactory(site=site2, lot=rainbow_lot,
                          stkcnt = 44444, fs_event = '665544',
                          event_date=stocking_date)

    event5 = EventFactory(site=site3, lot=rainbow_lot,
                          stkcnt = 55555,  fs_event = '554433',
                          event_date=stocking_date)


@pytest.mark.django_db
def test_site_list_status_and_template(client, db_setup):
    """verify that the site list url returns a status code of 200 and uses
    the template we think it does

    """

    url = reverse('site_list')
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/site_list.html' in templates


@pytest.mark.django_db
def test_site_list_contains_quick_search(client, db_setup):
    """the site list should contain an input box allowing the user to
    quickly find an site by FSIS Site id.

    """

    url = reverse('site_list')
    response = client.get(url)
    content = str(response.content)

    #these are some strings unique to the search box
    assert '<input type="text" class="form-control" name="q"' in content
    assert 'placeholder="Find Stocking Site">' in content


@pytest.mark.django_db
def test_site_list_contains_expected_data(client, db_setup):
    """verify that the site list url returns a status code of 200 and uses
    the template we think it does

  - the of stocking sites should contain basic infomation such as:
    - fsis site numbers
    - species
    - strain
    - number stocked
    - site date
    - site name
    - clip code
    - development stage

    """

    url = reverse('site_list')
    response = client.get(url)
    content = str(response.content)

    sites = ['My Creek', 'Your Creek', 'Site3', 'Site4','Site5']
    for site in sites:
        assert site in content

    basins = ["North Channel", "Georgian Bay", "Main Basin"]
    for basin in basins:
        assert basin in content

    grids = ['0101', '2046', '2456']
    for grid in grids:
        assert grid in content

    #make sure that the lat and lon are included and are formated as ddm
    assert "Latitude"  in content
    assert "45&#176;30.000&#39; N" in content  # 45.5 degrees

    assert "Longitude" in content
    assert "-81&#176;15.000&#39; W" in content # -81.25 degrees


@pytest.mark.django_db
def test_site_list_contains_expected_data_partial(client, db_setup):
    """verify that the site list url returns records for the sites that
    partially match the pattern and does not contain information
    assoicated with sites/records that we know do not match.

  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name (and acronym)

    """

    url = reverse('site_list')
    response = client.get(url,{'q':'creek'})
    content = str(response.content)

    #only the first two sites should match *creek*
    #these are elements that are unique to records that should be returned
    sites = ['My Creek', 'Your Creek']
    for site in sites:
        assert site in content
    assert "North Channel" in content
    assert "Georgian Bay" in content

    grids = ['0101', '2046']
    for grid in grids:
        assert grid in content

    #make sure that the lat and lon are included and are formated as ddm
    assert "Latitude"  in content
    assert "45&#176;30.000&#39; N" in content  # 45.5 degrees

    assert "Longitude" in content
    assert "-81&#176;15.000&#39; W" in content # -81.25 degrees

    #NOT in final response
    sites = ['Site3', 'Site4','Site5']
    for site in sites:
        assert site not in content

    assert "Honey Hole" not in content
    assert "Main Basin" not in content
    assert '2456' not in content


@pytest.mark.django_db
def test_site_list_partial_no_match(client, db_setup):
    """If the partial site id submitted does not match any site in the
    database, an appropriate message should be thrown. 'No records match
    that criteria'

    """

    url = reverse('site_list')
    response = client.get(url,{'q':'999'})
    content = str(response.content)

    msg = 'Sorry no named stocking sites match that criteria'
    assert msg in content


@pytest.mark.django_db
def test_site_detail_status_and_template(client, db_setup):
    """verify that the site detail url returns a status code of 200 and uses
    the template we think it does

    """

    site = StockingSite.objects.all()[0]
    url = reverse('site_detail', kwargs={'pk':site.id})
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/site_detail.html' in templates


@pytest.mark.django_db
def test_site_detail_expected_content(client, db_setup):
    """verify that the lot detail page contains the information we think
    it does.  Specifically:

    verify that it does not contain information about sites
    associated with other lots of fish.

    """

    site = StockingSite.objects.get(site_name='My Creek')

    url = reverse('site_detail', kwargs={'pk':site.id})
    response = client.get(url)

    content = str(response.content)

    assert site.site_name in content
    assert site.grid in content
    assert site.basin in content
    assert str(site.fsis_site_id) in content
    assert site.utm in content
    assert site.deswby in content


    #make sure that the lat and lon are included and are formated as ddm
    assert "Latitude"  in content
    assert "45&#176;30.000&#39; N" in content  # 45.5 degrees

    assert "Longitude" in content
    assert "-81&#176;15.000&#39; W" in content # -81.25 degrees



@pytest.mark.django_db
def test_site_detail_without_events(client, db_setup):
    """Most sites will have at least one stocking event associated with
    them (if there are no stocking events associated with a site is it
    really a stocking site??).  In the unlikely event that a site has
    not stocking events associated with it, the template should
    display a meaningful message.

    There do not appear to be any events associated with this site.

    """
    #use the 5th stocking site - no events associated with it
    site = StockingSite.objects.get(site_name='Not Stocked')

    url = reverse('site_detail', kwargs={'pk':site.id})
    response = client.get(url)
    content = str(response.content)

    msg = 'There are currenly no stocking events associated with this location'
    assert msg in content


@pytest.mark.django_db
def test_site_detail_with_events(client, db_setup):
    """if events are assoiciated with this stocking site, they should
    be presented as a table.  The table should contain:
      + FSIS Event
      + Number Stocked
      + Event Date
      + Species
      + Strain
      + Clip Applied
      + Development Stage
    """

    #the first stocking site does have some events associated with it:
    site = StockingSite.objects.get(site_name='My Creek')

    url = reverse('site_detail', kwargs={'pk':site.id})
    response = client.get(url)
    content = str(response.content)

    fsis_events = ['998877', '887766', '776655']
    for event in fsis_events:
        event in content

    stkcnts = ['11,111','22,222', '33,333']
    for cnt in stkcnts:
        assert cnt in content

    assert 'Rainbow Trout' in content
    assert 'Wild'
    assert 'Yearling (10-19 months)' in content


    #NOT in content
    fsis_events = ['665544', '554433']
    for event in fsis_events:
        event not in content

    stkcnts = ['44,444','55,555']
    for cnt in stkcnts:
        assert cnt not in content


@pytest.mark.django_db
def test_site_detail_no_matching_id(client, db_setup):
    """ If the site id submitted does not match any site in the database, an
    appropriate message should be thrown. 'No records match that
    criteria'
    """

    url = reverse('site_detail', kwargs={'pk':'54321'})
    response = client.get(url)
    assert response.status_code == 404
