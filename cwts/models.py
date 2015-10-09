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

from datetime import datetime

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

    #a field to hold the text that will be displayed when we click on
    #a stocking site - saving it as a field reduces the number of
    #database queries when the pages are rendered.
    popup_text = models.CharField(max_length=2500)


    objects = models.GeoManager()


    def save(self, *args, **kwargs):
        '''When we save each cwt, populate the popup_text field.'''
        self.popup_text = self.get_popup_text()
        super(CWT_recovery, self).save( *args, **kwargs)


    def __unicode__(self):
        '''the string method of the cwt_recovery will be the composite key -
        it should be unique and refer to an individual row in one of our
        databases.'''

        return self.composite_key


    def get_popup_text(self):
        """The popup text method for a cwt recovery should include basic
        information about that recovery including the recovery source,
        recovery date/year, the cwt, the age and size of the fish and
        the composite key corresponding to the record one of our
        master databases.
        """

        base_string = """
                <table class="table">
                      <tr>
                        <td><b>CWT:</b></td>
                        <td>{cwt}</td>
                      </tr>
                      <tr>
                        <td>  <b>Source:</b></td>
                        <td> {source} </td>
                      </tr>
                      <tr>
                        <td>  <b>Recovery Date:</b></td>
                        <td> {recovery_date}</td>
                      </tr>
                      <tr>
                        <td>  <b>Key:</b></td>
                        <td> {key} </td>
                      </tr>
                      <tr>
                        <td>  <b>Fork Length:</b></td>
                        <td> {flen} </td>
                      </tr>
                      <tr>
                        <td>  <b>Age:</b></td>
                        <td> {age} </td>
                      </tr>
                    </table>"""


        if self.recovery_date:
            recovery_date = self.recovery_date.strftime('%b. %d, %Y')
        else:
            recovery_date = self.recovery_year

        value_dict = {
            'cwt':self.cwt,
            'source':self.get_recovery_source_display(),
            'recovery_date': recovery_date,
            'key':self.composite_key,
            'flen':self.flen,
            'age':self.age
        }

        return base_string.format(**value_dict)




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

    #a field to hold the text that will be displayed when we click on
    #a stocking site - saving it as a field reduces the number of
    #database queries when the pages are rendered.
    popup_text = models.CharField(max_length=5000)


    def save(self, *args, **kwargs):
        '''When we save each cwt, populate the popup_text field.'''
        self.popup_text = self.get_popup_text()
        super(CWT, self).save( *args, **kwargs)


    def __unicode__(self):
        '''the string method of the cwt objects returns as
        expected - dashes bentween the second and third and fourth and fifth
        digits.'''

        cwt = str(self.cwt)
        string = '-'.join((cwt[:2], cwt[2:4], cwt[4:]))
        return string


    def get_popup_text(self):
        """The popup text for a cwt recovery should include all of the basic
        information about a cwt stocked by an agency - species,
        strain, agency, year class, stocking location, tag count.
        """

        base_string = """
                <table class="table">
                      <tr>
                        <td><b>CWT:</b></td>
                        <td>{cwt}</td>
                      </tr>
                      <tr>
                        <td>  <b>Species:</b></td>
                        <td> {common_name}
                          (<em>{scientific_name}</em>) </td>
                      </tr>
                      <tr>
                        <td>  <b>Strain:</b></td>
                        <td> {strain_display} ({strain})</td>
                      </tr>
                      <tr>
                        <td>  <b>Year Class:</b></td>
                        <td> {year_class} </td>
                      </tr>
                      <tr>
                        <td>  <b>Stocking Year:</b></td>
                        <td> {stock_year} </td>
                      </tr>
                      <tr>
                        <td>  <b>Life Stage:</b></td>
                        <td> {development_stage} </td>
                      </tr>
                      <tr>
                        <td>  <b>Clip Applied:</b></td>
                        <td> {clipa} </td>
                      </tr>
                      <tr>
                        <td>  <b>Stocking Location:</b></td>
                        <td> {plant_site} </td>
                      </tr>
                      <tr>
                        <td>  <b>Tag Count:</b></td>
                        <td> {tag_cnt:,} </td>
                      </tr>
                      <tr>
                        <td>  <b>Agency:</b></td>
                        <td> {agency} </td>
                      </tr>
                      <tr>
                        <td>  <b>Hatchery:</b></td>
                        <td> {hatchery} </td>
                      </tr>
                      <tr>
                        <td>  <b>Tag Manufacturer:</b></td>
                        <td> {manufacturer} </td>
                      </tr>
                      <tr>
                        <td>  <b>Tag Type:</b></td>
                        <td> {tag_type} </td>
                      </tr>
                      {sequential_string}
                      <tr>
                        <td>  <b>CWT Reused:</b></td>
                        <td> {cwt_reused} </td>
                      </tr>
                      <tr>
                        <td>  <b>Comments:</b></td>
                        <td> {comments} </td>
                      </tr>
                    </table>"""

        if self.tag_type == 17:
            sequential_string = """ <tr>
                       <td>  <b>Sequence Range:</b></td>
                        <td> {} - {} </td>
                      </tr>""".format(self.seq_start, self.seq_end)
        else:
            sequential_string = ""


        tag_cnt = self.tag_cnt if self.tag_cnt else 0

        value_dict = {'cwt':self.cwt,
                      'sequential_string':sequential_string,
                      'common_name':self.spc.common_name,
                      'scientific_name':self.spc.scientific_name,
                      'strain_display':self.get_strain_display(),
                      'strain': self.strain,
                      'year_class':self.year_class,
                      'stock_year':self.stock_year,
                      'development_stage':self.get_development_stage_display(),
                      'clipa':self.clipa,
                      'plant_site':self.plant_site,
                      'tag_cnt':tag_cnt,
                      'agency':self.agency,
                      'hatchery':self.hatchery,
                      'manufacturer':self.get_cwt_mfr_display(),
                      'tag_type':self.get_tag_type_display(),
                      'cwt_reused':self.cwt_reused,
                      'comments':self.comments,

        }

        return base_string.format(**value_dict)


    def age_at_capture(self):
        """return a tuple of two element tuples - respresenting the age of
        fish with this cwt would have been between stocking year and now"""

        yc = self.year_class
        if yc is None:
            return None

        this_year = datetime.now().year

        if this_year < yc:
            return None
        else:
            yrs = range(yc, this_year + 1)
            aac = list(enumerate(yrs, start=0))
            aac.sort(reverse=True, key=lambda x: x[1])
            return aac
