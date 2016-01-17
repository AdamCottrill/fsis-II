'''=============================================================
c:/1work/Python/djcode/fsis2/cwts/utils/get_cwt_data.py
Created: 21 Nov 2013 11:39:01

DESCRIPTION:

# this script migrates data from 'cwt master' and inserts into the
# database associated with a django application (cwts).  The US and
# Ontario tags are imported seperately and appended into the same
# table.  The US tags come from a table "~/US_CWTs/WhatThe_USCWTS.mdb"
# while the ontario tags are derived from a query in
# ~/CWTcodes_InventoryUGLMUv1.mdb

# if DEPLOY==False, the data will be inserted into the local postgres
# instance.  If DEPLOY==TRUE, the cwt data will be inserted into the
# postgres server on the remote desktop machine.

A. Cottrill
=============================================================

'''

import pyodbc
import psycopg2

DBASE = 'fsis2'
PG_USER = 'cottrillad'
PG_PW = 'django'

DEPLOY = False
REMOTE_IP = '142.143.160.51'

def truc_cwts_cwt(pgconstr):
    """'a helper function to clear data out of the table [cwts_cwt].'

    Arguments: - `constr`: connection string required for postgres
    server in question

    """
    pgconn = psycopg2.connect(pgconstr)
    pgcur = pgconn.cursor()

    pgcur.execute("TRUNCATE TABLE cwts_cwt")

    pgconn.commit()
    pgcur.close()
    pgconn.close()

    return None

def get_spc_id(species_code, pgconstr):
    """'a helper function to get the id number for a given species
    code.  the id number is queried from the species table in fsis2
    application.'
    Arguments: - `spc_code`:

    """
    #constr = "dbname={0} user={1}".format('fsis2', 'adam')
    pgconn = psycopg2.connect(pgconstr)
    pgcur = pgconn.cursor()
    sql = "select id from fsis2_species where species_code={0}"
    sql = sql.format(species_code)
    pgcur.execute(sql)
    try:
        result = pgcur.fetchall()[0]
    except IndexError:
        result = None
    pgcur.close()
    pgconn.close()

    return result

print("Retrieving US tags...")

usdbase = "C:/1work/LakeTrout/Stocking/CWTs/US_CWTs/WhatThe_USCWTS.mdb"

#============================================
# get the database locations
constr =r'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={};'
constr = constr.format(usdbase)

# connect to the database
usconn = pyodbc.connect(constr)
# create a cursor
uscur = usconn.cursor()

#use this query when live:
uscur.execute('exec Get_US_TagData_for_Django2')
result = uscur.fetchall()

#col_names = [i[0] for i in uscur.description]
col_names = [i[0].lower() for i in uscur.description]
print('{0} records found'.format(len(result)))

uscur.close()
usconn.close()


#build the appropriate connection string depending on which PG
#instance we want to connect to.
if DEPLOY:
    PG_HOST = REMOTE_IP
else:
    PG_HOST = 'localhost'
pgconstr = "host={0} dbname={1} user={2} password = {3}".format(
        PG_HOST, DBASE, PG_USER, PG_PW)


#Clean out the old data:
trunc_cwts_cwt(pgconstr)

pgconn = psycopg2.connect(pgconstr)
pgcur = pgconn.cursor()

#this sql string is scary looking, but can be easily built/updated
#based on contents of col_names.  The format is required to allow a
#point to be created from ddlat and ddlon using dictionary
#substitution.

sql = """
INSERT INTO cwts_cwt
(
  stocked,
  cwt,
  seq_start,
  seq_end,
  cwt_mfr,
  cwt_reused,
  spc_id,
  strain,
  development_stage,
  year_class,
  stock_year,
  plant_site,
  ltrz,
  agency,
  hatchery,
  tag_cnt,
  clipa,
  tag_type,
  comments,
  us_grid_no,
  release_basin,
  popup_text,
  geom
)
VALUES
(
  %(stocked)s,
  %(cwt)s,
  %(seq_start)s,
  %(seq_end)s,
  %(cwt_mfr)s,
  %(cwt_reused)s,
  %(spc_id)s,
  %(strain)s,
  %(development_stage)s,
  %(year_class)s,
  %(stock_year)s,
  %(plant_site)s,
  %(ltrz)s,
  %(agency)s,
  %(hatchery)s,
  %(tag_cnt)s,
  %(clipa)s,
  %(tag_type)s,
  %(comments)s,
  %(us_grid_no)s,
  %(release_basin)s,
  %(popup_text)s,
  ST_SetSRID(ST_MakePoint (%(ddlon)s,%(ddlat)s),4326)
);
"""

for row in result:
    data = {key: value for (key, value) in zip(col_names, row)}
    data['spc_id'] = get_spc_id(data['spc'], pgconstr)
    #add a placeholder for popup_text - updated later
    data['popup_text'] = data['cwt']
    pgcur.execute(sql, data)

print('Done inserting US tags.')
pgconn.commit()
pgcur.close()
pgconn.close()
print('US tags committed and connection closed.')


#============================================
# get the database locations

dbase = ("Y:/Information Resources/Dataset_Utilities/FS_Maker/"
         "CWTledger/CWTcodes_InventoryUGLMUv1.mdb")
#dbase = ("C:/1work/ScrapBook/CWTcodes_InventoryUGLMUv1.mdb")

constr =r'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={};'
constr = constr.format(dbase)

# connect to the database
print("Retrieving OMNR tags...")

#conn = adodbapi.connect(constr)
conn = pyodbc.connect(constr)
# create a cursor
#try the lookup tables first - keep things simple
cur = conn.cursor()
cur.execute('exec Get_CWT_Data_Django')
col_names = [i[0].lower() for i in cur.description]

result = cur.fetchall()
print('{0} records found'.format(len(result)))

cur.close()
conn.close()

#now connect to postges and insert the us cwt data into the cwt table

sql = """
INSERT INTO cwts_cwt
(
  stocked,
  cwt,
  seq_start,
  seq_end,
  cwt_mfr,
  cwt_reused,
  spc_id,
  strain,
  development_stage,
  year_class,
  stock_year,
  plant_site,
  ltrz,
  agency,
  hatchery,
  tag_cnt,
  clipa,
  tag_type,
  comments,
  release_basin,
  popup_text
)
VALUES
(
  %(stocked)s,
  %(cwt)s,
  %(seq_start)s,
  %(seq_end)s,
  %(cwt_mfr)s,
  %(cwt_reused)s,
  %(spc_id)s,
  %(strain)s,
  %(development_stage)s,
  %(year_class)s,
  %(stock_year)s,
  %(plant_site)s,
  %(ltrz)s,
  %(agency)s,
  %(hatchery)s,
  %(tag_cnt)s,
  %(clipa)s,
  %(tag_type)s,
  %(comments)s,
  %(release_basin)s,
  %(popup_text)s
);
 """


#constr = "dbname={0} user={1}".format('fsis2', 'adam')
pgconn = psycopg2.connect(pgconstr)
pgcur = pgconn.cursor()


for row in result:
    data = {key: value for (key, value) in zip(col_names, row)}
    #convert spc to an int and take the first element returned
    data['spc_id'] = get_spc_id(int(data['spc']), pgconstr)[0]
    #add a placeholder for popup_text - updated later
    data['popup_text'] = data['cwt']
    pgcur.execute(sql, data)


print('Done inserting OMNR tags.')
pgconn.commit()
pgcur.close()
pgconn.close()
print('OMNR tags committed and connection closed.')

print("Don't forget to open a django shell and resave the cwts!")

# from cwts.models import CWT
# cwts = CWT.objects.all()
# for cwt in cwts:
#     cwt.save()
# print('Done populating cwt.popup_text.')
