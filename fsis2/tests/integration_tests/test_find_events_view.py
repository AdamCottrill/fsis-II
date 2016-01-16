'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_find_sites_view.py
Created: 30 Sep 2015 07:26:10

DESCRIPTION:

This script ensures that the view to find events in a region of
interest contains all of the elements we think it should and that the
view functions as expected when we submit a region of interest.

Specifically, a get request to the url should return a response that contains:

GET Request should contain:
- expanitory title "Find Stocking Events"
- earliest year - with default place holder earliest stocking event
- latest year - with default place holder most recent stocking event
- list of species
- submit button
- reset button

POST Requests:

No species Specified
should return information about the stocking events that fall within the roi
- only sites within the roi should be returned
+ information returned about each site should include:
    + FSIS Event
    + Species
    + Strain
    + Number Stocked
    + Event Date
    + Site Name
    + Clip Applied
    + Development Stage

- events outside the roi should not be in the response

- if no events are in the roi, an appropriate error message should be
  returned. "Sorry no events match that criteria"

- if no roi is provided, a message should be displayed and form re-rendered.

- if the geometry is invalid, the form should report an appropriate
  message

- if the years are not valid years - the form should report an
  appropriate message

- when several species specifed, the corresponding stocking events
  should be returned.

- if the earliest is specified in the form, events prior to that year
  should be exlcuded.

- if the latest year is specified in the form, events after to that year
  should be exlcuded.

- if both ealiest and latest years are specified, only events that
occured between those years should be included

- if both ealiest and latest years are specified and they are equal,
only events that occured in that year should be included


A. Cottrill
=============================================================

'''

import pytest
from django.contrib.gis.geos import GEOSGeometry, LinearRing, Point, Polygon
from django.core.urlresolvers import reverse

from fsis2.tests.factories import *
from fsis2.models import Species


@pytest.fixture(scope='class')
def db_setup():
    """For the tests in this file, we will need several different species,
    and several events.

    one species will not be stocked at all, but should be included in
    the list of available species.

    lake trout will be stocked, but only outside of the roi and should
    not appear in any of the responses.

    The brown and rainbow events will occur at different location and
    over different range of years to test the form inputs for species
    and first year-last year

    """

    BuildDateFactory.create()
    ReadmeFactory.create()

    lake_trout = SpeciesFactory(common_name='Lake Trout',
                                scientific_name='Salvelinus namaycush')

    brown_trout = SpeciesFactory(common_name='Brown Trout',
                                scientific_name='Salmo trutta')

    rainbow_trout = SpeciesFactory(common_name='Rainbow Trout',
                                scientific_name='Oncorhynchus mykiss')

    coho = SpeciesFactory(common_name='Coho Salmon',
                                scientific_name='Oncorhynchus kisutch')

    lt_strain = StrainFactory(species=lake_trout)
    rt_strain = StrainFactory(species=rainbow_trout,
                              sto_code = "Wild",
                              strain_code = "WILD",
                              strain_name = "Wild")
    bt_strain = StrainFactory(species=brown_trout,
                              sto_code = "Wild",
                              strain_code = "WILD",
                              strain_name = "Wild")
    coho_strain = StrainFactory(species=coho,
                              sto_code = "Wild",
                              strain_code = "WILD",
                              strain_name = "Wild")

    laker_lot = LotFactory(species=lake_trout, strain=lt_strain)
    brown_lot = LotFactory(species=brown_trout, strain=bt_strain)
    coho_lot = LotFactory(species=coho, strain=coho_strain)
    rainbow_lot = LotFactory(species=rainbow_trout, strain=rt_strain)

    outside_pt = GEOSGeometry('POINT(-81.0 44.9)')
    outside = StockingSiteFactory(site_name='Outside Site',
                                  geom=outside_pt)

    inside_pt = GEOSGeometry('POINT(-81.8 45.1)')
    insideA = StockingSiteFactory(site_name='Inside SiteA',
                                  geom=inside_pt)
    insideB = StockingSiteFactory(site_name='Inside SiteB',
                                  geom=inside_pt)
    insideC = StockingSiteFactory(site_name='Inside SiteC',
                                  geom=inside_pt)
    insideD = StockingSiteFactory(site_name='Inside SiteD',
                                  geom=inside_pt)


    date_2000 = datetime(2000,10,15)
    date_2005 = datetime(2005,10,15)
    date_2010 = datetime(2010,10,15)

    event1 = EventFactory(lot=laker_lot, site=outside, geom=outside_pt,
                          event_date=date_2000)
    event2 = EventFactory(lot=laker_lot, site=outside, geom=outside_pt,
                          event_date=date_2005)
    event3 = EventFactory(lot=laker_lot, site=outside, geom=outside_pt,
                          event_date=date_2010)

    event4 = EventFactory(lot=rainbow_lot, site=insideA, geom=inside_pt,
                          event_date=date_2005)

    event5 = EventFactory(lot=brown_lot, site=insideB, geom=inside_pt,
                          event_date=date_2000)
    event6 = EventFactory(lot=brown_lot, site=insideC, geom=inside_pt,
                          event_date=date_2005)
    event7 = EventFactory(lot=brown_lot, site=insideD, geom=inside_pt,
                          event_date=date_2010)


@pytest.fixture(scope='class')
def roi():
    """A fixture to return a region of interest polygon.  The Stocking
    Site 'Inside' is in the middle of this roi.

    """
    #inside = -81.8 45.1
    #outsite= -81.0 44.9
    polygon = ("POLYGON ((-82.0 45.0, -82.0 45.2, -81.6 45.2, " +
               "-81.6 45.0, -82.0 45.0))")

    return polygon


@pytest.mark.django_db
def test_status_and_template(client, db_setup):
    """Verify that the url returns an appropriate status code and that the
    template is the one we think it is.

    """


    url = reverse('find_events')
    response = client.get(url)
    content = str(response.content)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/find_events_gis.html' in templates


@pytest.mark.django_db
def test_find_events_contain_basic_elements(client, db_setup):
    """ A get request to "find_events" should return response that contains:
    - expanitory title "Find Stocking Events"
    - "earliest year" - with default place holder earliest stocking event
    - "latest year" - with default place holder most recent stocking event
    - submit button
    - reset button
    """

    url = reverse('find_events')
    response = client.get(url)
    content = str(response.content)

    assert "Find Stocking Events" in content
    assert 'placeholder="2000"' in content #year of earliest event
    assert 'placeholder="2010"' in content #year of lastest event
    assert "Submit" in content
    assert "Reset" in content




@pytest.mark.django_db
def test_find_events_contain_species_list(client, db_setup):
    """ A get request to "find_events" should return response that contains:
    - list of species
    """

    url = reverse('find_events')
    response = client.get(url)
    content = str(response.content)

    assert "Select Species" in content
    assert "Lake Trout" in content
    assert "(Salvelinus namaycush)" in content

    assert "Brown Trout" in content
    assert "(Salmo trutta)" in content

    assert "Coho Salmon" in content
    assert "(Oncorhynchus kisutch)" in content


@pytest.mark.django_db
def test_find_events_contain_year_inputs(client, db_setup):
    """ A get request to "find_events" should return response that contains:
    - "earliest year" - with default place holder earliest stocking event
    - "latest year" - with default place holder most recent stocking event
    """

    url = reverse('find_events')
    response = client.get(url)
    content = str(response.content)

    assert "Earliest Year:" in content
    assert "Latest Year:" in content


@pytest.mark.django_db
def test_find_events_post_without_selection(client, db_setup):
    """If we submit a post request without providing a roi, the form
    should return with a meaningful message.
    """

    url = reverse('find_events')
    response = client.post(url)
    content = str(response.content)

    assert "No geometry value provided." in content


@pytest.mark.django_db
def test_find_events_post_without_any_events(client, db_setup):
    """If we submit a post request providing a roi that does not contains
    any stocking events, the response should contain a meaningful
    message:'Sorry no events match that criteria.'

    """

    #our normal roi, just shifted to the west by one degree:
    roi = ("POLYGON ((-83.0 45.0, -83.0 45.2, -82.6 45.2, " +
               "-82.6 45.0, -83.0 45.0))")
    data = {'selection':roi}
    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "Sorry no events match that criteria." in content


@pytest.mark.django_db
def test_find_events_post_first_year_after_last_year(client, db_setup, roi):
    """If we submit a post request without providing a roi, the form
    should return with a meaningful message.
    """

    data = {'selection':roi, 'earliest': 2010,  'latest': 2005}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    err_msg =  "&#39;Earliest Year&#39; occurs after &#39;Last Year&#39;."
    assert err_msg in content


@pytest.mark.django_db
def test_find_events_post_nonnumeric_earliest_year(client, db_setup, roi):
    """If we submit a post request without with an earliest year value
    that cannot be converted to a number the form should return with a
    meaningful message.

    """

    data = {'selection':roi, 'earliest': 'foo'}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "&#39;Earliest Year&#39; must be numeric." in content


@pytest.mark.django_db
def test_find_events_post_nonnumeric_latest_year(client, db_setup, roi):
    """If we submit a post request without with an latest year value
    that cannot be converted to a number the form should return with a
    meaningful message.

    """

    data = {'selection':roi, 'latest': 'foo'}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "&#39;Latest Year&#39; must be numeric." in content


@pytest.mark.django_db
def test_find_events_post_invalid_roi(client, db_setup):
    """If we submit a post request with a geometry that is not a valid
    polygon, an error should be thrown.  """

    data = {'selection':Point(-82.0, 45.0)}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "Invalid geometry value." in content


#==================================
@pytest.mark.django_db
def test_find_events_post_valid_data(client, db_setup, roi):
    """If we submit a post request with a valid roi and the rest of the
    controls blank, we should be taken a view that uses the template
    show_events_gis.html and contains a table of stocking events.

    """

    data = {'selection':roi}

    url = reverse('find_events')
    response = client.post(url, data)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/show_events_gis.html' in templates

    content = str(response.content)

    #confirm that the table heading are there too:
    assert '<td>FSIS Event</td>' in content
    assert '<td>Species</td>' in content
    assert '<td>Strain</td>' in content
    assert '<td>Number Stocked</td>' in content
    assert '<td>Event Date</td>' in content
    assert '<td>Site Name</td>' in content
    assert '<td>Clip Applied</td>' in content
    assert '<td>Development Stage</td>' in content




@pytest.mark.django_db
def test_find_events_post_valid_species(client, db_setup, roi):
    """If we submit a post request with a valid roi and species selected
    as brown trout, we should get only three stocking events.
    Inside SiteA should not appear in the results, nor should any of
    the outevent events - they were all stocked outside of the region of
    interest.

    """

    spc = Species.objects.get(common_name='Brown Trout')
    data = {'selection':roi, 'species': (spc.id,)}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "3 events found." in content
    assert 'Inside SiteB' in content
    assert 'Inside SiteC' in content
    assert 'Inside SiteD' in content

    assert 'Outside Event' not in content
    assert 'Inside SiteA' not in content #rainbow stocking



@pytest.mark.django_db
def test_find_events_post_valid_earliest_year(client, db_setup, roi):
    """If we submit a post request with a valid roi and speciy an earliest
    year (2004) we should get only three stocking events.  Inside
    EventB (stocked in 2001) should not appear in the results.

    """

    data = {'selection':roi, 'earliest':'2004'}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "3 events found." in content
    assert 'Inside SiteA' in content
    assert 'Inside SiteC' in content
    assert 'Inside SiteD' in content

    assert 'Outside Site' not in content
    assert 'Inside SiteB' not in content #brown trout stocking in 2000



@pytest.mark.django_db
def test_find_events_post_valid_latest_year(client, db_setup, roi):
    """If we submit a post request with a valid roi and speciy an latest
    year (2006) we should get only three stocking events.  The events
    associated with 'Inside SiteD'' (stocked in 2010) should not appear in
    the results.

    """
    data = {'selection':roi, 'latest':'2006'}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "3 events found." in content
    assert 'Inside SiteA' in content
    assert 'Inside SiteB' in content
    assert 'Inside SiteC' in content

    assert 'Outside Site' not in content
    assert 'Inside SiteD' not in content   #brown trout stocking in 2010


@pytest.mark.django_db
def test_find_events_post_valid_between_years(client, db_setup, roi):
    """If we submit a post request with a valid roi and speciy both and
    early (2004) and a late year (2006) we should get only two
    stocking events.  The events associated wth "Inside SiteA" and
    "Inside SiteD" (stocked in 2001 and 2010) should not appear in the
    results.

    """

    data = {'selection':roi, 'earliest': '2004', 'latest':'2006'}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "2 events found." in content
    assert 'Inside SiteA' in content
    assert 'Inside SiteC' in content

    assert 'Outside Site' not in content
    assert 'Inside SiteB' not in content   #brown trout stocking in 2000
    assert 'Inside SiteD' not in content   #brown trout stocking in 2010




@pytest.mark.django_db
def test_find_events_post_valid_earliest_latest_same(client, db_setup, roi):
    """If we submit a post request with a valid roi and speciy both and
    early (2005) and a late year (2005) we should get only two
    stocking locations.  Event associated with "Inside SiteA" and
    "Inside SiteD" (stocked in 2001 and 2010) should not appear in the
    results.

    """

    data = {'selection':roi, 'earliest': '2004', 'latest':'2006'}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "2 events found." in content
    assert 'Inside SiteA' in content
    assert 'Inside SiteC' in content

    assert 'Outside Site' not in content
    assert 'Inside SiteB' not in content   #brown trout stocking in 2000
    assert 'Inside SiteD' not in content   #brown trout stocking in 2010



@pytest.mark.django_db
def test_find_events_post_several_species(client, db_setup, roi):
    """If we submit a post request with more than one species, the events
    associated with that species should be returned.

    """


    spc1 = Species.objects.get(common_name='Brown Trout')
    spc2 = Species.objects.get(common_name='Rainbow Trout')

    data = {'selection':roi, 'species': (spc1.id, spc2.id),
            'earliest': '2004', 'latest':'2006'}

    url = reverse('find_events')
    response = client.post(url, data)
    content = str(response.content)

    assert "2 events found." in content
    assert 'Inside SiteA' in content
    assert 'Inside SiteC' in content
    assert 'Brown Trout' in content
    assert 'Rainbow Trout' in content

    assert 'Outside Event' not in content
    assert 'Inside SiteB' not in content
    assert 'Inside SiteD' not in content
