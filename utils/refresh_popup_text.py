'''=============================================================
~/fsis2/utils/refresh_popup_text.py
Created: 09 Aug 2016 14:24:47

DESCRIPTION:

This script automates the generation of the pop-up text associated
with stocking sites and stocking events.

It is meant to be run from within a django shell that is
connected/associated with the appropriate version of FSIS2 (ie -
controlled through --settings argument to manage.py) after all of the
data has been appended into the database.

ipython usage:
%run ./utils/refresh_popup_text.py

A. Cottrill
=============================================================

'''

from fsis2.models import StockingSite, Event

print('Updating stocking sites...')
objects = StockingSite.objects.all()
for obj in objects:
    obj.save()

print('Updating stocking events...')
objects = Event.objects.all()
for obj in objects:
    obj.save()

print('Done!!')
