'''
=============================================================
c:/1work/Python/djcode/fsis2/fsis2/utils.py
Created: 05 Oct 2015 14:23:37


DESCRIPTION:



A. Cottrill
=============================================================
'''


from fsis2.models import (Event, Lot, TaggingEvent, CWTs_Applied, StockingSite,
                     Proponent, Species, Strain,
                          ManagementUnit, Lake, BuildDate, Readme)

from cwts.models import CWT, CWT_recovery


from datetime import datetime



def get_totals(events):
    """give a queryset of stocking events, return a dictionary with keys
    'total' and 'basins'.  Total will be the all sum of stkcnt for all
    records the queryset.  basin will be dictionary containing the sum of
    fish stocked by basin.

    Arguments:
    - `qs`:

    """

    basins = {}

    #if this basin key exists in the dictionary, add the stkcnt,
    #otherwise create the key and set it equal to the total.
    for event in events:
        if basins.get(event.site.basin):
           basins[event.site.basin] += event.stkcnt
        else:
           basins[event.site.basin] = event.stkcnt

    total = sum([x[1] for x in basins.items()])
    totals = {'total':total, 'basins':basins}

    return totals






#def calc_aac(yc):
#    """given a year class that a cwt was associated with calculate
#    age-at-capture for every year between age 0 and today
#
#    returns a list of two element tuples.  each tuple contains the
#    year and the age the fish would have been if it had been captured
#    in that year.  If yc is greater than the current year it returns None.
#
#    """
#
#    from datetime import datetime
#    this_year = datetime.now().year
#    if this_year < yc:
#        return None
#    else:
#        yrs = range(yc, this_year + 1)
#        aac = list(enumerate(yrs, start=0))
#        aac.sort(reverse=True, key=lambda x: x[1])
#        return aac
#


def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    from:http://flask.pocoo.org/snippets/33/
    """

    now = datetime.utcnow()
    diff = now - dt

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default


def footer_string():
    '''Build the footer string that indicates when the website
    database as last build and when the data was last downloaded from
    fsis.  This string will appear at the bottom of a number of
    standard views
    '''

    build_date = BuildDate.objects.latest('build_date').build_date
    build_date = build_date.strftime("%b-%d-%Y")

    download_date = Readme.objects.latest('date')
    download_date = download_date.get_download_date()
    delta = timesince(download_date) #lapse time
    download_date = download_date.strftime("%b-%d-%Y") #time as a string

    ftr_str="FSIS-II built on {0} using data downloaded from FSIS on {1} ({2})"
    ftr_str = ftr_str.format(build_date, download_date, delta)
    return ftr_str


def prj_cd_Year(x):
    '''format LHA_IA12_000 as 2012'''
    if int(x[6:8]) > 60:
        yr = "".join(["19", x[6:8]])
    else:
        yr = "".join(["20", x[6:8]])
    return yr


def get_basin_totals(year, spc, strain=None):
    '''A helper function to retrieve the number of fish stocked by
    basin given a species and year.

    This function uses raw sql - the django orm still doesn't seem to
    to aggregation well.'

    Returns a dictionary that includes keys for 'North Channel',
    'Georgian Bay', 'Main Basin' and 'total''

    '''
    from django.db import connection

    #spc ignoring strain
    sql = '''select basin, sum(stkcnt) from fsis2_event
         join fsis2_lot on fsis2_lot.id=fsis2_event.lot_id
         join fsis2_species on fsis2_species.id = fsis2_lot.species_id
         join fsis2_stockingsite on fsis2_stockingsite.id = fsis2_event.site_id
         group by basin, year, species_code having
         fsis2_event.year=%(year)s and
         fsis2_species.species_code=%(spc)s;
         '''

    cursor = connection.cursor()
    cursor.execute(sql, {'year':year, 'spc':spc})
    rs = cursor.fetchall()

    basin_dict = dict()
    for basin in rs:
        #remove any spaces and turn them into lowercase
        basin_name = basin[0].lower().replace(" ","")
        basin_dict[basin_name] = int(basin[1])
    basin_dict['total']=sum(basin_dict.values())

    return basin_dict




#==============================================================
#                 UTLITIES BELOW THIS POINT

# helper functions that should be moved to utls.py


def get_management_unit_dict():
    '''get a nested dictionary of dictionaries containing the management
    unit labels and types in each lake.
    1st level - lake name
    2nd level - management unit type
    3rd level - management unit labels

    dictionary is iterated over in managment list template. - one tab
    per list, collapsing panels containing management unit labels

    '''
    lakes = Lake.objects.all()
    object_dict = {}
    for lake in lakes:
        mus = ManagementUnit.objects.filter(lake=lake).order_by('mu_type',
                                                                'label')
        mu_dict = {}
        for mu in mus:
            mu_dict.setdefault(mu.get_mu_type_display(), []).append(
                dict(slug=mu.slug, label=mu.label))
        object_dict[lake.lake] = mu_dict
    return object_dict





def get_recovery_points(recoveries):
    '''a helper function to extract the project composite key and the
    point of recovery given a list/queryset of recoveries.

    returns a list of list pairs of the form [composite key, geom]

    '''
    if recoveries:
        try:
            recovery_points = [[x.composite_key, x.geom] for x in recoveries]
        except:
            recovery_points = [[recoveries.composite_key, recoveries.geom]]
    else:
        recovery_points = []
    return recovery_points


def get_stocking_points(stocking_events):
    '''a helper function to extract the stocking event identifier and point
    geometry given a list/queryset of stocking events.

    returns a list of list pairs of the form [fs_event, geom]

    '''
    if stocking_events:
        try:
            event_points = [[x.fs_event, x.geom] for x in stocking_events]
        except:
            event_points = [[stocking_event.fs_event, stocking_event.geom]]
    else:
        event_points = []
    return event_points



def get_recovered_cwts(mu_poly, year=None, strain=None):
    """A helper function to actually get the cwt stocking and recovery
    data.  Given a management unit polygon, find all of the cwt
    recoveries from that polygon as well as their associated stocking events.

    Returns a dictionary containing the following keys:

    cwts = a cwt queryset of that contains only those cwts recovered
    in this management unit
    recoveries = recovery events for this managemnet unit(year and strain)
    events = Ontario stocking events associated with the cwts recovered
    US_events = U.S stocking events associated with the cwts recovered

    """

    recoveries = CWT_recovery.objects.filter(geom__within=mu_poly.geom)

    #these are all of the cwt recoveries - all strains and species
    if year:
        recoveries = recoveries.filter(recovery_year=year)

    #cwts = []
    #[cwts.append(x.cwt) for x in recoveries]
    #cwts= list(set(cwts))

    cwts = [x.cwt for x in recoveries]
    recovery_count = dict([(i, cwts.count(i)) for i in set(cwts)])

    cwts = recovery_count.keys()

    #now that we have a list cwts recovered in the roi and year
    #get the stocking events associated with them and filter by the strain:
    filtered_cwts=[]

    #canadian stocking events
    events = (Event.objects.filter(taggingevent__cwts_applied__cwt__in=cwts).
              distinct().order_by('fs_event'))
    if strain:
        events = events.filter(lot__strain__strain_code=strain)

    for event in events:
        tmp = event.get_cwts()
        if tmp:
            filtered_cwts.extend([x.cwt for x in tmp])

    #filtered cwts include only those cwts we recovered in this roi
    #and have stocking event associated with them (this eliminates cwts
    #that may not have been recovered but are associated with same
    #stocking events)
    filtered_cwts = list(set(filtered_cwts).intersection(set(cwts)))

    #US stocking events
    US_events = (CWT.objects.filter(cwt__in=cwts).exclude(agency='OMNR').
                 order_by('year_class'))

    filtered_cwts.extend(list(set([x.cwt for x in US_events])))

    filtered_cwts = CWT.objects.filter(cwt__in=filtered_cwts)
    for x in filtered_cwts:
        x.recovery_count = recovery_count.get(x.cwt, 0)

    #add recovery_count to each of the cwt numbers:
    #import pdb; pdb.set_trace()

    ret = dict( cwts = filtered_cwts,
                 recoveries = recoveries, events = events,
                 US_events = US_events)

    return ret


def get_cwts_stocked_mu(mu_poly, year=None, strain=None):
    """A helper function to actually get the cwt stocking and recovery
    data for cwts stocked in a management unit.  Given a management unit
    polygon, find all of the stocking events that have occured inside
    of it, and then get all of their associated recovery events.

    Returns a dictionary containing the following keys:
    cwts = set of unique cwt numbers recovered in this management unit
    recoveries = recovery events for this management unit (year and strain)
    events = Ontario stocking events associated with the cwts recovered

    """
    #get all of the stocking events with a cwt tagging event that have
    #occured in the management unit
    events = (Event.objects.filter(taggingevent__tag_type=6).
              filter(geom__within=mu_poly.geom))
    if year:
        events = events.filter(year=year)
    if strain:
        events = events.filter(lot__strain__strain_code='SI')

    #extract the unique cwts associated with those events
    cwt_numbers = []
    for event in events:
        tmp = event.get_cwts()
        if tmp:
            cwt_numbers.extend([x.cwt for x in tmp])
    cwt_numbers=list(set(cwt_numbers))

    #get the all recovery instances from the set of cwts
    recoveries = CWT_recovery.objects.filter(cwt__in=cwt_numbers)
    cwts = CWT.objects.filter(cwt__in=cwt_numbers)

    #we need to add the number of recoveries to each cwt instance:

    #pull out just the cwt numbers and put them in a list
    foo = [x.cwt for x in recoveries]
    #create a dictionary of counts by cwt number
    recovery_counts = dict([(i, foo.count(i)) for i in set(foo)])

    for x in cwts:
        x.recovery_count = recovery_counts.get(x.cwt, 0)

    return(dict( cwts=cwts, events = events,
                 recoveries = recoveries))





#==============================================================
#these are olwidget views that will eventually be replaced with
#leaflet equivalents

def get_map(event_points):
    """a helper function that will return an info map object containing
    the points in event_points

    Arguments:
    - `event_points`:

    """
    if len(event_points)>0:
        geoms = [[x[1],x[0]] for x in event_points]
        map = InfoMap(
            geoms,
            {'default_lat': 45,
            'default_lon': -82.0,
            'default_zoom': 7,
            'zoom_to_data_extent': False,
            'map_div_style': {'width': '700px', 'height': '600px'},
            }
            )
    else:
        map=None
    return map


def empty_map():
    """returns and empty map zoomed to Lake Huron.  Used when no points
    are available.
    Arguments:
    - None

    """
    map = InfoMap(
        None,
        {'default_lat': 45,
         'default_lon': -82.0,
         'default_zoom': 7,
         'zoom_to_data_extent': False,
         'map_div_style': {'width': '700px', 'height': '600px'}})
    return map



#def get_map2(event_points, roi=None):
#    """This map function taks a list of points and a region of
#    interest and returns a map that is zoomed to spatial extent of the
#    roi.  The roi and all of the points it contains are rendered.
#
#    used by views find_events
#
#    Arguments: -
#    `event_points`: a list of points objects and their event numbers
#    'roi': region of interest used to select event points
#
#    """
#    layers = []
#    zoom_to_extent = False
#    if len(event_points)>0:
#        if roi:
#            style = {'overlay_style': {'fill_color': '#0000FF',
#                               'fill_opacity': 0,
#                               'stroke_color':'#0000FF'},
#                     'name':'Region of Interest'}
#            #polygon = InfoLayer([roi,style])
#            polygon =  InfoLayer([[roi.wkt, "Region Of Interest"]] ,style)
#            try:
#                layers.extend(polygon)
#            except TypeError:
#                layers.append(polygon)
#            zoom_to_extent = True
#
#        for pt in event_points:
#            pt_layer = InfoLayer([[pt[1].wkt, str(pt[0])]],{'name':str(pt[0])})
#            try:
#                layers.extend(pt_layer)
#            except TypeError:
#                layers.append(pt_layer)
#
#        mymap = Map(
#            layers,
#            {'default_lat': 45,
#            'default_lon': -82.0,
#            'default_zoom':7,
#            'zoom_to_data_extent': zoom_to_extent,
#            'map_div_style': {'width': '700px', 'height': '600px'},
#
#            }
#            )
#    else:
#        mymap = empty_map()
#    return mymap


def get_recovery_map(stocking_points, recovery_points, roi=None):

    """This map function takes a list of stocking points and second
    list of recovery points.

    used by views cwt_detail to illustrate where a cwt was stocked and
    subsequently recovered.

    Arguments: -
    `stocking_points`: a list of points objects and their event numbers
    `recovery_points`: a list of recovery point objects and their id string
    'roi': region of interest used to select event points

    """
    layers = []

    if roi:
        #if there was a region of interest, add it first so its on the bottom
        style = {'overlay_style': {'fill_color': '#7DF9FF',
                           'fill_opacity': 0,
                           'stroke_color':'#7DF9FF'},
                 'name':'Region of Interest'}
        #polygon = InfoLayer([roi,style])
        polygon =  InfoLayer([[roi.wkt, "Region Of Interest"]] ,style)
        try:
            layers.extend(polygon)
        except TypeError:
            layers.append(polygon)

    if recovery_points:
        for pt in recovery_points:
            recovery_layer = InfoLayer([[pt[1].wkt, str(pt[0])]],
                                   {'name':str(pt[0]),
                                    'overlay_style': {'fill_color': '#00FF00',
                                                      'fill_opacity': 0.2,
                                                      'stroke_color':'#00FF00'},
                                })
            try:
                layers.extend(recovery_layer)
            except TypeError:
                layers.append(recovery_layer)

    if len(stocking_points) > 0:
        for pt in stocking_points:
            pt_layer = InfoLayer([[pt[1].wkt,
                                   str(pt[0])]], {'name': str(pt[0])})
            try:
                layers.extend(pt_layer)
            except TypeError:
                layers.append(pt_layer)

    if len(layers) > 0:
        mymap = Map(
            layers,
            {'default_lat': 45,
             'default_lon': -82.0,
             'default_zoom': 7,
             'zoom_to_data_extent': False,
             'map_div_style': {'width': '700px', 'height': '600px'},
            })
    else:
        mymap = empty_map()
    return mymap
