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
#     is formatted either as dd/mm/yyyy, mmm-dd-yyyy or dd-mmm-yyyy.
#     Otherwise it returns None.
#     
#
# A. Cottrill
#=============================================================

import datetime
import unittest

def upper_or_none(x):
    '''a little helper function to ensure that constants enter the
    database in uppercase (or not at all)'''
    if x:
        return x.upper()
    else:
        return None


def datetime_or_none(x):
    '''Another helper function to ensure that dates comming out of the
    fish stocking data base are fomatted properly datetimes (with
    timestamp) or are returned as None.'''
    from datetime import datetime

    if x:

        #04/14/2012
        try:
            x = datetime.strptime(x,'%m/%d/%Y %H:%M:%S.0')
            return(x)
        except ValueError:
            pass
        try:
            x = datetime.strptime(x,'%m/%d/%Y')
            return(x)
        except ValueError:
            pass

        
        #Apr-14-2012
        try:
            x = datetime.strptime(x,'%b-%d-%Y %H:%M:%S.0')
            return(x)
        except ValueError:
            pass
        try:
            x = datetime.strptime(x,'%b-%d-%Y')
            return(x)
        except ValueError:
            pass

        # 14-04-2014
        try:
            x = datetime.strptime(x,'%d-%b-%Y')
            return(x)
        except ValueError:
            pass                
        try:
            x = datetime.strptime(x,'%d-%b-%Y %H:%M:%S.0')
            return(x)
        except ValueError:
            return None
    else:
        return None
            
#[date_time_or_none(x) for x in samples]


class TestDateTimeOrNone(unittest.TestCase):

    def testDifferentDateFormats(self):
        '''Basic unit test to make sure that the function
        datetime_or_none() is able to return a datetime
        object from formatted string objects.  The formats
        returned are not comprehensive, but should cover
        those instances returned by ms access and
        sqlite.
        '''

        from datetime import datetime

        datestring = "04/18/2011"
        dt = datetime.strptime(datestring,'%m/%d/%Y')
        x = datetime_or_none(datestring)
        self.assertEqual(x,dt)

        datestring = "04/18/2011 11:43:32.0"
        dt = datetime.strptime(datestring,'%m/%d/%Y %H:%M:%S.0')
        x = datetime_or_none(datestring)
        self.assertEqual(x,dt)
        
        datestring = "18-Apr-2011"
        dt = datetime.strptime(datestring,'%d-%b-%Y')
        x = datetime_or_none(datestring)
        self.assertEqual(x,dt)

        datestring = "18-Apr-2011 11:43:32.0"
        dt = datetime.strptime(datestring,'%d-%b-%Y %H:%M:%S.0')
        x = datetime_or_none(datestring)
        self.assertEqual(x,dt)

        datestring = "Apr-18-2011"
        dt = datetime.strptime(datestring,'%b-%d-%Y')
        x = datetime_or_none(datestring)
        self.assertEqual(x,dt)

        datestring = "Apr-18-2011 11:43:32.0"
        dt = datetime.strptime(datestring,'%b-%d-%Y %H:%M:%S.0')
        x = datetime_or_none(datestring)
        self.assertEqual(x,dt)
        
        x = datetime_or_none('')
        self.assertIsNone(x)              

        x = datetime_or_none(None)
        self.assertIsNone(x)              

        
def main():
    unittest.main()

if __name__ == '__main__':
    main()
        