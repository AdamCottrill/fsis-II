'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_species_list.py
Created: 01 Dec 2015 10:54:29


DESCRIPTION:

The tests in this script verfy that the views assoicated with species
list render as expected.  Views tested in this script are currently
limited to species_list.

Species List
- uses 'fsis2/species_list.html'
- contains
  - Lake Name (Lake Huron)
  - list of species that have been stocked
  - common names
  - scientific names
  - first year stocked
  - last year stocked

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


@pytest.fixture(scope='class')
def db_setup():
    """For the tests in this file, we will need three different species,
    and several events spread over several years.
    """

    BuildDateFactory.create()
    ReadmeFactory.create()

    laketrout = SpeciesFactory(species_code=81,
                               common_name = 'Lake Trout',
                               scientific_name = 'Salvelinus nameychush')

    rainbow = SpeciesFactory(common_name='Rainbow Trout',
                             scientific_name = 'Oncorhynchus mykiss',
                             species_code=76)

    coho = SpeciesFactory.create(common_name='Coho Salmon',
                                 scientific_name = 'Oncorhynchus kisutch',
                                 species_code=75)

    #we need to specify strains to keep FactoryBoy from creating more species
    #(seems like a factory boy bug to me)
    wild_rainbow = StrainFactory(species = rainbow,
                           strain_name = "wild")

    hatchery_laketrout = StrainFactory(species = laketrout,
                           strain_name = "hatchery")

    #now create out lots using our species and strains
    laketrout_lot = LotFactory(species=laketrout,strain=hatchery_laketrout,
                             spawn_year=2010)

    rainbow_lot1 = LotFactory(species=rainbow, strain=wild_rainbow,
                              spawn_year=2001)

    rainbow_lot2 = LotFactory(species=rainbow, strain=wild_rainbow,
                              spawn_year=2011)

    #EVENTS
    stocking_date = datetime(2010,10,15)
    event1 = EventFactory(lot=laketrout_lot, #year=2010,
                          event_date=stocking_date)
    event2 = EventFactory(lot=laketrout_lot, #year=2010,
                          event_date=stocking_date)
    event3 = EventFactory(lot=laketrout_lot, #year=2010,
                          event_date=stocking_date)

    #Rainbow1 Stocking Events
    stocking_date = datetime(2001,10,15)
    event4 = EventFactory(lot=rainbow_lot1, #year=2001,
                          event_date=stocking_date)

    event5 = EventFactory(lot=rainbow_lot1, #year=2001,
                          event_date=stocking_date)

    #Rainbow-2 Stocking Events
    stocking_date = datetime(2011,10,15)
    event6 = EventFactory(lot=rainbow_lot2, #year=2011,
                          event_date=stocking_date)

    event6 = EventFactory(lot=rainbow_lot2,# year=2011,
                          event_date=stocking_date)


@pytest.mark.django_db
def test_species_list_status_and_template(client, db_setup):
    """verify that the species list url returns a status code of 200 and uses
    the template we think it does
    """

    url = reverse('species_list')
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/SpeciesList.html' in templates


@pytest.mark.django_db
def test_species_list_contains_common_names(client, db_setup):
    """Verify that the reponse contains the common names of the species stocked
    """
    url = reverse('species_list')
    response = client.get(url)

    content = str(response.content)
    assert "Lake Trout" in content
    assert "Rainbow Trout" in content
    assert "Coho Salmon" not in content


@pytest.mark.django_db
def test_species_list_contains_scientific_names(client, db_setup):
    """Verify that the reponse contains the scientific names of the
    species stocked.
    """

    url = reverse('species_list')
    response = client.get(url)

    content = str(response.content)
    assert 'Salvelinus nameychush' in content
    assert 'Oncorhynchus mykiss' in content
    assert 'Oncorhynchus kisutch' not in content




@pytest.mark.django_db
def test_species_list_contains_first_and_last_years(client, db_setup):
    """Verify that the reponse contains the first and last year stocked
    for each species.
    """

    url = reverse('species_list')
    response = client.get(url)

    content = str(response.content)
    assert '[2010]' in content
    assert '[2010-2010]' not in content
    assert '[2001-2011]' in content
