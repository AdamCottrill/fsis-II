'''=============================================================
c:/1work/Python/djcode/fsis2/deploy.py
Created: 09 Oct 2013 08:49:36

DESCRIPTION:

This script is intended to be used for deployment of django projects
to the internal server.  (Essenially it replaces the original git
post-recieve hook.)  All of the directories and files listed in the
source directory (src_dir) will be mirrored in target directory
(trg_dir).

Usage:
From a command prompt: python deploy.py


A. Cottrill
=============================================================

'''

#here are the root directories for the source and target 
src_dir = 'c:/1work/Python/djcode/fsis2/'
trg_dir = 'x:/djcode/fsis2/'

#here are the directories that will be mirrored on trg_dir
dirs = ['fsis2', 'main', 'staticfiles', 'templates', 'utils']

#these are files in the root directory that will be copied too:
files = ['django_settings.py', 'manage.py', 'reset_db.bat']


#===========================
# a helper function that will do all of the work for us

import shutil 
import os

def recursive_overwrite(src, dest, ignore=None):
    '''a helper function blatantly stolen from mgrant's answer on
    stackoverflow: http://stackoverflow.com/questions/12683834/
    '''
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
    else:
        shutil.copyfile(src, dest)


#===========================
# deploy the files and directories        
        
for dir in dirs:
    src = os.path.join(src_dir,dir)
    trg = os.path.join(trg_dir,dir)
    print "copying {0} to {1}".format(src,trg)
    recursive_overwrite(src=src, dest=trg)
    #shutil.rmtree(trg)
    #shutil.copytree(src=src, dst=trg)
    #deploy(src=src, dest=trg)

for fname in files:
    src = os.path.join(src_dir,fname)
    trg = os.path.join(trg_dir,fname)
    print "copying {0} to {1}".format(src,trg)
    recursive_overwrite(src=src, dest=trg)

print "Done!"
