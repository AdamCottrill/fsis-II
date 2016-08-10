'''=============================================================
~/fsis2/cwts/utils/purge_unused_species.py
Created: 10 Aug 2016 10:05:07

DESCRIPTION:

This script removes any un-used species from the species look-up
table.  When FSIS-II is built, it is populated from the master species
look-up and contains more than 250 species.  This script removes any
species that are not included in the stocking or cwt recovery tables.

This script assumes that the django application and models are
available (e.g. a django shell).  Usage From within ipython:

%run ./cwts/utils/purge_unused_species.py

TODO: update forms to include only those species that have records
associated with the form in question - find stocking sites should only
include species that have actually been stocked.

A. Cottrill
=============================================================

'''

from cwts.models import CWT_recovery
from fsis2.models import Species, Strain, Lot

cwt_spc = set(CWT_recovery.objects.values_list('spc_id', flat=True))
lot_spc = set(Lot.objects.values_list('species_id', flat=True))
strain_spc = set(Lot.objects.values_list('species_id', flat=True))

all_spc = list(cwt_spc | lot_spc | strain_spc)

Species.objects.exclude(id__in=all_spc).delete()
print("Done purging un-used Species objects.")
