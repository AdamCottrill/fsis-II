'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_species_list.py
Created: 01 Dec 2015 10:54:29


DESCRIPTION:

The tests in this script verfy that the views assoicated with species
list render as expected.  Views tested in this script are currently
limited to species_list.

Proponent/Hatchery List
- uses 'fsis2/hatchery_list.html'
- contains
  - Fish Hatcheries/Proponents
  - a quick search box containing 'Filter by Name or Abbrev.'
  - list of hatcheries
  - club's abbreviation
  - first year and last year of activity for each club


- is should not contain information about species in the database that
  have not been stocked (ie - cwts deployed by other agencies) - it
  should not throw an error if species that have been stocked are in
  the species table.


A. Cottrill
=============================================================

'''


import pytest
from django.core.urlresolvers import reverse

from fsis2.tests.factories import *


@pytest.fixture(scope='function')
def db_setup(db):
    """For the tests in this file, we will need three different species,
    and several events spread over several years.
    """

    BuildDateFactory.create()
    ReadmeFactory.create()

    laketrout = SpeciesFactory(species_code=81,
                               common_name = 'Lake Trout',
                               scientific_name = 'Salvelinus nameychush')

    #we need to specify strains to keep FactoryBoy from creating more species
    #(seems like a factory boy bug to me)

    hatchery_laketrout = StrainFactory(species = laketrout,
                           strain_name = "hatchery")

    hatchery1 = ProponentFactory(abbrev='ABC',
                                 proponent_name='ABC Fishin Club')

    hatchery2 = ProponentFactory(abbrev='OFG',
                                 proponent_name='Old Fishin Geezers')

    #the springfield fishin club didn't actaully stock anything
    hatchery3 = ProponentFactory(abbrev='SFC',
                                 proponent_name='Springfield Fishin Club')

    #now create our lots using our species and strains
    laketrout_lot1 = LotFactory(species=laketrout,strain=hatchery_laketrout,
                                proponent=hatchery1, spawn_year=2000)

    laketrout_lot2 = LotFactory(species=laketrout,strain=hatchery_laketrout,
                                proponent=hatchery2, spawn_year=2000)

    #ABC Fishin club only stocked one year
    stocking_date = datetime(2010,10,15)
    event1 = EventFactory(lot=laketrout_lot1,
                          event_date=stocking_date)

    #The old Fishin' Geezers stocked for several
    stocking_date = datetime(2001,10,15)
    event2 = EventFactory(lot=laketrout_lot2,
                          event_date=stocking_date)

    stocking_date = datetime(2011,10,15)
    event3 = EventFactory(lot=laketrout_lot2,
                          event_date=stocking_date)


@pytest.mark.django_db
def test_proponent_list_status_and_template(client, db_setup):
    """verify that the species list url returns a status code of 200 and uses
    the template we think it does
    """

    url = reverse('hatchery_list')
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/ProponentList.html' in templates


@pytest.mark.django_db
def test_hatchery_list_contains_common_names(client, db_setup):
    """Verify that the reponse contains the name of each club
    that has stocked fish (and does contain the name of clubs
    that did not stock)
    """
    url = reverse('hatchery_list')
    response = client.get(url)

    content = str(response.content)
    assert 'ABC Fishin Club' in content
    assert 'Old Fishin Geezers' in content
    assert 'Springfield Fishin Club' not in content


@pytest.mark.django_db
def test_hatchery_list_contains_club_abbreviations(client, db_setup):
    """Verify that the reponse contains the abbreviation for each club
    that has stocked fish (and does contain the abbreviation of clubs
    that did not stock)
    """

    url = reverse('hatchery_list')
    response = client.get(url)

    content = str(response.content)

    assert 'ABC' in content
    assert 'OFG' in content
    assert 'SFC' not in content


@pytest.mark.django_db
def test_hatchery_list_contains_first_and_last_years(client, db_setup):
    """Verify that the reponse contains the first and last year stocked
    for by each proponent.
    """

    url = reverse('hatchery_list')
    response = client.get(url)

    content = str(response.content)
    assert '[2010]' in content
    assert '[2010-2010]' not in content
    assert '[2001-2011]' in content


@pytest.mark.django_db
def test_proponent_contains_quick_search(client, db_setup):
    """the page rendered by the proponent list view should include a quick
    search form, and that form should contain the message 'Filter by
    Name or Abbrev.'.
    """

    url = reverse('hatchery_list')
    response = client.get(url)

    content = str(response.content)
    assert 'Filter by Name or Abbrev.' in content


@pytest.mark.django_db
def test_proponent_quick_seach_name_contains(client, db_setup):
    """The when part of a club name is entered in the quick search, only
    the matching club(s) should be in the response.
    """
    q = 'Geezers'
    url = reverse('hatchery_list')
    response = client.get(url, {'q': q})

    content = str(response.content)
    assert 'ABC Fishin Club' not in content
    assert 'Old Fishin Geezers' in content
    assert 'Springfield Fishin Club' not in content
    assert 'Sorry no hatcheries match that criteria' not in content


@pytest.mark.django_db
def test_proponent_quick_seach_abbrev_contains(client, db_setup):
    """The when part of a club abbreviation is entered in the quick search, only
    the matching club(s) should be in the response.
    """
    q = 'ABC'
    url = reverse('hatchery_list')
    response = client.get(url, {'q': q})

    content = str(response.content)
    assert 'ABC Fishin Club' in content
    assert 'Old Fishin Geezers' not in content
    assert 'Springfield Fishin Club' not in content
    assert 'Sorry no hatcheries match that criteria' not in content


@pytest.mark.django_db
def test_proponent_quick_seach_lowercase_abbrev_contains(client, db_setup):
    """The when part of a club abbreviation is entered in the quick search
    as lowercase text, only the matching club(s) should be in the
    response.

    """
    q = 'abc'
    url = reverse('hatchery_list')
    response = client.get(url, {'q': q})

    content = str(response.content)
    assert 'ABC Fishin Club' in content
    assert 'Old Fishin Geezers' not in content
    assert 'Springfield Fishin Club' not in content
    assert 'Sorry no hatcheries match that criteria' not in content


@pytest.mark.django_db
def test_proponent_quick_seach_no_match(client, db_setup):
    """If we search for a string that does not match any club name or
    abbreviation, we should get a meaningful message to that effect.

    """
    q = 'foobarbaz'
    url = reverse('hatchery_list')
    response = client.get(url, {'q': q})

    content = str(response.content)
    assert 'ABC Fishin Club' not in content
    assert 'Old Fishin Geezers' not in content
    assert 'Springfield Fishin Club' not in content

    assert 'Sorry no hatcheries match that criteria' in content
