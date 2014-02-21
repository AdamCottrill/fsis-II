
'''=============================================================
c:/1work/Python/djcode/fsis2/utils/clone_fs_master.py
Created: 27 Sep 2013 08:48:24

DESCRIPTION:

The purpose of this script is to create a clone of FS_Master.mdb in
sqlite.  FS_master is 32-bit ms access, and is not accessible from the
64-bit desktop machine (if we want to work in 64-bit moving forward).

first step - create a copy of the data structure

loop over the tables in FS_master and then insert the results into the
sqlite clone.

the schema file used by this script was initially generated using
jet-tool.  The sql file was then edited to reflect the relatively
simple datatypes available in sqlite (integer, real and text)

A. Cottrill
=============================================================

'''
import datetime
import pyodbc
import os
import shutil
import sqlite3

#here is where we will place the clone after we make it:
deploy_dir = r'X:/djcode/fsis2/utils/data'

#trg =  r'C:/1work/ScrapBook/clone_fs_master/FS_Master.db'
trg = r'c:/1work/Python/djcode/fsis2/utils/data/fs_master_clone.db'
#recreate the target database:
cmd = 'sqlite3 {0} < FS_master_schema.sql'.format(trg)
os.system(cmd)

#open a connection to our new target database:
trg_conn = sqlite3.connect(trg)
trg_cur = trg_conn.cursor()


#open a connection to the source database and create a cursor
#src = r'C:/1work/ScrapBook/clone_fs_master/FS_Master.mdb'
#src = r"C:/1work/Python/djcode/fsis2/utils/FS_Master_copy.mdb"
src = r"Y:/Information Resources/Dataset_Utilities/FS_Maker/FS_Master.mdb"
src_conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb)};" \
                     "DBQ=%s" % src)
src_cur = src_conn.cursor()


#get the list of tables in the source database:
tables = src_cur.tables()
tables = [row[2] for row in tables if row[3] == 'TABLE']

for table in tables:
    if not table in ("TL_StockingSites", "TL_ActualStockingSites"):
        sql = '''select * from {0}'''.format(table)

        rs = src_cur.execute(sql)
        jj = rs.fetchall()

        fldcnt = len(jj[0])
        sql2 = '''insert into {0} values({1}?)'''.format(
            table, "?," * (fldcnt -1))

        trg_cur.executemany(sql2, jj)
        trg_conn.commit()

        print "Successfully ported {0}".format(table)

src_cur.close()
src_conn.close()

#==========================
#we need to get the species table too:
src = r"Z:/Data Warehouse/Utilities/Code Tables/LookupTables/LookupTables.mdb"
src_conn = pyodbc.connect(r"DRIVER={Microsoft Access Driver (*.mdb)};" \
                     "DBQ=%s" % src)
src_cur = src_conn.cursor()

sql = '''select * from SPC'''
rs = src_cur.execute(sql)
jj = rs.fetchall()

fldcnt = len(jj[0])
sql2 = '''insert into SPC values({0}?)'''.format("?," * (fldcnt -1))

trg_cur.executemany(sql2, jj)
trg_conn.commit()


#some final cleanup
trg_cur.close()
src_cur.close()

trg_conn.close()
src_conn.close()

#
print "Copying clone to deployment directory..."
os.remove(os.path.join(deploy_dir, os.path.split(trg)[1]))
#os.rename(trg,os.path.join(deploy_dir, os.path.split(trg)[1]))
destination = os.path.join(deploy_dir, os.path.split(trg)[1])
shutil.copy(trg, destination)
print "Done! ({0})".format(datetime.datetime.now().strftime("%b-%d-%Y %H:%M"))




