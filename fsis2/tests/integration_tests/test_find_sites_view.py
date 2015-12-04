'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_find_sites_view.py
Created: 30 Sep 2015 07:26:10

DESCRIPTION:

This script ensures that the view to find sites contains all of the
elements we think it should and that the view functions as expected
when we submit a region of interest.

Specifically, a get request to the url should return a response that contains:

GET Request should contain:
- expanitory title "Find Stocking Sites"
- earliest year - with default place holder earliest stocking event
- latest year - with default place holder most recent stocking event
- list of species
- submit button
- reset button


POST Requests:

No species Specified
should return information about the stocking sites that fall within the roi
- only sites within the roi should be returned
- the number of sites found
  + information returned about each site should include:
    + site name
    + basin
    + grid
    + ddlat
    + ddlon
    + number of stocking events (that match species and year criteria)

- sites outside the roi should not be in the response

- if no sites are in the roi, an appropriate error message should be
  returned.

- if no roi is provided, a message should be displayed and form re-rendered.

- if the geometry is invalid, the form should report an appropriate
  message

- if the years are not valid years - the form should report an
  appropriate message


Several species specifed

#NOT YET IMPLEMENTED:
Eariest year specified
latest year specified
ealiest and latest year specified
No year specifed


A. Cottrill
=============================================================

'''

import pytest
from django.contrib.gis.geos import GEOSGeometry, LinearRing, Point, Polygon
from django.core.urlresolvers import reverse

from fsis2.tests.factories import *



@pytest.fixture(scope='class')
def db_setup():
    """For the tests in this file, we will need three different species,
    and several events.

    one species will not be stocked at all, but should be included in
    the list of available species

    the events need to be occur over several years and be both inside
    and outside of the ROI.

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

    laker_lot = LotFactory(species=lake_trout)
    brown_lot = LotFactory(species=brown_trout)
    coho_lot = LotFactory(species=coho)
    rainbow_lot = LotFactory(species=rainbow_trout)

    outside = StockingSiteFactory(site_name='Outside Site',
                                  geom=GEOSGeometry('POINT(-81.0 44.9)'))
    inside = StockingSiteFactory(site_name='Inside Site',
                                  geom=GEOSGeometry('POINT(-81.8 45.1)'))

    date_2000 = datetime(2000,10,15)
    date_2005 = datetime(2005,10,15)
    date_2010 = datetime(2010,10,15)

    event1 = EventFactory(lot=laker_lot, site=outside, event_date=date_2000)
    event2 = EventFactory(lot=laker_lot, site=outside, event_date=date_2005)
    event3 = EventFactory(lot=laker_lot, site=outside, event_date=date_2010)

    event4 = EventFactory(lot=rainbow_lot, site=outside, event_date=date_2005)

    event5 = EventFactory(lot=brown_lot, site=inside, event_date=date_2000)
    event6 = EventFactory(lot=brown_lot, site=inside, event_date=date_2005)
    event7 = EventFactory(lot=brown_lot, site=inside, event_date=date_2010)


@pytest.fixture(scope='class')
def roi():
    """A fixture to return a region of interest polygon.  The Stocking
    Site 'Inside' is in the middle of this roi.

    """
    #inside = -81.8 45.1
    #outsite= -81.0 44.9
    polygon = ("POLYGON ((-82.0 45.0, -82.0 45.2, -81.6 45.2, " +
               "-81.6 45.0, -82.0 45.0))")

    #polygon = Polygon(((-82.0, 45.0), (-82.0, 45.2), (-81.6, 45.2), (-81.6, 45.0), (-82.0, 45.0)))

    return polygon


@pytest.mark.django_db
def test_status_and_template(client, db_setup):
    """Verify that the url returns an appropriate status code and that the
    template is the one we think it is.

    """

    url = reverse('find_sites')
    response = client.get(url)
    content = str(response.content)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/find_events_gis.html' in templates


@pytest.mark.django_db
def test_find_sites_contain_basic_elements(client, db_setup):
    """ A get request to "find_sites" should return response that contains:
    - expanitory title "Find Stocking Sites"
    - "earliest year" - with default place holder earliest stocking event
    - "latest year" - with default place holder most recent stocking event
    - submit button
    - reset button
    """

    url = reverse('find_sites')
    response = client.get(url)
    content = str(response.content)

    assert "Find Stocking Sites" in content
    assert "Submit" in content
    assert "Reset" in content


@pytest.mark.django_db
def test_find_sites_contain_species_list(client, db_setup):
    """ A get request to "find_sites" should return response that contains:
    - list of species
    """

    url = reverse('find_sites')
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
def test_find_sites_contain_year_inputs(client, db_setup):
    """ A get request to "find_sites" should return response that contains:
    - "earliest year" - with default place holder earliest stocking event
    - "latest year" - with default place holder most recent stocking event
    """

    url = reverse('find_sites')
    response = client.get(url)
    content = str(response.content)

    assert "Earliest Year:" in content
    assert "Latest Year:" in content


@pytest.mark.django_db
def test_find_post_without_selection(client, db_setup):
    """If we submit a post request without providing a roi, the form
    should return with a meaningful message.
    """

    url = reverse('find_sites')
    response = client.post(url)
    content = str(response.content)

    assert "No geometry value provided." in content


@pytest.mark.django_db
def test_find_post_first_year_after_last_year(client, db_setup, roi):
    """If we submit a post request without providing a roi, the form
    should return with a meaningful message.
    """

    data = {'selection':roi, 'earliest': 2010,  'latest': 2005}

    url = reverse('find_sites')
    response = client.post(url, data)
    content = str(response.content)

    print('content={}'.format(content))
    err_msg =  "&#39;Earliest Year&#39; occurs after &#39;Last Year&#39;."
    assert err_msg in content



@pytest.mark.django_db
def test_find_post_nonnumeric_earliest_year(client, db_setup, roi):
    """If we submit a post request without with an earliest year value
    that cannot be converted to a number the form should return with a
    meaningful message.

    """

    data = {'selection':roi, 'earliest': 'foo'}

    url = reverse('find_sites')
    response = client.post(url, data)
    content = str(response.content)

    assert "&#39;Earliest Year&#39; must be numeric." in content

@pytest.mark.django_db
def test_find_post_nonnumeric_latest_year(client, db_setup, roi):
    """If we submit a post request without with an latest year value
    that cannot be converted to a number the form should return with a
    meaningful message.

    """

    data = {'selection':roi, 'latest': 'foo'}

    url = reverse('find_sites')
    response = client.post(url, data)
    content = str(response.content)

    assert "&#39;Latest Year&#39; must be numeric." in content


@pytest.mark.django_db
def test_find_post_invalid_roi(client, db_setup):
    """If we submit a post request with a geometry that is not a valid
    polygon, an error should be thrown.  """

    data = {'selection':Point(-82.0, 45.0)}

    url = reverse('find_sites')
    response = client.post(url, data)
    content = str(response.content)

    assert "Invalid geometry value." in content



#==================================
@pytest.mark.django_db
def test_find_post_valid_data(client, db_setup, roi):
    """If we submit a post request with a valid roi and the rest of the
    controls blank, we should be take a view that uses the temlate
    show_sites_gis.html

    """

    data = {'selection':roi}

    url = reverse('find_sites')
    response = client.post(url, data)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/show_sites_gis.html' in templates

    content = str(response.content)

    assert "3 sites found."
    assert 'Inside Site' in content

    assert 'Outside Site' not in content

    #confirm that the table heading are there too:
    assert '<td>FSIS Site ID</td>' in content
    assert '<td>Site Name</td>' in content
    assert '<td>Basin</td>' in content
    assert '<td>Grid</td>' in content
    assert '<td>Latitude</td>' in content
    assert '<td>Longitude</td>' in content
    assert '<td>N</td>' in content


@pytest.mark.django_db
def test_find_post_valid_data(client, db_setup, roi):
    """If we submit a post request with a valid roi and the rest of the
    controls blank, we should be take a view that uses the temlate
    show_sites_gis.html

    """

    data = {'selection':roi}

    url = reverse('find_sites')
    response = client.post(url, data)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/show_sites_gis.html' in templates

    content = str(response.content)

    assert "1 site found."
    assert 'Inside Site' in content

    assert 'Outside Site' not in content

    #confirm that the table heading are there too:
    assert '<td>FSIS Site ID</td>' in content
    assert '<td>Site Name</td>' in content
    assert '<td>Basin</td>' in content
    assert '<td>Grid</td>' in content
    assert '<td>Latitude</td>' in content
    assert '<td>Longitude</td>' in content
    assert '<td>N</td>' in content
