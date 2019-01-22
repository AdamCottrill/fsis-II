#=============================================================
# c:/1work/Python/djcode/fsis2/utils/data_migration.py
# Created: 29 Aug 2013 09:11:14
#
# DESCRIPTION:
#
# This script migrates the data from our existing FS_Master.mdb
# database to the postgres database that is by Django
# to render the fsis2 webpages.
#
# The script can be run from the command line by:
#      ~/python migrate_data.py
#
# Alternatively, tables can be uploaded one at a time by intactive
# submitting chunks of code associated with each table.  If used
# interactively, be sure to submit the tables in the proper order,
# tables later in the script often have a large number of foreign key
# dependencies on earlier tables.
#
# Each table 'chunk' is structured following a similiar pattern:
# - the source database is queried using a raw sql string
# - a loop is then used to iterate over the rows of the recordset.
#   Any associated objects are returned from the database and related to
#   the new sqlalchemy object, which is then added to the session.
# - after the loop is complete, the session is committed to the database.
#
# A. Cottrill
#=============================================================

import os
import sys

os.chdir('c:/Users/COTTRILLAD/Documents/1work/Python/djcode/fsis2/utils/')

import pytz
from datetime import datetime

import pyodbc

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
#from geoalchemy.base import WKTSpatialElement
from geoalchemy2.elements import WKTElement

from sqa_models import *
from helper_fcts import *


#here is where the data will be coming from:
MDB = 'C:/1work/Data_Warehouse/FS_Master.mdb'


#here is dicationary that will be needed for the tag attribute table.
#It may need to be updated if more tag positions are used in fsis.
TAG_POSITIONS = {
    'Flesh of Back':1,
    'Operculum':2,
    'Posterior Dorsal Fins':3,
    'Snout':4}

#are we working in the deployment machine or just locally?
DEPLOY = False

#override DEPLOY if it was passed in as a command line option.
for arg in sys.argv[1:]:
    exec(arg)
assert type(DEPLOY) == bool


#========================================
#          HELPER FUNCTIONS

def get_spc(species_code, session):
    """ a little helper function to get the appropriate species given
    an (Ontario) species code.
    Arguments:
    - `abbrev`: species abbreviation (eg - '081')
    - `session` - sqlalchemy session used to connect to target database
    """
    spc_code = int(species_code)
    try:
        species = session.query(Species).filter_by(species_code=spc_code).one()
        return species
    except (MultipleResultsFound, NoResultFound) as e:
        msg = "Species: {} with species_code='{}'".format(e, spc_code)
        print(msg)


def get_lot(fs_lot, spawn_year, species, session):
    """a little helper function to get the fish lot given a species,
    lot number and spawn year.  fs_lot is an identifier used by
    Fishculture section to track groups of fish, it is uniquue within
    a species and yearclass, but may not be through time. The function
    prints a meaningful message if an error occurs

    Arguments: -

    - `fs_lot`: fish culture's lot identifier
    - `spawn_year`: the year the fish were spawned
    - `species`: a sqlalchemy species instance (returned from get_spc())
    - `session` - sqlalchemy session used to connect to target
    database

    """


    try:
        lot = session.query(Lot).filter_by(species_id=species.id,
                                           fs_lot=fs_lot,
                                           spawn_year=spawn_year).one()
        return lot
    except (MultipleResultsFound, NoResultFound) as e:
        msg = "Lot: {} ({}, {}, {})".format(e, fs_lot, spawn_year, species)
        print(msg)



def get_site(site_id, session):
    """a little helper function to the stocking site for a particular
    stocking event.  Prints a meaningful message if a error occurs.

    Arguments: -

    - `site_id`: id number of the associated stocking site
    - `session` - sqlalchemy session used to connect to target
    database

    """
    try:
        site = session.query(StockingSite).filter_by(
            fsis_site_id=site_id).one()
        return site
    except (MultipleResultsFound, NoResultFound) as e:
        msg = "Stocking Site: {} (site_id={}))".format(e, site_id)
        print(msg)




#========================================
#            MDB CURSOR

mdbconstr ="DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={}"
mdbcon = pyodbc.connect(mdbconstr.format(MDB))
mdbcur = mdbcon.cursor()


#========================================
#           DATA TARGET

#target_db we will be using sqlalchemy to upload the data into the
#stocking database - it's database agnostic, so we just need to change
#the engine if our database changes

if DEPLOY:
    #engine = create_engine('postgresql://adam:django@localhost/fsis2')
    #this will connect to post gres instance on the desktop machine
    engine = create_engine('postgresql://cottrillad:django@142.143.160.56/fsis2')
else:
    #engine = create_engine('postgresql://COTTRILLAD:uglmu@localhost/fsis2')
    engine = create_engine('postgresql://cottrillad:django123@localhost/fsis2')

Session = sessionmaker(bind=engine)
session = Session()

#========================================
#           CLEAR TARGET

# make sure that any old data in the target database is removed before
# we append in new data.

session.execute('TRUNCATE cwts_cwt_recovery;')
session.execute('TRUNCATE cwts_cwt;')

session.query(CWTs_Applied).delete()
session.query(TaggingEvent).delete()
session.query(Event).delete()
session.query(Lot).delete()
session.query(Strain).delete()
session.query(Species).delete()
session.query(Proponent).delete()
session.query(StockingSite).delete()
session.query(Readme).delete()
session.commit()

#========================================
#           README TABLE
table = "readme"
print("Uploading '%s'..."  % table)

sql = '''SELECT [__README].DATE, [__README].COMMENT, [__README].INIT
        FROM __README
        ORDER BY [__README].DATE DESC;'''

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0] for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    item = Readme(
            #date =  datetime.datetime.strptime(row['DATE'],
            #                                   '%Y-%m-%d  %H:%M:%S'),
        date = row['DATE'],
        comment = row['COMMENT'],
            initials = row['INIT'])
    session.add(item)

session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S')))



#========================================
#           SPECIES TABLE
table = "species"
print("Uploading '%s'..."  % table)

sql = """SELECT SPC, SPC_NM, SPC_NMSC
FROM SPC
WHERE SPC.SPC Not In ('000','032', '998','999')
AND SPC_NM is not null and SPC_NMSC is not null
ORDER BY SPC.SPC;
"""

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0] for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    item = Species(species_code = row['SPC'],
            common_name = row['SPC_NM'],
            scientific_name = row['SPC_NMSC'])
    session.add(item)

#manually add backcross - they don't have a sci. name but we need them
#because they were stocked.
item = Species(species_code = '087',
            common_name = 'Backcross Lake Trout')
session.add(item)

session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S')))


#========================================
#           STRAINS TABLE
table = "strains"
print("Uploading '%s'..."  % table)

sql='''SELECT TL_Strains.SPC, TL_Strains.STO, TL_Strains.StrainCode,
       TL_Strains.StrainName
      FROM TL_Strains;'''

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0] for x in mdbcur.description]

allspc = session.query(Species)

for x in data:
    row = dict(zip(colnames, x))
    spc = allspc.filter_by(species_code=row['SPC']).one()
    spc.strains.extend([Strain(sto_code= row['STO'].upper(),
                               strain_code= row['StrainCode'].upper(),
                               strain_name= row['StrainName'])])
session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S')))


#========================================
#         PROPONENT TABLE
table = "Proponents"
print("Uploading '%s'..."  % table)

sql = """select abbreviation as abbrev,
       proponentName as name from tl_proponents;"""

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0] for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    item = Proponent(abbrev = row['abbrev'],
            proponent_name = row['name'])
    session.add(item)

session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S')))


#========================================
#        STOCKING SITES
table = "Stocking Sites"
print("Uploading '%s'..."  % table)

sql = '''SELECT SITE_ID, SITE_NAME, STKWBY, STKWBY_LID, UTM, GRID,
             DD_LAT, DD_LON, BASIN, DESWBY_LID, DESWBY
         FROM FS_Events
         GROUP BY SITE_ID, SITE_NAME, STKWBY, STKWBY_LID, UTM, GRID,
             DD_LAT, DD_LON, BASIN, DESWBY_LID, DESWBY;'''

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0] for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    pt = "POINT(%s %s)" % (row['DD_LON'], row['DD_LAT'])
    item = StockingSite(
        fsis_site_id =  row['SITE_ID'],
        site_name = row['SITE_NAME'],
        stkwby  = row['STKWBY'],
        stkwby_lid = row['STKWBY_LID'],
        utm  = row['UTM'],
        grid = row['GRID'],
        dd_lat = row['DD_LAT'],
        dd_lon = row['DD_LON'],
        basin = row['BASIN'],
        deswby_lid  = row['DESWBY_LID'],
        deswby  = row['DESWBY'],
        #geom = WKTSpatialElement(pt),
        geom = WKTElement(pt, srid=4326),
        popup_text = row['SITE_NAME'],
        )
    session.add(item)
session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S')))

#========================================
#        LOTS TABLE
table = "Lots"
print("Uploading '%s'..."  % table)

#note - query aggregates by strain, spawn year, rearing location
# and does not include project code or year -
sql = '''SELECT lot, SPC, STO, spawn_year, rearloc, rearloc_nm,
         PROPONENT_NAME as abbrev, proponent_type FROM FS_Lots
         GROUP BY LOT, SPC, STO, SPAWN_YEAR, REARLOC, REARLOC_NM,
         PROPONENT_NAME, PROPONENT_TYPE;'''

### includes join to standardize proponent names:
#sql = '''SELECT LOT, SPC, STO, SPAWN_YEAR, REARLOC, REARLOC_NM,
#         short as abbrev, PROPONENT_TYPE FROM FS_Lots
#         join TL_proponentNames as x
#         on x.proponent_name_is=FS_Lots.proponent_name
#         GROUP BY LOT, SPC, STO, SPAWN_YEAR, REARLOC, REARLOC_NM,
#         abbrev, PROPONENT_TYPE having x.preferred=1;'''


mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0] for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    spc = session.query(Species).filter_by(species_code=row['SPC']).one()
    strain = session.query(Strain).filter_by(species_id=spc.id,
                                             sto_code=row['STO'].upper()).one()
    proponent = session.query(Proponent).filter_by(abbrev=row['abbrev']).one()
    item = Lot(
    #prj_cd = row.prj_cd,
        fs_lot  = row['lot'],
        spawn_year = row['spawn_year'],
        rearloc = row['rearloc'],
        rearloc_nm = row['rearloc_nm'],
        proponent_type = row['proponent_type'],
        species_id = spc.id,
        strain_id = strain.id,
        proponent_id = proponent.id
    )
    session.add(item)

session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S')))


#========================================
#       STOCKING EVENTS

table = "Events"
print("Uploading '%s'..."  % table)

#MS ACCESS SYNTAX:
sql = '''SELECT FS_Events.Spc, FS_Lots.SPAWN_YEAR, FS_Events.LOT,
            FS_Events.SITE_ID, FS_Events.PRJ_CD, FS_Events.Event AS fs_event,
            FS_Events.LOTSAM, FS_Events.Year, FS_Events.Event_Date, FS_Events.CLIPA,
            FS_Events.FISH_AGE, FS_Events.STKCNT, FS_Events.FISH_WT,
            FS_Events.RECORD_BIOMASS_CALC, FS_Events.REARTEM, FS_Events.SITEM,
            FS_Events.TRANSIT_MORTALITY_COUNT AS mortality, FS_Events.DD_LAT,
            FS_Events.DD_LON,
            IIf(IsNull([FS_EVENTS].[DEV_CODE]),99,[FS_Events].[DEV_CODE]) AS
            DEV_CODE, FS_Events.TRANSIT, FS_Events.METHOD, FS_Events.STKPUR
            FROM FS_Lots INNER JOIN FS_Events ON (FS_Lots.SPC = FS_Events.SPC)
            AND (FS_Lots.LOT= FS_Events.LOT)
            AND (FS_Lots.PRJ_CD = FS_Events.PRJ_CD);'''


##SQLITE SYNTAX:
#sql = '''select fs_events.spc, fs_lots.spawn_year, fs_events.lot,
#            fs_events.site_id, fs_events.prj_cd, fs_events.event as fs_event,
#            fs_events.lotsam, fs_events.year, fs_events.event_date, fs_events.clipa,
#            fs_events.fish_age, fs_events.stkcnt, fs_events.fish_wt,
#            fs_events.record_biomass_calc, fs_events.reartem, fs_events.sitem,
#            fs_events.transit_mortality_count as mortality, fs_events.dd_lat,
#            fs_events.dd_lon,
#            case when [fs_events].[dev_code] is null then 99
#            else [fs_events].[dev_code] end as dev_code,
#            dev_code, fs_events.transit, fs_events.method, fs_events.stkpur
#            from fs_lots inner join fs_events on (fs_lots.spc = fs_events.spc)
#            and (fs_lots.lot= fs_events.lot)
#            and (fs_lots.prj_cd = fs_events.prj_cd);'''
#

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0].lower() for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    pt = "POINT(%s %s)" % (row['dd_lon'], row['dd_lat'])
    #get objects referenced by foreign key

    spc = get_spc(row['spc'], session)
    lot = get_lot(row['lot'].strip(), row['spawn_year'], spc, session)
    site = get_site(row['site_id'], session)

    item = Event(
        lot_id = lot.id,
        site_id = site.id,
        prj_cd =  row['prj_cd'],
        year = row['year'],
        fs_event = row['fs_event'],
        lotsam = row['lotsam'],
        event_date = datetime_or_none(row['event_date']),
        clipa = row['clipa'],
        fish_age = row['fish_age'],
        stkcnt = row['stkcnt'],
        fish_wt = row['fish_wt'],
        record_biomass_calc = row['record_biomass_calc'],
        reartem = row['reartem'],
        sitem = row['sitem'],
        transit_mortality_count = row['mortality'],
        development_stage =  99 if row.get('dev_code') is None else row.get('dev_code'),
        transit = upper_or_none(row['transit']),
        stocking_method = upper_or_none(row['method']),
        stocking_purpose = upper_or_none(row['stkpur']),
        dd_lat = row['dd_lat'],
        dd_lon = row['dd_lon'],
        popup_text = row['fs_event'],
        #geom = WKTSpatialElement(pt),
        geom = WKTElement(pt, srid=4326),
    )
    session.add(item)

session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S')))



#========================================
#       TAGGING EVENTS

table = "Tagging Events"
print("Uploading '%s'..."  % table)

sql = '''SELECT EVENT AS fs_event, TAG_ID, RETENTION_RATE_PCT,
            RETENTION_RATE_SAMPLE_SIZE, RETENTION_RATE_POP_SIZE,
            COMMENTS, TAG_TYPE_CODE, TAG_POSITION, TAG_ORIGIN_CODE,
            TAG_COLOUR_CODE
         FROM FS_TagAttributes;'''

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0].lower() for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    #get objects referenced by foreign key
    stocking_event=session.query(Event).filter_by(
        fs_event=row['fs_event']).one()
    item = TaggingEvent(
            stocking_event_id = stocking_event.id,
            fs_tagging_event_id = row['tag_id'],
            retention_rate_pct = row['retention_rate_pct'],
            retention_rate_sample_size = row['retention_rate_sample_size'],
            retention_rate_pop_size = row['retention_rate_pop_size'],
            comments = row['comments'],
            tag_type =  row['tag_type_code'],
            tag_position =  TAG_POSITIONS[row['tag_position']],
            tag_origins =  row['tag_origin_code'],
            tag_colour =  row['tag_colour_code'],
    )
    session.add(item)

session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
      (table, now.strftime('%Y-%m-%d %H:%M:%S')))



#========================================
#       CWTs APPLIED

table = "CWTs Applied"
print("Uploading '%s'..."  % table)

sql = ''' SELECT TAG_ID AS fs_tagging_event_id, CWT
          FROM FS_CWTs_Applied;'''

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0].lower() for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    #get objects referenced by foreign key
    tagging_event = session.query(TaggingEvent).filter_by(
                        fs_tagging_event_id=row['fs_tagging_event_id']).one()
    item = CWTs_Applied(
            tagging_event_id=tagging_event.id,
            fs_tagging_event_id = row['fs_tagging_event_id'],
            cwt = int(row['cwt'])
    )
    session.add(item)

session.commit()

now = datetime.datetime.now()
print("'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S')))


#========================================
#              BUILD DATE
build_date = BuildDate(build_date = datetime.datetime.utcnow())
session.add(build_date)
session.commit()



#========================================
#        UPDATE STOCKING LOCATIONS

#finally, update the spatial date for each event with the actual
#lat-lon where the event occured.
print('Updating spatial info...')

sql = ''' SELECT * from TL_ActualStockingSites;'''

mdbcur.execute(sql)
data = mdbcur.fetchall()
colnames = [x[0].lower() for x in mdbcur.description]

for x in data:
    row = dict(zip(colnames, x))
    event = session.query(Event).filter_by(fs_event=row['event']).one()
    event.dd_lat = row['dd_lat']
    event.dd_lon = row['dd_lon']
    pt = "POINT(%s %s)" % (row['dd_lon'], row['dd_lat'])
    event.geom =  WKTElement(pt, srid=4326)
    session.add(event)
session.commit()
print('Spatial up to date.')


print("All Migrations Complete ({0})".format(build_date))

session.close()
