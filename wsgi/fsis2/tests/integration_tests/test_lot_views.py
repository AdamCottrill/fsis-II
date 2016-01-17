'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_lot_views.py
Created: 06 Oct 2015 13:29:50


DESCRIPTION:

The tests in this script verfy that the views assoicated with lots
render as expected.  Views tested in this script include lot list, lot
detail and find_lot using complete and partial lot numbers.

Lot List
- uses 'fsis2/lot_detail.html'
- contains
  - list of lots in the database
  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name (and acronym)
  - Find Lot quick search

Lot List <Year>
- same as Lot List but only for lots stocked in a given year are returned
- NOT IMPLEMTNED

Find Lot Partial
- uses 'fsis2/lot_detail.html'
- contains
  - list of lots in the database that partially match criteria
  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name(and acronym)
  - Find Lot quick search
- if no lots match the criteria, an appropriate message should appear


Find Lot Complete
- uses 'fsis2/lot_detail.html'
- contains
  - list of lots in the database that match criteria perfectly.
    Partial Matches should be excluded.
  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name (and acronym)
  - Find Lot quick search
- if no lots match the criteria, an appropriate message should appear


Lot Detail
- uses 'fsis2/lot_detail.html'
- contains
  - lot id
  - species names
  - proponent
  - spawn year
  - a map of associated stocking events
  - a table of associated stocking events
- if no lots match the id, an appropriate message should appear


A. Cottrill
=============================================================

'''


import pytest
from django.core.urlresolvers import reverse

from fsis2.tests.factories import *



@pytest.fixture(scope='class')
def db_setup():
    """For the tests in this file, we will need three different species,
    two different hatcheries, and several events.

    """

    BuildDateFactory.create()
    ReadmeFactory.create()

    laketrout = SpeciesFactory.create(species_code=81)
    rainbow = SpeciesFactory.create(common_name='Rainbow Trout',
                                    species_code=76)

    chinook = SpeciesFactory.create(common_name='Chinook Salmon',
                                    species_code=75)

    hatchery1 = ProponentFactory(abbrev='ABC',
                                 proponent_name='ABC Fishin Club')

    hatchery2 = ProponentFactory(abbrev='OFG',
                                 proponent_name='Old Fishin Geezers')

    chinook_lot = LotFactory(species=chinook,
                             spawn_year=2010,
                             proponent=hatchery1,
                             fs_lot=7575)

    rainbow_lot = LotFactory(species=rainbow,
                             spawn_year=2011,
                             proponent=hatchery1,
                             fs_lot=7576)

    laketrout_lot = LotFactory(species=laketrout,
                             spawn_year=2009,
                             proponent=hatchery2,
                             fs_lot=8181)

    site1 = StockingSiteFactory(site_name='Site1')
    site2 = StockingSiteFactory(site_name='Site2')
    site3 = StockingSiteFactory(site_name='Site3')
    site4 = StockingSiteFactory(site_name='Site4')
    site5 = StockingSiteFactory(site_name='Site5')

    stocking_date = datetime(2010,10,15)
    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(site=site1, lot=chinook_lot,
                          event_date=stocking_date)
    event2 = EventFactory(site=site2, lot=chinook_lot,
                          event_date=stocking_date)
    event3 = EventFactory(site=site3, lot=chinook_lot,
                          event_date=stocking_date)


    event4 = EventFactory(site=site4, lot=rainbow_lot,
                          event_date=stocking_date)

    event5 = EventFactory(site=site5, lot=laketrout_lot,
                          event_date=stocking_date)



@pytest.mark.django_db
def test_lot_list_status_and_template(client, db_setup):
    """verify that the lot list url returns a status code of 200 and uses
    the template we think it does

    """

    url = reverse('lot_list')
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/lot_list.html' in templates


@pytest.mark.django_db
def test_lot_list_contains_quick_search(client, db_setup):
    """the lot list should contain an input box allowing the user to
    quickly find lot by FSIS Lot id.

    """

    url = reverse('lot_list')
    response = client.get(url)
    content = str(response.content)

    assert '<input type="text" class="form-control" name="lot"' in content
    assert 'placeholder="Find FSIS Lot">' in content


@pytest.mark.django_db
def test_lot_list_contains_expected_data(client, db_setup):
    """verify that the lot list url returns a status code of 200 and uses
    the template we think it does

  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name (and acronym)


    """

    url = reverse('lot_list')
    response = client.get(url)
    content = str(response.content)

    lotids = ['7575', '7576', '8181']
    for lotid in lotids:
        assert lotid in content

    spawn_years = ['2009', '2010', '2011']
    for yr in spawn_years:
        assert yr in content

    print(content)

    assert 'Abc Fishin Club (ABC)' in content
    assert 'Old Fishin Geezers (OFG)' in content
    assert 'Chinook Salmon' in content
    assert 'Rainbow Trout' in content
    assert 'Lake Trout' in content


@pytest.mark.django_db
def test_lot_list_contains_expected_data_partial(client, db_setup):
    """verify that the lot list url returns records for the lots that
    partially match the pattern and does not contain information
    assoicated with lots/records that we know do not match.

  - the list should contain basic infomation such as:
    + spawn year,
    + species,
    + strain and
    + proponent name (and acronym)

    """

    url = reverse('lot_list')
    response = client.get(url,{'lot':'75'})
    content = str(response.content)

    lotids = ['7575', '7576']
    for lotid in lotids:
        assert lotid in content

    spawn_years = ['2010', '2011']
    for yr in spawn_years:
        assert yr in content

    assert 'Abc Fishin Club (ABC)' in content
    assert 'Chinook Salmon' in content
    assert 'Rainbow Trout' in content

    assert '2009' not in content
    assert '8181' not in content
    assert 'Old Fishin Geezers (OFG)' not in content
    assert 'Lake Trout' not in content


@pytest.mark.django_db
def test_lot_list_partial_no_match(client, db_setup):
    """If the partial lot id submitted does not match any lot in the
    database, an appropriate message should be thrown. 'No records match
    that criteria'

    """

    url = reverse('lot_list')
    response = client.get(url,{'lot':'999'})
    content = str(response.content)

    msg = "Sorry no lots match that criteria."
    assert msg in content



@pytest.mark.django_db
def test_lot_detail_status_and_template(client, db_setup):
    """verify that the lot detail url returns a status code of 200 and uses
    the template we think it does

    """

    proponent = Proponent.objects.get(abbrev='ABC')
    species = Species.objects.get(species_code=75)

    lot = Lot.objects.get(proponent=proponent, species=species)

    url = reverse('lot_detail', kwargs={'pk':lot.id})
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/lot_detail.html' in templates




@pytest.mark.django_db
def test_lot_detail_expected_content(client, db_setup):
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

    proponent = Proponent.objects.get(abbrev='ABC')
    species = Species.objects.get(species_code=75)

    lot = Lot.objects.get(proponent=proponent, species=species)

    url = reverse('lot_detail', kwargs={'pk':lot.id})
    response = client.get(url)

    content = str(response.content)

    assert species.common_name in content
    assert species.scientific_name in content
    assert str(lot.spawn_year) in content
    assert lot.fs_lot in content
    assert lot.strain.strain_name in content

    assert 'Rainbow Trout' not in content
    assert 'Lake Trout' not in content


@pytest.mark.django_db
def test_lot_detail_no_matching_id(client, db_setup):
    """ If the lot id submitted does not match any lot in the database, an
    appropriate message should be thrown. 'No records match that
    criteria'
    """

    url = reverse('lot_detail', kwargs={'pk':'54321'})
    response = client.get(url)
    assert response.status_code == 404

    #content = str(response.content)
    #assert 'Lot with id 54321 does not exist.' in content
