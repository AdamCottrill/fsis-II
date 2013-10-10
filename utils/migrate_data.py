#=============================================================
# c:/1work/Python/djcode/fsis2/utils/data_migration.py
# Created: 29 Aug 2013 09:11:14

#
# DESCRIPTION:
#
# This script migrates the data from our existing FS_Master.mdb
# database to a sqlite or postgres database that can be used by Django
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
# Each table 'chunk' is structured followin a similiar pattern:
# - the source database is queried using a raw sql string
# - a loop is then used to iterate over the rows of the recordset.
#   Any associated objects are returned from the database and related to
#   the new sqlalchemy object, which is then added to the session.
# - after the loop is complete, the session is committed to the database.
#
# A. Cottrill
#=============================================================

import pytz
from datetime import datetime
import sqlite3
#import adodbapi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy.base import WKTSpatialElement


from sqa_models import *
from helper_fcts import *


#here is dicationary that will be needed for the tag attribute table.
#It may need to be updated if more tag positions are used in fsis.
TAG_POSITIONS = {
    'Flesh of Back':1,
    'Operculum':2,
    'Posterior Dorsal Fins':3,
    'Snout':4}


#are we working in the deployment machine or just locally?
DEPLOY = False


#========================================
#            DATA SOURCE

#here is where the data will be coming from:
#source db
## srcdb = "C:/1work/Python/djcode/fsis2/utils/FS_Master_to_FSIS2.mdb"
## 
## src_constr = 'Provider=Microsoft.Jet.OLEDB.4.0; Data Source=%s'  % srcdb
## src_conn = adodbapi.connect(src_constr)
## src_cur = src_conn.cursor()
## 

#sqlite clone of FS_master:
if DEPLOY:
    src = r'c:/1work/djcode/fsis2/utils/data/FS_Master_clone.db'
else:
    src = r'c:/1work/Python/djcode/fsis2/utils/data/FS_Master_clone.db'
    
src_conn = sqlite3.connect(src)
src_conn.row_factory = sqlite3.Row

src_cur = src_conn.cursor()



#========================================
#           DATA TARGET

#target_db we will be using sqlalchemy to upload the data into the
#stocking database - it's database agnostic, so we just need to change
#the engine if our database changes

#trgdb = "C:/1work/Python/djcode/fsis2/db/fsis2.db"
#trgdb = '/home/adam/Documents/djcode/fsis2/db/fsis2.db'
#engine = create_engine('sqlite:///%s' % trgdb)

if DEPLOY:
    engine = create_engine('postgresql://adam:django@localhost/fsis2')
else:
    engine = create_engine('postgresql://COTTRILLAD:uglmu@localhost/fsis2')

Session = sessionmaker(bind=engine)
session = Session()


#========================================
#           CLEAR TARGET

# make sure that any old data in the target database is removed before
# we append in new data.

# rather than using sqlalchemy orm layer to delete tables and models
# to rebuild them, we will use django's management commands to ensure
# that models.py remains definative:

# .\venv\scripts\activate
# reset_db.bat

#========================================
#           README TABLE
table = "readme"

sql = '''SELECT [__README].DATE, [__README].COMMENT, [__README].INIT
        FROM __README
        ORDER BY [__README].DATE DESC;'''

src_cur.execute(sql)
data = src_cur.fetchall()

for row in data:
    item = Readme(
            date =  datetime.datetime.strptime(row['DATE'],
                                               '%Y-%m-%d  %H:%M:%S'),
            comment = row['COMMENT'],
            initials = row['INIT'])
    session.add(item)

session.commit()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))



#========================================
#           SPECIES TABLE
table = "species"

sql = '''SELECT SPC.SPC, SPC.SPC_NM, SPC.SPC_NMSC
         FROM FS_Events INNER JOIN SPC ON FS_Events.SPC = SPC.SPC
         GROUP BY SPC.SPC, SPC.SPC_NM, SPC.SPC_NMSC;'''

src_cur.execute(sql)
data = src_cur.fetchall()

for row in data:
    item = Species(species_code = row['SPC'],
            common_name = row['SPC_NM'],
            scientific_name = row['SPC_NMSC'])
    session.add(item)

session.commit()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))




#========================================
#           STRAINS TABLE
table = "strains"

sql='''SELECT TL_Strains.SPC, TL_Strains.STO, TL_Strains.StrainCode,
       TL_Strains.StrainName
      FROM TL_Strains;'''


src_cur.execute(sql)
data = src_cur.fetchall()

allspc = session.query(Species)

for row in data:
   spc = allspc.filter_by(species_code=row['SPC']).one()
   spc.strains.extend([Strain(sto_code= row['STO'].upper(),
                                strain_code= row['StrainCode'].upper(),
                                strain_name= row['StrainName'])])

session.commit()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))


#========================================
#         PROPONENT TABLE
table = "Proponents"

sql = '''SELECT TL_ProponentNames.Short AS abbrev,
         TL_ProponentNames.PROPONENT_NAME_is AS name
   FROM TL_ProponentNames
   GROUP BY TL_ProponentNames.Short, TL_ProponentNames.PROPONENT_NAME_is,
         TL_ProponentNames.Preferred
   HAVING (((TL_ProponentNames.Preferred)=1));'''


src_cur.execute(sql)
data = src_cur.fetchall()

for row in data:
    item = Proponent(abbrev = row['abbrev'],
            proponent_name = row['name'])
    session.add(item)

session.commit()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))



#========================================
#        STOCKING SITES
table = "Stocking Sites"

sql = '''SELECT SITE_ID, SITE_NAME, STKWBY, STKWBY_LID, UTM, GRID,
             DD_LAT, DD_LON, BASIN, DESWBY_LID, DESWBY
         FROM FS_Events
         GROUP BY SITE_ID, SITE_NAME, STKWBY, STKWBY_LID, UTM, GRID,
             DD_LAT, DD_LON, BASIN, DESWBY_LID, DESWBY;'''

src_cur.execute(sql)
data = src_cur.fetchall()

for row in data:
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
        geom = WKTSpatialElement(pt),
        )
    session.add(item)

session.commit()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))


#========================================
#        LOTS TABLE
table = "Lots"
#note - query aggregates by strain, spawn year, rearing location
# and does not include project code or year -

sql = '''SELECT LOT, SPC, STO, SPAWN_YEAR, REARLOC, REARLOC_NM,
         PROPONENT_NAME as abbrev, PROPONENT_TYPE FROM FS_Lots
         GROUP BY LOT, SPC, STO, SPAWN_YEAR, REARLOC, REARLOC_NM,
         PROPONENT_NAME, PROPONENT_TYPE;'''


src_cur.execute(sql)
data = src_cur.fetchall()

for row in data:
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
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))


#========================================
#       STOCKING EVENTS

table = "Events"

##MS ACCESS SYNTAX:
#sql = '''SELECT FS_Events.Spc, FS_Lots.SPAWN_YEAR, FS_Events.LOT,
#            FS_Events.SITE_ID, FS_Events.PRJ_CD, FS_Events.Event AS fs_event,
#            FS_Events.LOTSAM, FS_Events.Event_Date, FS_Events.CLIPA,
#            FS_Events.FISH_AGE, FS_Events.STKCNT, FS_Events.FISH_WT,
#            FS_Events.RECORD_BIOMASS_CALC, FS_Events.REARTEM, FS_Events.SITEM,
#            FS_Events.TRANSIT_MORTALITY_COUNT AS mortality, FS_Events.DD_LAT,
#            FS_Events.DD_LON,
#            IIf(IsNull([FS_EVENTS].[DEV_CODE]),99,[FS_Events].[DEV_CODE]) AS
#            DEV_CODE, FS_Events.TRANSIT, FS_Events.METHOD, FS_Events.STKPUR
#            FROM FS_Lots INNER JOIN FS_Events ON (FS_Lots.SPC = FS_Events.SPC)
#            AND (FS_Lots.LOT= FS_Events.LOT)
#            AND (FS_Lots.PRJ_CD = FS_Events.PRJ_CD);'''


#SQLITE SYNTAX:

sql = '''SELECT FS_Events.Spc, FS_Lots.SPAWN_YEAR, FS_Events.LOT,
            FS_Events.SITE_ID, FS_Events.PRJ_CD, FS_Events.Event AS fs_event,
            FS_Events.LOTSAM, FS_Events.Event_Date, FS_Events.CLIPA,
            FS_Events.FISH_AGE, FS_Events.STKCNT, FS_Events.FISH_WT,
            FS_Events.RECORD_BIOMASS_CALC, FS_Events.REARTEM, FS_Events.SITEM,
            FS_Events.TRANSIT_MORTALITY_COUNT AS mortality, FS_Events.DD_LAT,
            FS_Events.DD_LON,
            CASE WHEN [FS_EVENTS].[DEV_CODE] is NULL THEN 99
            ELSE [FS_EVENTS].[DEV_CODE] END as DEV_CODE,
            DEV_CODE, FS_Events.TRANSIT, FS_Events.METHOD, FS_Events.STKPUR
            FROM FS_Lots INNER JOIN FS_Events ON (FS_Lots.SPC = FS_Events.SPC)
            AND (FS_Lots.LOT= FS_Events.LOT)
            AND (FS_Lots.PRJ_CD = FS_Events.PRJ_CD);'''


src_cur.execute(sql)
data = src_cur.fetchall()

for row in data:
    pt = "POINT(%s %s)" % (row['DD_LON'], row['DD_LAT'])
    #get objects referenced by foreign key
    spc = session.query(Species).filter_by(species_code=row['SPC']).one()
    lot = session.query(Lot).filter_by(species_id=spc.id,
                                       fs_lot=row['lot'],
                                       spawn_year=row['spawn_year']).one()
    site = session.query(StockingSite).filter_by(
        fsis_site_id=row['site_id']).one()
    item = Event(
        lot_id = lot.id,
        site_id = site.id,        
        prj_cd =  row['prj_cd'],
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
        development_stage = row['dev_code'],
        transit = upper_or_none(row['transit']),
        stocking_method = upper_or_none(row['method']),
        stocking_purpose = upper_or_none(row['stkpur']),
        dd_lat = row['dd_lat'],
        dd_lon = row['dd_lon'],
        geom = WKTSpatialElement(pt),        
    )
    session.add(item)

session.commit()

now = datetime.datetime.now()
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))





#========================================
#       TAGGING EVENTS

table = "Tagging Events"

sql = '''SELECT EVENT AS fs_event, TAG_ID, RETENTION_RATE_PCT,
            RETENTION_RATE_SAMPLE_SIZE, RETENTION_RATE_POP_SIZE,
            COMMENTS, TAG_TYPE_CODE, TAG_POSITION, TAG_ORIGIN_CODE,
            TAG_COLOUR_CODE
         FROM FS_TagAttributes;'''

src_cur.execute(sql)
data = src_cur.fetchall()

for row in data:
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
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))





#========================================
#       CWTs APPLIED

table = "CWTs Applied"

sql = ''' SELECT TAG_ID AS fs_tagging_event_id, CWT
          FROM FS_CWTs_Applied;'''


src_cur.execute(sql)
data = src_cur.fetchall()

for row in data:
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
print "'%s' Transaction Complete (%s)"  % \
  (table, now.strftime('%Y-%m-%d %H:%M:%S'))


#========================================
#              BUILD DATE
build_date = BuildDate(build_date = datetime.datetime.utcnow())
session.add(build_date)
session.commit()

print "All Migrations Complete ({0})".format(build_date)

