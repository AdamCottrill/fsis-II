'''=============================================================
c:/1work/Python/djcode/fsis2/cwts/utils/get_cwt_data.py
Created: 21 Nov 2013 11:39:01

DESCRIPTION:

#this script migrates data from 'cwt master' and inserts into the
#database associated with a django application (cwts).  The US and
#Ontario tags are imported seperately and appended into the same
#table.  The US tags come from a table "~/US_CWTs/WhatThe_USCWTS.mdb"
#while the ontario tags are derived from a query in
#~/CWTcodes_InventoryUGLMUv1.mdb

# if DEPLOY==False, the data will be inserted into the local postgres
# instance.  If DEPLOY==TRUE, the cwt data will be inserted into the
# postgres server on the remote desktop machine.

A. Cottrill
=============================================================

'''

#import adodbapi
import pyodbc
import psycopg2

DBASE = 'fsis2'
PG_USER = 'cottrillad'
PG_PW = 'django'

DEPLOY = False
REMOTE_IP = '142.143.160.56'

def drop_cwts_cwt(pgconstr):
    """'a helper function to drop table cwts_cwt.'

    Arguments: - `constr`: connection string required for postgres
    server in question

    """
    #constr = "dbname={0} user={1}".format('fsis2', 'adam')
    pgconn = psycopg2.connect(pgconstr)
    pgcur = pgconn.cursor()

    #pgcur.execute("DROP TABLE cwts_cwt")
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


def get_us_grid_id(us_grid_no, constr):
    '''a little helper function to get the id number or us grids from
    the lookup table in cwt

    '''
    #constr = "dbname={0} user={1}".format('fsis2', 'adam')
    pgconn = psycopg2.connect(constr)
    pgcur = pgconn.cursor()
    sql = "select id from cwts_usgrid where us_grid_no='{0}'"
    sql = sql.format(us_grid_no)
    pgcur.execute(sql)
    try:
        result = pgcur.fetchall()[0]
    except IndexError:
        result = None
    pgcur.close()
    pgconn.close()

    return result



print("Retrieving US tags...")

#usdbase = 'C:/1work/LakeTrout/Stocking/CWTs/US_CWTs/WhatThe_USCWTS.mdb'
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
uscur.execute('exec Get_US_TagData_for_Django')
result = uscur.fetchall()

col_names = [i[0] for i in uscur.description]
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
drop_cwts_cwt(pgconstr)

pgconn = psycopg2.connect(pgconstr)
pgcur = pgconn.cursor()

reused_index = [x.lower() for x in col_names].index('cwt_reused')
spc_index = [x.lower() for x in col_names].index('spc')
grid_index = [x.lower() for x in col_names].index('us_grid_no')
#rename the column for species to 'spc_id'
col_names[spc_index] = 'spc_id'
col_names[grid_index] = 'us_grid_no_id'

for row in result:
    spc_code = row.Spc
    spc_id = get_spc_id(spc_code, pgconstr)

    us_grid = row.us_grid_no
    us_grid_id = get_us_grid_id(us_grid, pgconstr)

    values = [x for x in row]

    values[spc_index] = spc_id
    values[grid_index] = us_grid_id
    #convert reused from 0/-1 to False/True
    values[reused_index] = False if values[reused_index]==0 else True

    sql = '''insert into cwts_cwt ({0}) values ({1})'''.format(
        ", ".join(col_names).lower(),
        ",".join(['%s']*len(col_names))
    )
    pgcur.execute(sql, values)

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

result = cur.fetchall()

col_names = [i[0] for i in cur.description]
#print col_names
#print result[0]
print('{0} records found'.format(len(result)))

cur.close()
conn.close()

#now connect to postges and insert the us cwt data into the cwt table

#constr = "dbname={0} user={1}".format('fsis2', 'adam')
pgconn = psycopg2.connect(pgconstr)
pgcur = pgconn.cursor()


reused_index = [x.lower() for x in col_names].index('cwt_reused')
spc_index = [x.lower() for x in col_names].index('spc')
stocked_index = [x.lower() for x in col_names].index('stocked')
#rename the column for species to 'spc_id'
col_names[spc_index] = 'spc_id'

for row in result:
    spc_code = row.SPC
    spc_id = get_spc_id(spc_code, pgconstr)

    values = [x for x in row]
    values[spc_index] = spc_id
    #convert reused from 0/-1 to False/True
    values[reused_index] = False if values[reused_index]==0 else True
    values[stocked_index] = False if values[stocked_index]==0 else True

    sql = '''insert into cwts_cwt ({0}) values ({1})'''.format(
        ", ".join(col_names).lower(),
        ",".join(['%s']*len(col_names))
    )
    pgcur.execute(sql, values)

print('Done inserting OMNR tags.')
pgconn.commit()
pgcur.close()
pgconn.close()
print('OMNR tags committed and connection closed.')
