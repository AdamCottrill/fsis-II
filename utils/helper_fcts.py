#=============================================================
# c:/1work/Python/djcode/fsis2/utils/helper_fcts.py
# Created: 30 Aug 2013 09:39:45

#
# DESCRIPTION:
#
# This file contains some helper functions that are used by
# migrate_data.py.  In most cases, they are quick and dirty functions
# that format data elements in the manner expected by sqlalchemy or
# the fsis2 data model.
#
# upper_or_none - converts the passed string to uppercase or returns
#     None.  Ensures that constants/choices are passed to database in
#     standard format.
#
# datetime_or_none - if a value is present, it parses assuming that it
#     is formatted either as mmm-dd-yyyy or dd-mmm-yyyy.  Otherwize it
#     returns None.
#
# A. Cottrill
#=============================================================

import datetime


def upper_or_none(x):
    '''a little helper function to ensure that constants enter the
    database in uppercase (or not at all)'''
    if x:
        return x.upper()
    else:
        return None


def datetime_or_none(x):
    '''Another helper function to ensure that dates comming out of the
    fish stocking data base are fomatted properly (or are returned as
    None)'''
    try:
        x = datetime.datetime.strptime(x,'%b-%d-%Y')
        return(x)
    except:
        pass
    try:
        x = datetime.datetime.strptime(x,'%d-%b-%Y')
        return(x)
    except:
        return None

#[date_time_or_none(x) for x in samples]
