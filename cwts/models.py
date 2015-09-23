'''
for the cwt detail view we need a table much like cwt_master.

It must include the fields:

cwt
species
strain
year class
stocked_year (if possible)
lifestage (if possible)
stocking location
LTRZ
stocking agency (OMNR for now)
sequential (yes/no)
hatchery
comments
'''


from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.contrib.gis.db import models

from fsis2.models import (StockingSite, Proponent, Species, Strain)


class USgrid(models.Model):
    '''Centroids of us 10-minute grids - thee are used as APPROXIMATE
    stocking locations for US cwts.
    '''

    us_grid_no = models.CharField(max_length=4)
    geom = models.PointField(srid=4326,
                             help_text='Represented as (longitude, latitude)')

    objects = models.GeoManager()

    def __unicode__(self):
        return self.us_grid_no


class CWT_recovery(models.Model):
    '''instances of cwt recoveries.  generated from 121 and 125 data
    in Grandwazoo2

    '''

    cwt = models.CharField(max_length=6)
    RECOVERY_SOURCE_CHOICES = (
        ("AOFRC", "AOFRC"),
        ("CF", "Catch Sampling"),
        ("CWT", "CWT Cooperative"),
        ("IA_Nearshore", "Nearshore Index"),
        ("IA_Offshore", "Offshore Index"),
        ("NAWASH", "Nawash"),
        ("SportCreel", "Creels"),
        ("SportFish","Sportfish"),
    )
    recovery_source = models.CharField(max_length=20,
                                       choices=RECOVERY_SOURCE_CHOICES)
    recovery_year = models.IntegerField()
    recovery_date = models.DateField(null=True, blank=True)
    recovery_grid= models.CharField(max_length=4)
    composite_key = models.CharField(max_length=50)
    flen = models.IntegerField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    geom = models.PointField(srid=4326,
                             help_text='Represented as (longitude, latitude)')

    objects = models.GeoManager()


class CWT(models.Model):

    stocked = models.BooleanField()
    cwt = models.CharField(max_length=6)
    seq_start = models.IntegerField(default=0)
    seq_end = models.IntegerField(default=1)
    #spool_cnt = models.IntegerField(default=1)
    tag_cnt = models.IntegerField(null=True, blank=True)
    #date_aqcuired = models.DateField(null=True, blank=True)
    #po =  models.CharField(max_length=10)

    TAG_TYPE_CHOICES = (
        (6,'Coded Wire'),
        (17,'Sequential Coded Wire'),
    )

    tag_type = models.IntegerField(choices=TAG_TYPE_CHOICES,
                                   default=6)

    MANUFACTURER_CHOICES = (
        ('MM', 'Micro Mark'),
        ('NMT', 'Northwest Marine Technologies'),)

    cwt_mfr = models.CharField(max_length=10, choices=MANUFACTURER_CHOICES)
    #cwt_length = models.IntegerField()
    cwt_reused = models.BooleanField()
    #distributed = models.BooleanField()
    #distributed_date = models.DateField(null=True, blank=True)

    #spc is null before tags are distributed
    spc = models.ForeignKey(Species, null=True, blank=True)
    STRAIN_CHOICES = (
        ('BS', 'Big Sound'),
        ('GL', 'Green Lake'),
        ('IB', 'Iroquois Bay'),
        ('JL', 'Jenny Lake'),
        ('LL', 'Lewis Lake'),
        ('LM', 'Lake Manitou'),
        ('LO', 'Lake Ontario'),
        ('MA', 'Marquette'),
        ('MASE', 'Marquette cross'),
        ('MP', 'Michipicoten Island'),
        ('SA', 'Apositle Island'),
        ('SI', 'Superior Isle Royal'),
        ('SN', 'Seneca Lake'),
        ('STI', 'Superior Traverse Island'),
        ('WI', 'Wisconsin'),
        ('MB', 'Mishubishu'),
        ('ST', 'Slate Island'),
        ('UNKN', 'Unknown'),
    )
    #strain is also null before the tags are distributed
    strain = models.CharField(max_length=10,
                              choices=STRAIN_CHOICES,
                              null=True, blank=True)
    #strain = models.ForeignKey(Strain)

    DEVELOPMENT_STAGE_CHOICES = (
        (99, 'Unknown'),
        (10, 'Egg (unknown stage)'),
        (12, 'Eyed Eggs'),
        (31, 'Fry (1-2 months)'),
        (32, 'Fingerling (3-9 months)'),
        (50, 'Juvenile / Adult (unknown age)'),
        (51, 'Yearling (10-19 months)'),
        (52, 'Sub-adult (>= 20 months, but immature)'),
        (53, 'Adult (mature)'),
        (81, 'Sac Fry (0-1 month)'),
        )

    development_stage = models.IntegerField(
                                      choices=DEVELOPMENT_STAGE_CHOICES,
                                      default=99, null=True, blank=True)

    year_class = models.IntegerField(null=True, blank=True)
    stock_year = models.IntegerField(null=True, blank=True)

    #stocking_site = models.ForeignKey(StockingSite)
    plant_site = models.CharField(max_length=80, null=True, blank=True)

    LTRZ_CHOICES = (
        (1, 'Western North Channel'),
        (2, 'Darch Islands'),
        (3, 'Fraser Bay'),
        (4, 'Grand Bank/Dawson Rock'),
        (5, 'Iroquois Bay'),
        (6, 'Parry Sound'),
        (7, 'Limestone Islands'),
        (8, 'Watcher Islands'),
        (9, 'Nottawasaga Bay'),
        (10, 'Owen Sound/Colpoys Bay'),
        (11, 'Point Clark'),
        (12, 'Western Bruce Penninsula'),
        (13, 'Bruce Archipelago'),
        (14, 'SW Manitoulin Island'),
        (15, 'South Bay'),
        (16, 'Six Fathom Bank'),
        (17, 'North Lake Huron Humps'),
    )

    ltrz =  models.IntegerField(choices=LTRZ_CHOICES, null=True, blank=True)
    #other = models.CharField(max_length=100, null=True, blank=True)
    #study_number = models.CharField(max_length=15, null=True, blank=True)
    us_grid_no = models.ForeignKey(USgrid, null=True, blank=True)

    #hatchery = models.ForeignKey(Proponent)
    hatchery = models.CharField(max_length=80, null=True, blank=True)

    AGENCY_CHOICES = (
        ('OMNR', 'Ontario Ministry of Natural Resources'),
        ('MDNR', 'Michigan Department of Natural Resources'),
        ('USFWS', 'U.S. Fish and Wildlife Service'),
    )
    agency = models.CharField(max_length=5, choices=AGENCY_CHOICES)

    comments = models.TextField(null=True, blank=True)

    CLIP_CHOICES = (
        (0, 'No Clip'),
        (1, 'Right Pectoral'),
        (2, 'Left Pectoral'),
        (3, 'Right Pelvic'),
        (4, 'Left Pelvic'),
        (14, 'Right Pectoral and Left Pelvic'),
        (23, 'Left Pectoral and Right Pelvic'),
        (5, 'Adipose'))

    clipa = models.IntegerField(choices=CLIP_CHOICES,
                                      default=5, null=True, blank=True)


    def __unicode__(self):
        cwt = str(self.cwt)
        string = '-'.join((cwt[:2], cwt[2:4], cwt[4:]))
        return string
