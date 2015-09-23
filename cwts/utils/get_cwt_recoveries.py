'''=============================================================
c:/1work/Python/djcode/fsis2/cwts/utils/get_cwt_recoveries.py
Created: 23 Nov 2013 15:33:13

DESCRIPTION:

This scripts updates the cwt_recovery table in fsis2 database.
Currently the data is retireved from grandwazoo2, although thought
should be given to collecting the data directly from each of our
master databases.  This script should be re-run each year (or more
often when master databases are updated)

A. Cottrill
=============================================================

'''

#import adodbapi
import pyodbc
import psycopg2

DEPLOY = False
REMOTE_IP = '142.143.160.56'

print("Retrieving  recoveries ...")

dbase = ("C:/1work/LakeTrout/Stocking/CWTs/CWT_Recovery.mdb")
#constr = 'Provider=Microsoft.Jet.OLEDB.4.0; Data Source={0}'.format(dbase)

constr =r'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={};'
constr = constr.format(dbase)


#============================================
# get the database locations

# connect to the database
conn = pyodbc.connect(constr)
# create a cursor
#try the lookup tables first - keep things simple
cur = conn.cursor()

#cur.execute('exec get_cwt_recoveries')

sql = '''SELECT All_Sam_Info.Source, All_BioData.Year AS recovery_year,
      EFFDT1 AS recovery_date, [All_BioData].GRID, [All_BioData].[PRJ_CD]
      & '-' & [All_BioData].[SAM] & '-' & [EFF] & '-' & [SPC] & '-' &
      [GRP] & '-' & [FISH] AS composite, DD_LAT as ddlat, DD_LON as ddlon,
      FLEN, AGE, Mid([TAGID],4,2) & Left([TAGID],2) & Right([TAGID],2) AS cwt
      FROM
      All_Sam_Info INNER JOIN All_BioData ON (All_Sam_Info.SAM =
      All_BioData.SAM) AND (All_Sam_Info.PRJ_CD = All_BioData.PRJ_CD) WHERE
      (((All_BioData.TAGID) Like '%-%-%'));
      '''

cur.execute(sql)

col_names = [x[0].lower() for x in cur.description]

result = cur.fetchall()
#convert the results into a dictionary so we can use named arguments
#to update the database.
result_dict = []
for rec in result:
    result_dict.append(dict(zip(col_names, rec)))

print('{0} records found'.format(len(result)))

cur.close()
conn.close()

#============================================
print("Inserting recoveries into cwt_recoveries")

if DEPLOY:
    #remote
    pgconstr = "host={0} dbname={1} user={2}".format(REMOTE_IP, 'fsis2',
                                                     'adam')
else:
    #local
    pgconstr = "dbname={0} user={1}".format('fsis2', 'adam')


pgconn = psycopg2.connect(pgconstr)
pgcur = pgconn.cursor()

#pgcur.execute("DROP TABLE IF EXISTS cwts_cwt_recover")

sql = '''insert into cwts_cwt_recovery (
             cwt, recovery_year, recovery_date, recovery_grid, recovery_source,
             composite_key, flen, age, geom)
             values (
             %(cwt)s, %(recovery_year)s, %(recovery_date)s, %(grid)s,
             %(source)s, %(composite)s, %(flen)s, %(age)s,
             ST_SetSRID(ST_MakePoint(%(ddlon)s, %(ddlat)s), 4326))'''

pgcur.executemany(sql, result_dict)

print('Done inserting recovered cwts.')
pgconn.commit()
pgcur.close()
pgconn.close()
print('recoveries committed and connection closed.')
