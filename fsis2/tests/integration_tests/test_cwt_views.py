'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/tests/integration_tests/test_cwt_views.py
Created: 08 Oct 2015 08:58:45


DESCRIPTION:

The tests in this script verfy that the views assoicated with cwts
render as expected.  Views tested in this script include cwt list and
find_cwt using complete and partial cwt numbers.  The cwt_detail views
are tested in a dedicated script (for now)

cwt List
- uses 'fsis2/cwt_list.html'
- contains
  - list of cwts in the cwts_cwt table - cwts that have been deployed.
  - the list should contain basic infomation such as:
    + year class,
    + cwt number
    + species,
    + strain
    + lifestage
    + stocking location
    + agency
  - Find Lot quick search

Find Lot Partial
- uses 'fsis2/cwt_list.html'
- contains
  - list of cwts in the database that partially match criteria
  - the list should contain basic infomation such as:
    + year class,
    + cwt number
    + species,
    + strain
    + lifestage
    + stocking location
    + agency

- if no cwts match the criteria, an appropriate message should appear


Lot Detail
- see fsis2/tests/test_cwt_detail_view.py


CWT Detail
- uses 'fsis2/cwt_detail.html'
- the cwt detail page should contain
    + year class,
    + cwt number
    + species,
    + strain
    + lifestage
    + stocking location
    + agency
    + tag count
    + hatchery
    + tag manufacturer
    + tag type
    + Sequence range (conditional on tag type)
    + tag Re-use
    + comment
- also age-at-capture matrix (available and not available)

- Warnings:
  - more than one location
  - more than one species
  - more than one year class
  - more than one strain

- US TAGS (no stocking records expected)
  - with recaps
  - without any recaps

- ONTARIO TAGS
  - with recaps
  - stocked without any recaps
  - not stocked but with recaps
  - not stocked with recaps



A. Cottrill
=============================================================

'''


import pytest
from django.core.urlresolvers import reverse

from cwts.models import CWT

from fsis2.tests.factories import *
from cwts.tests.factories import *


@pytest.fixture(scope='function')
def db_setup(db):
    """For the tests in this file, we will need three different species,
    two different hatcheries, and several events.

    """

    BuildDateFactory.create()
    ReadmeFactory.create()

    rainbows = SpeciesFactory(common_name='Rainbow Trout')
    browns = SpeciesFactory(common_name='Brown Trout')

    strain_nm = 'Domestic'
    rainbow_strain = StrainFactory(strain_name=strain_nm, species=rainbows)
    brown_strain = StrainFactory(strain_name=strain_nm, species=browns)


    #this is a sequential tag that has never been stocked. Used to
    #verify that Sequence range is included in response and that an
    #warning message is rendered that no stocking events are available
    #but should be.
    cwt0 = CWTFactory(cwt='123456',
                      spc=rainbows,
                      strain=strain_nm,
                      year_class = 1999,
                      stock_year=2000,
                      agency='OMNR',
                      plant_site='Sequential River',
                      tag_type=17

    )



    #Create a OMNR tag that is not recovered, but associated with two
    #stocking events
    cwt1 = CWTFactory(cwt='111111',
                      spc=rainbows,
                      strain=strain_nm,
                      year_class = 1999,
                      stock_year=2000,
                      agency='OMNR',
                      plant_site='Our Creek',
    )

    #stocking events associated with MNR tag not yet recovered
    rainbow_lot = LotFactory(species=rainbows)
    brown_lot = LotFactory(species=browns)
    site1 = StockingSiteFactory(site_name='Site1')

    stocking_date = datetime(2010,10,15)
    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(site=site1, lot=rainbow_lot,
                          stkcnt = 11111, fs_event = '998877',
                          event_date=stocking_date)

    event2 = EventFactory(site=site1, lot=rainbow_lot,
                          stkcnt = 22222, fs_event = '887766',
                          event_date=stocking_date)

    #now associated some tags with our stocking events
    tagging_event = TaggingEventFactory.create(stocking_event=event1)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=111111)
    tagging_event2 = TaggingEventFactory.create(stocking_event=event2)
    CWTsAppliedFactory.create(tagging_event=tagging_event2, cwt=111111)


    #USFWS Tag that is not recovered
    cwt2 = CWTFactory(cwt='222222',
                      spc=browns,
                      strain=strain_nm,
                      year_class = 1990,
                      stock_year=1991,
                      agency='USFWS',
                      plant_site='Their Creek',
    )



@pytest.fixture()
def us_tag_with_recoveries():
    """This fixture creates a us cwt and two associated recoveries.  US
    tags have no associated stocking events."""

    browns = Species.objects.get(common_name='Brown Trout')
    strain_nm = 'Domestic'

    #USFWS tag with some recoveries
    cwt3 = CWTFactory(cwt='333333',
                      spc=browns,
                      strain=strain_nm,
                      year_class = 1990,
                      stock_year=1991,
                      agency='USFWS',
                      plant_site='Their Creek',
    )

    recovery1 = CWT_RecoveryFactory(
        cwt = '333333',
        recovery_source = "Catch Sampling",
        recovery_year = 2012,
        recovery_date = date(2012, 11, 15),
        recovery_grid = "9999",
        composite_key = "Recovery-Key1",
        flen = 500,
        age = 6,
    )

    recovery2 = CWT_RecoveryFactory(
        cwt = '333333',
        recovery_source = "Creel",
        recovery_year = 2010,
        recovery_date = date(2010, 11, 15),
        recovery_grid = "8888",
        composite_key = "Recovery-Key2",
        flen = 400,
        age = 4,
    )


@pytest.fixture()
def omnr_tag_with_recoveries():
    """This fixtures creates an omnr cwt that is associated with two
    events, and has two recoveries.
    """
    #    #OMNR tag with recoveries
    rainbows = Species.objects.get(common_name='Rainbow Trout')
    strain_nm = 'Domestic'


    cwt11 = CWTFactory(cwt='112233',
                      spc=rainbows,
                      strain=strain_nm,
                      year_class = 1999,
                      stock_year=2000,
                      agency='OMNR',
                      plant_site='Our Creek',
    )


    rainbow_lot = Lot.objects.get(species__common_name='Rainbow Trout')
    site1=StockingSite.objects.get(site_name='Site1')

    stocking_date = datetime(2010,10,15)
    #we need an event for hatchery2 - it shouldn't appear in our tests
    event11 = EventFactory(site=site1, lot=rainbow_lot,
                          stkcnt = 11111, fs_event = '554433',
                          event_date=stocking_date)

    event21 = EventFactory(site=site1, lot=rainbow_lot,
                          stkcnt = 22222, fs_event = '443322',
                          event_date=stocking_date)

    #now associated some tags with our stocking events
    tagging_event = TaggingEventFactory.create(stocking_event=event11)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=111111)
    tagging_event2 = TaggingEventFactory.create(stocking_event=event21)
    CWTsAppliedFactory.create(tagging_event=tagging_event2, cwt=111111)



    recovery11 = CWT_RecoveryFactory(
        cwt = '112233',
        recovery_source = "Creel",
        recovery_year = 2012,
        recovery_date = date(2012, 11, 15),
        recovery_grid = "9999",
        composite_key = "Recovery-Key1",
        flen = 500,
        age = 6,
    )

    recovery21 = CWT_RecoveryFactory(
        cwt = '112233',
        recovery_source = "Index",
        recovery_year = 2010,
        recovery_date = date(2010, 11, 15),
        recovery_grid = "8888",
        composite_key = "Recovery-Key2",
        flen = 400,
        age = 4,
    )


@pytest.fixture()
def tag_in_two_species():
    """To test the warning mechanisms, we need a tag that was applied to
    two different species."""

    cwt = '445566'

    rainbows = Species.objects.get(common_name='Rainbow Trout')
    browns = Species.objects.get(common_name='Brown Trout')

    cwt1 = CWTFactory(cwt=cwt, spc=rainbows, )
    cwt2 = CWTFactory(cwt=cwt, spc=browns, )

    rainbow_lot = Lot.objects.get(species__common_name='Rainbow Trout')
    brown_lot = Lot.objects.get(species__common_name='Brown Trout')

    stocking_date = datetime(2010,10,15)
    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(lot=rainbow_lot)
    event2 = EventFactory(lot=brown_lot)

    #now associated some tags with our stocking events
    tagging_event = TaggingEventFactory.create(stocking_event=event1)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=cwt)

    tagging_event = TaggingEventFactory.create(stocking_event=event2)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=cwt)




@pytest.fixture()
def tag_in_two_strains():
    """To test the warning mechanisms, we need a tag that was applied to
    two different strains."""

    cwt = '445566'

    #get existing strain and species
    rainbows = Species.objects.get(common_name='Rainbow Trout')
    strain1 = Strain.objects.get(species=rainbows, strain_name='Domestic')

    #Make a new strain
    strain2 = StrainFactory(strain_name='Strain2')

    #get and existing lot of rainbow trout
    lot1 = Lot.objects.filter(species=rainbows).all()[0]
    #we need to create new for our second strain
    lot2 = LotFactory(species=rainbows, strain=strain2)

    cwt1 = CWTFactory(cwt=cwt, spc=rainbows, strain = strain1.strain_name)
    cwt2 = CWTFactory(cwt=cwt, spc=rainbows, strain=strain2.strain_name)

    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(lot=lot1)
    event2 = EventFactory(lot=lot2)

    #now associated some tags with our stocking events
    tagging_event = TaggingEventFactory.create(stocking_event=event1)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=cwt)

    tagging_event = TaggingEventFactory.create(stocking_event=event2)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=cwt)



@pytest.fixture()
def tag_in_two_yc():
    """To test the warning mechanisms, we need a tag that was applied
    in two different year classes"""

    cwt = '191919'

    #get existing strain and species
    rainbows = Species.objects.get(common_name='Rainbow Trout')

    #create two different lots of fish 10 years a part (same strain and species)
    lot1 = LotFactory(species=rainbows, spawn_year=1991)
    lot2 = LotFactory(species=rainbows, spawn_year=2001)

    cwt1 = CWTFactory(cwt=cwt, spc=rainbows, year_class=1990)
    cwt2 = CWTFactory(cwt=cwt, spc=rainbows, year_class=2000)

    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(lot=lot1)
    event2 = EventFactory(lot=lot2)

    #now associated some tags with our stocking events
    tagging_event = TaggingEventFactory.create(stocking_event=event1)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=cwt)

    tagging_event = TaggingEventFactory.create(stocking_event=event2)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=cwt)





@pytest.fixture()
def tag_in_two_locations():
    """To test the warning mechanisms, we need a tag that was applied to
    two different species."""

    cwt = '667788'

    #get existing strain and species
    rainbows = Species.objects.get(common_name='Rainbow Trout')
    strain = Strain.objects.get(species=rainbows, strain_name='Domestic')

    #get and existing lot of rainbow trout
    lot1 = Lot.objects.filter(species=rainbows).all()[0]
    #we need to create new for our second strain
    lot2 = LotFactory(species=rainbows, strain=strain)


    siteA = StockingSiteFactory(site_name='Right Here')
    siteB = StockingSiteFactory(site_name='Over There')

    cwt1 = CWTFactory(cwt=cwt, spc=rainbows, strain=strain.strain_name,
                      plant_site=siteA.site_name)
    cwt2 = CWTFactory(cwt=cwt, spc=rainbows, strain=strain.strain_name,
                      plant_site=siteB.site_name)

    #we need an event for hatchery2 - it shouldn't appear in our tests
    event1 = EventFactory(lot=lot1, site=siteA)
    event2 = EventFactory(lot=lot1, site=siteB)

    #now associated some tags with our stocking events
    tagging_event = TaggingEventFactory.create(stocking_event=event1)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=cwt)

    tagging_event = TaggingEventFactory.create(stocking_event=event2)
    CWTsAppliedFactory.create(tagging_event=tagging_event, cwt=cwt)



@pytest.mark.django_db
def test_cwt_list_status_and_template(client, db_setup):
    """verify that the cwt list url returns a status code of 200 and uses
    the template we think it does

    """

    url = reverse('cwt_list')
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/cwt_list.html' in templates


@pytest.mark.django_db
def test_cwt_list_contains_quick_search(client, db_setup):
    """the cwt list should contain an input box allowing the user to
    quickly find cwt by FSIS Cwt id.

    """

    url = reverse('cwt_list')
    response = client.get(url)
    content = str(response.content)

    assert '<input type="text" class="form-control" name="cwt"' in content
    assert 'placeholder="cwt or c-w-t">' in content


@pytest.mark.django_db
def test_cwt_list_contains_expected_data(client, db_setup):
    """verify that the cwt list url returns a status code of 200 and uses
    the template we think it does

  - the list should contain basic infomation such as:
    + year class,
    + cwt number
    + species,
    + strain
    + lifestage
    + stocking location
    + agency

    """

    url = reverse('cwt_list')
    response = client.get(url)
    content = str(response.content)


    assert '111111' in content
    assert 'Rainbow Trout' in content
    assert 'Domestic' in content
    assert '1999' in content
    assert '2000' in content
    assert 'OMNR' in content
    assert 'Our Creek' in content

    #the USFWS tag
    assert '222222' in content
    assert 'Brown Trout' in content
    assert '1990' in content
    assert '1991' in content
    assert 'USFWS' in content
    assert 'Their Creek' in content


@pytest.mark.django_db
def test_cwt_list_contains_expected_data_partial(client, db_setup):
    """verify that the cwt list url returns records for the cwts that
    partially match the pattern and does not contain information
    assoicated with cwts/records that we know do not match.

  - the list should contain basic infomation such as:
    + year class,
    + cwt number
    + species,
    + strain
    + lifestage
    + stocking location
    + agency

    """

    url = reverse('cwt_list')
    response = client.get(url,{'cwt':'111'})
    content = str(response.content)

    assert '111111'  in content
    assert 'Rainbow Trout'  in content
    assert 'Domestic' in content
    assert '1999'  in content
    assert '2000' in content
    assert 'OMNR' in content
    assert 'Our Creek' in content

    #the USFWS tag - these should not be returned by the partial match
    assert '222222'  not in content
    assert 'Brown Trout'  not in content
    assert '1990'  not in content
    assert '1991' not in content
    assert 'USFWS' not in content
    assert 'Their Creek' not in content


@pytest.mark.django_db
def test_cwt_list_partial_no_match(client, db_setup):
    """If the partial cwt id submitted does not match any cwt in the
    database, an appropriate message should be thrown. 'No records match
    that criteria'

    """

    url = reverse('cwt_list')
    response = client.get(url,{'cwt':'999'})
    content = str(response.content)

    msg = "Sorry no cwts match that criteria."
    assert msg in content



@pytest.mark.django_db
def test_cwt_detail_status_and_template(client, db_setup):
    """verify that the cwt detail url returns a status code of 200 and uses
    the template we think it does

    """


    url = reverse('cwt_detail', kwargs={'cwt_number':111111})
    response = client.get(url)

    assert response.status_code == 200
    templates = [x.name for x in response.templates]
    assert 'fsis2/cwt_detail.html' in templates



@pytest.mark.django_db
def test_cwt_detail_expected_content(client, db_setup):
    """verify that the cwt detail page contains the information we think
    it does.  Specifically:
    - cwt id
    - species names
    - proponent
    - spawn year
    - a map of associated stocking events
    - a table of associated stocking events

    verify that it does not contain information about events
    associated with other cwts of fish.

    """

    cwt = CWT.objects.get(cwt='111111')

    url = reverse('cwt_detail', kwargs={'cwt_number':cwt.cwt})
    response = client.get(url)

    content = str(response.content)

    assert "Sequence Range:" not in content  #only for sequential tags

    assert cwt.spc.common_name in content
    assert cwt.spc.scientific_name in content
    assert str(cwt.stock_year) in content
    assert str(cwt.year_class) in content
    assert str(cwt.ltrz) in content
    assert cwt.strain in content
    assert cwt.plant_site in content
    assert cwt.hatchery in content
    assert cwt.agency in content
    assert str(cwt.clipa) in content
    assert '{:,}'.format(cwt.tag_cnt) in content



@pytest.mark.django_db
def test_cwt_detail_no_matching_id(client, db_setup):
    """ If the cwt id submitted does not match any cwt in the database, an
    appropriate message should be thrown. 'No records match that
    criteria'
    """

    url = reverse('cwt_detail', kwargs={'cwt_number':999999})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_cwt_detail_sequential_tag(client, db_setup):
    """if the tag type is sequential cwt, the sequence range should be in
    the response.

    """

    url = reverse('cwt_detail', kwargs={'cwt_number':123456})
    response = client.get(url)
    content = str(response.content)

    assert "Sequence Range:" in content



@pytest.mark.django_db
def test_cwt_detail_age_at_capture(client, db_setup):
    """By default, the cwt detail page should include an age at capture
    matrix illustrating how old the fish should have been for each
    possible year of recapture.

    The cwt 11-11-11 was associated with fish from the 1999 year
    class.  That means the reponse should include an age at capture
    table with the following elements:

    2000 - 1
    2001 - 2
    2002 - 3
    ...
    2010 - 11

    """

    ages = range(1,12)
    yrs = range(2000,2011)

    base_string = '<td>{}</td><td>{}</td>'

    url = reverse('cwt_detail', kwargs={'cwt_number':111111})
    response = client.get(url)
    content = str(response.content)

    for y,a in zip(yrs, ages):
        assert base_string.format(y,a) in content



@pytest.mark.django_db
def test_cwt_detail_no_age_at_capture(client, db_setup):
    """If an age at recapture cannot be calculated (more than one year
    class or no year class associated with cwt), a meaningful message
    should be presented.
    """

    cwt1 = CWTFactory(cwt='987654',
                      year_class = 2999,
                      stock_year=3000)

    url = reverse('cwt_detail', kwargs={'cwt_number':cwt1.cwt})
    response = client.get(url)
    content = str(response.content)

    msg = 'Age at capture is not currently available for 98-76-54'
    assert msg in content


@pytest.mark.django_db
def test_cwt_detail_warning_multiple_species(client, db_setup,
                                             tag_in_two_species):
    """If the cwt number has been deployed in more than one species, a
    warning should be included in the response.
    """

    cwt = '445566'
    url = reverse('cwt_detail', kwargs={'cwt_number':cwt})
    response = client.get(url)

    templates = [x.name for x in response.templates]
    #assert 'fsis2/multiple_cwt_detail.html' in templates
    assert 'fsis2/cwt_detail.html' in templates

    content = str(response.content)

    alert = '<div class="alert alert-danger">'
    assert alert in content

    msg = ('WARNING - THIS CWT APPEARS TO HAVE BEEN USED MORE THAN ' +
           ' ONCE.  INTERPRET WITH CAUTION.')
    assert msg in content


@pytest.mark.django_db
def test_cwt_detail_warning_multiple_strains(client, db_setup,
                                             tag_in_two_strains):
    """If the cwt number has been deployed in more than one strain, a
    warning should be included in the response.
    """

    cwt = '445566'
    url = reverse('cwt_detail', kwargs={'cwt_number':cwt})
    response = client.get(url)

    templates = [x.name for x in response.templates]
    #assert 'fsis2/multiple_cwt_detail.html' in templates
    assert 'fsis2/cwt_detail.html' in templates

    content = str(response.content)
    alert = '<div class="alert alert-danger">'
    assert alert in content

    msg = ('WARNING - THIS CWT APPEARS TO HAVE BEEN USED MORE THAN ' +
           ' ONCE.  INTERPRET WITH CAUTION.')
    assert msg in content



@pytest.mark.django_db
def test_cwt_detail_warning_multiple_yc(client, db_setup,
                                               tag_in_two_yc):
    """If the cwt number has been deployed in more than one year class, a
    warning should be included in the response.
    """

    cwt = 191919
    url = reverse('cwt_detail', kwargs={'cwt_number':cwt})
    response = client.get(url)

    templates = [x.name for x in response.templates]
    #assert 'fsis2/multiple_cwt_detail.html' in templates
    assert 'fsis2/cwt_detail.html' in templates

    content = str(response.content)
    alert = '<div class="alert alert-danger">'
    assert alert in content

    msg = ('WARNING - THIS CWT APPEARS TO HAVE BEEN USED MORE THAN ' +
           ' ONCE.  INTERPRET WITH CAUTION.')
    assert msg in content




@pytest.mark.django_db
def test_cwt_detail_warning_multiple_locations(client, db_setup,
                                               tag_in_two_locations):
    """If the cwt number has been deployed in more than one stocking location, a
    warning should be included in the response.
    """

    cwt = 667788
    url = reverse('cwt_detail', kwargs={'cwt_number':cwt})
    response = client.get(url)

    templates = [x.name for x in response.templates]
    #assert 'fsis2/multiple_cwt_detail.html' in templates
    assert 'fsis2/cwt_detail.html' in templates

    content = str(response.content)
    alert = '<div class="alert alert-danger">'
    assert alert in content

    msg = ('WARNING - THIS CWT APPEARS TO HAVE BEEN USED MORE THAN ' +
           ' ONCE.  INTERPRET WITH CAUTION.')
    assert msg in content



@pytest.mark.django_db
def test_cwt_detail_OMNR_tag_with_recoveries(client, db_setup,
                                             omnr_tag_with_recoveries):
    '''If there are tag recoveries associated with a cwt number, they
    should be presented on the cwt_detail page.  the information should
    include:
      + the recpature year,
      + program (source),
      + Recovery Date,
      + 5-minute grid,
      + the project key,
      + the size and age of the fish at recapture.

    '''

    cwt = 112233
    url = reverse('cwt_detail', kwargs={'cwt_number':cwt})
    response = client.get(url)
    content = str(response.content)

    #stocking information
    events = Event.objects.filter(taggingevent__cwts_applied__cwt=cwt)

    for event in events:
        assert str(event.fs_event) in content
        assert '{:,}'.format(event.stkcnt) in content
        assert event.event_date.strftime("%b. %d, %Y") in content
        assert event.site.site_name in content
        assert event.clipa in content
        assert event.get_development_stage_display() in content



    #Recapture information
    assert "(n = 2)" in content #two recoveries to date

    #the first recapture
    assert "Creel" in content
    assert "2012" in content
    assert date(2012, 11, 15).strftime("%b. %d, %Y") in content
    assert "9999" in content
    assert "Recovery-Key1" in content
    assert "500" in content

    #the second recapture
    assert "Index" in content
    assert "2010" in content
    assert date(2010, 11, 15).strftime("%b. %d, %Y") in content
    assert "8888" in content
    assert "Recovery-Key2" in content
    assert "400" in content #fork length



@pytest.mark.django_db
def test_cwt_detail_OMNR_tag_without_recoveries(client, db_setup):
    '''the cwt detail for a valid tag without recoveries should provide a
    meaningful message to that effect but should still include basic
    stocking event informtaion:
    + FSIS number (link)
    + Number stocked
    + Event Date
    + Site Name
    + Clip
    + Development State

    '''

    cwt = 111111
    url = reverse('cwt_detail', kwargs={'cwt_number':cwt})
    response = client.get(url)
    content = str(response.content)

    events = Event.objects.filter(taggingevent__cwts_applied__cwt=cwt)

    for event in events:
        assert str(event.fs_event) in content
        assert '{:,}'.format(event.stkcnt) in content
        assert event.event_date.strftime("%b. %d, %Y") in content
        assert event.site.site_name in content
        assert event.clipa in content
        assert event.get_development_stage_display() in content

    assert 'OMNR' in content
    assert 'This cwt has not been recovered (yet).' in content



@pytest.mark.django_db
def test_cwt_detail_OMNR_tag_without_stocking_events(client, db_setup):
    '''If we try to access a cwt that does not have any stocking events
    associated with it, we should handle that gracefully and issue an
    appropriate warning. This error indicates that this cwt is not in
    FSIS.

    '''

    url = reverse('cwt_detail', kwargs={'cwt_number':123456})
    response = client.get(url)
    content = str(response.content)

    alert = '<div class="alert alert-danger">'
    assert alert in content

    msg = ('There are no Ontario stocking events associated with cwt 12-34-56.'
           + '   According to the Agency code there should be.')
    assert msg in content



@pytest.mark.django_db
def test_cwt_detail_US_tag_with_recoveries(client, db_setup,
                                           us_tag_with_recoveries):
    '''If there are tag recoveries associated with a cwt number
    stocked by another agency, the recoveries should be presented on
    the cwt_detail page.  The information should include:
      + the recpature year,
      + program (source),
      + Recovery Date,
      + 5-minute grid,
      + the project key,
      + the size and age of the fish at recapture.

    '''

    url = reverse('cwt_detail', kwargs={'cwt_number':333333})
    response = client.get(url)
    content = str(response.content)

    msg = "There are no Ontario stocking events associated with cwt 33-33-33."
    assert msg in content

    assert "(n = 2)" in content #two recoveries to date

    #the first recapture
    assert "Catch Sampling" in content
    assert "2012" in content
    assert date(2012, 11, 15).strftime("%b. %d, %Y") in content
    assert "9999" in content
    assert "Recovery-Key1" in content
    assert "500" in content

    #the second recapture
    assert "Creel" in content
    assert "2010" in content
    assert date(2010, 11, 15).strftime("%b. %d, %Y") in content
    assert "8888" in content
    assert "Recovery-Key2" in content
    assert "400" in content #fork length


@pytest.mark.django_db
def test_cwt_detail_US_tag_without_recoveries(client, db_setup):
    '''the cwt detail for a valid tag without recoveries should provide a
    meaningful message to that effect.'''


    url = reverse('cwt_detail', kwargs={'cwt_number':222222})
    response = client.get(url)
    content = str(response.content)

    assert 'USFWS' in content
    assert 'This cwt has not been recovered (yet).' in content
