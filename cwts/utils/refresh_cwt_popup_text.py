'''=============================================================
~/fsis2/cwts/utils/refresh_cwt_popup_text.py
Created: 09 Aug 2016 14:24:47

DESCRIPTION:

This script automates the generation of the pop-up text associated
with cwt and cwt_recovery objects.

It is meant to be run from within a django shell that is
connected/associated with the appropriate version of FSIS2 (ie -
controlled through --settings argument to manage.py)

ipython usage:
%run ./cwts/utils/refresh_cwt_popup_text.py

A. Cottrill
=============================================================

'''

from cwts.models import CWT, CWT_recovery

print('Updating cwt objects...')
cwts = CWT.objects.all()
for cwt in cwts:
    cwt.save()

print('Updating cwt recoveries ...')
cwts = CWT_recovery.objects.all()
for cwt in cwts:
    cwt.save()

print('Done!!')
