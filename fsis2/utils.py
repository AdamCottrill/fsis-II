'''
=============================================================
c:/1work/Python/djcode/fsis2/fsis2/utils.py
Created: 05 Oct 2015 14:23:37


DESCRIPTION:



A. Cottrill
=============================================================
'''


from fsis2.models import BuildDate, Readme
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






def calc_aac(yc):
    """given a year class that a cwt was associated with calculate
    age-at-capture for every year between age 0 and today

    returns a list of two element tuples.  each tuple contains the
    year and the age the fish would have been if it had been captured
    in that year.  If yc is greater than the current year it returns None.

    """

    from datetime import datetime
    this_year = datetime.now().year
    if this_year < yc:
        return None
    else:
        yrs = range(yc, this_year + 1)
        aac = list(enumerate(yrs, start=0))
        aac.sort(reverse=True, key=lambda x: x[1])
        return aac



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
