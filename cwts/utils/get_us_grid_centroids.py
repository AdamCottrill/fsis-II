'''=============================================================
c:/1work/Python/djcode/fsis2/cwts/utils/get_us_grid_centroids.py
Created: 23 Nov 2013 09:11:40


DESCRIPTION:

This script calculates the centroid of the 10-minute grids from the
shapefile ~/Grids_10_Minute_No_Island_Bounds.shp and then write the
centroids and their associated grid number into the fish stocking
django database.  these values are use to provide approximate stocking
locations for American CWTs (since we have grid, but not lat-long.)


A. Cottrill
=============================================================

'''


import fiona
import psycopg2
from shapely.geometry import Polygon


DEPLOY = False
REMOTE_IP = '142.143.160.56'

DBASE = 'fsis2'
PG_USER = 'cottrillad'
PG_PW = 'django'


shp = ("E:/LHMU_GIS/Lake_Huron_GIS_new/Base_Layers/Great_Lakes/"
       "Grid_Layers/MI_Waters/Grids_10_Minute_No_Island_Bounds.shp")

centroids = []

#open the shapefile, get the grid identifier, extract the geometry
#elements, calculate the centroid for each polygon and then write the
#grid, lat and lon into a dictionary we can use to append into
#postgres.
with fiona.open(shp) as c:
    for item in c:
        grid = item['properties']['Grid_Strng']
        geom = item['geometry']
        centroid = Polygon(geom['coordinates'][0]).centroid
        ddlat = centroid.y
        ddlon = centroid.x
        centroids.append({'grid': grid, 'ddlat': ddlat, 'ddlon': ddlon})
#check
print(centroids[0])


#now connect to our postgres database and insert the records.
if DEPLOY:
    PG_HOST = REMOTE_IP
else:
    PG_HOST = 'localhost'

pgconstr = "host={0} dbname={1} user={2} password = {3}".format(
        PG_HOST, DBASE, PG_USER, PG_PW)


pgconn = psycopg2.connect(pgconstr)
pgcur = pgconn.cursor()


sql = """INSERT INTO cwts_usgrid (us_grid_no, geom)
         VALUES(%(grid)s,
         ST_SetSRID(ST_MakePoint(%(ddlon)s, %(ddlat)s), 4326));"""

pgcur.executemany(sql, centroids)
pgconn.commit()

print("done!")
pgcur.close()
pgconn.close()
