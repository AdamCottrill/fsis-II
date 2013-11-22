'''
=============================================================
c:/1work/Python/djcode/fsis2/utils/test_migration.py
Created: 11 Oct 2013 15:34:55

DESCRIPTION:

# We're having trouble with dates and some stocking numbers not being
# populated in postgres. Here we run a some tests on events with known
# dates and stocking counts to verify that they are correct


A. Cottrill
=============================================================
'''

import unittest

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqa_models import *


DEPLOY= False



class TestStockingEvents(unittest.TestCase):

    def check_event(self, event):
        id, stkcnt, date = event

        print "checking {0} - {1} - {2}".format(id, stkcnt, date)        
        msg = "stocking event {0}".format(id)

        errmsg = "".join([msg, " - wrong stkcnt."])
        xx = self.session.query(Event).filter_by(fs_event=id).one()      
        self.assertEqual(xx.stkcnt, stkcnt, errmsg)
        
        event_date = xx.event_date
        errmsg = "".join([msg, " - date is missing."])
        self.assertIsNotNone(event_date, errmsg)
        
        event_date = event_date.replace(tzinfo=None)
        errmsg  = "".join([msg, " - date is wrong."])       
        self.assertEqual(event_date,
                         datetime.datetime.strptime(date, "%m/%d/%Y"),
                         errmsg)

    
    def setUp(self):
        """
        """
        if DEPLOY:
            engine = create_engine('postgresql://adam:django@localhost/fsis2')
        else:
            engine = create_engine('postgresql://COTTRILLAD:uglmu@localhost/fsis2')

        Session = sessionmaker(bind=engine)
        self.session = Session()


    def test_stkcnt_and_dates(self):

        events = [(1800,1000,"04/20/1994"),
                  (2020 ,14792,"04/24/1995"),
                  (6950, 4784, "04/30/2001"),
                  (19030, 19849, "03/27/2008"),
                  (27500, 8388, "05/08/2012")
        ]


        for event in events:
            self.check_event(event)

    

    def tearDown(self):        
        """
        """

        self.session.close()


def main():
    unittest.main()

if __name__ == '__main__':
    main()
        