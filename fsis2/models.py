import re
#from django.db import models
#from django.contrib.auth.models import User
#from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models

from django.contrib.gis.geos import Point

#from fsis2 import managers


from datetime import datetime


class BuildDate(models.Model):
    '''A database to hold the date that the database was last refreshed.'''
    build_date =  models.DateField(editable=False)

    def __unicode__(self):
        return self.build_date.strftime("%d-%b-%Y")


class Readme(models.Model):
    #a table to hold all of the information regarding last FSIS
    #download and FS_Master rebuild (it appear as a footer on every
    #page)
    date = models.DateField(editable=False)
    comment = models.TextField()
    initials = models.CharField(max_length=4)

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return self.comment


    def get_download_date(self, ):
        """a little function to pull the FSIS download date out of the
        readme string build by Process-FSIS
        """
        regex = "\d{1,2}\-[a-zA-Z]{3}\-\d{4}|\d{1,2}/\d{1,2}/\d{4}"
        datestring = re.search(regex, self.comment)
        if datestring:
            xx = datestring.group()
            try:
                formatted_date = datetime.strptime(xx, "%d-%b-%Y")
                return formatted_date
            except ValueError:
                pass
            try:
                formatted_date = datetime.strptime(xx, "%m/%d/%Y")
                return formatted_date
            except ValueError:
                return None
        else:
            return None


class Species(models.Model):
    species_code = models.IntegerField(unique=True)
    common_name = models.CharField(max_length=30)
    scientific_name = models.CharField(max_length=50, null=True, blank=True)


    class Meta:
        ordering = ['species_code']

    def __unicode__(self):
        if self.scientific_name:
            spc_unicode = "%s (%s)" % (self.common_name, self.scientific_name)
        else:
            spc_unicode =  "%s" % self.common_name
        return spc_unicode

class Strain(models.Model):

    species = models.ForeignKey(Species)
    sto_code = models.CharField(max_length=5) #crap from fsis
    strain_code = models.CharField(max_length=5)
    strain_name = models.CharField(max_length=20)

    class Meta:
        ordering = ['species', 'strain_name']
        #unique_together = ['species_code', 'sto_code']

    def __unicode__(self):
        return "%s %s" % (self.strain_name, self.species.common_name)


class Proponent(models.Model):

    abbrev = models.CharField(max_length=7, unique=True)
    proponent_name =  models.CharField(max_length=50)

    class Meta:
        ordering = ['proponent_name']

    def __unicode__(self):
        return "%s (%s)" % (self.proponent_name, self.abbrev)

    def get_absolute_url(self):
        return ('proponent_detail', (), {'pk':self.id})



class StockingSite(models.Model):
    #many of these should be choice fields or foreign keys to look-up tables
    #eventually they will be replaced with spatial queries
    fsis_site_id =  models.IntegerField(unique=True)
    site_name = models.CharField(max_length=50) #this should be unique
    stkwby  = models.CharField(max_length=30)
    stkwby_lid = models.CharField(max_length=15)
    utm  = models.CharField(max_length=20)
    grid = models.CharField(max_length=4)
    dd_lat = models.FloatField()
    dd_lon = models.FloatField()
    basin = models.CharField(max_length=15)
    deswby_lid  = models.CharField(max_length=30)
    deswby  = models.CharField(max_length=30)

    geom = models.PointField(srid=4326,
                             help_text='Represented as (longitude, latitude)')


    objects = models.GeoManager()

    def __unicode__(self):
        return "%s (%s)" % (self.site_name, self.fsis_site_id)

    class Meta:
        ordering = ['site_name']

    def save(self, *args, **kwargs):
        if not self.geom:
            self.geom = Point(float(self.dd_lon), float(self.dd_lat))
        super(StockingSite, self).save( *args, **kwargs)



class Lot(models.Model):

    #prj_cd = models.CharField(max_length=13)
    #fs_lot  = models.IntegerField()
    fs_lot = models.CharField(max_length=10)
    species = models.ForeignKey(Species)
    strain = models.ForeignKey(Strain)
    spawn_year = models.IntegerField()
    #these should be in their own table
    rearloc = models.CharField(max_length=30)
    rearloc_nm = models.CharField(max_length=30)
    proponent = models.ForeignKey(Proponent)

    PROPONENT_TYPE_CHOICES = (
        ('CFIP', 'CFIP'),
        ('OMNR', 'OMNR'),
        ('PRIVATE', 'Private Hatchery'),
        ('UNKNOWN', 'Unknown'),
        )
     #this should be lower case:
    proponent_type = models.CharField(max_length=10,
                                      choices=PROPONENT_TYPE_CHOICES,
                                      default='OMNR')

    class Meta:
        ordering = ['-spawn_year']


    def __unicode__(self):
        return "%s (%s yc %s)" % (self.fs_lot, self.spawn_year,
                                  self.species.common_name)

    def get_absolute_url(self):
        return reverse('lot_detail', args=[str(self.id)])


    def get_year(self):
            """
            Arguments:
            - `self`:
            """
            '''format LHA_IA12_000 as 2012'''
            x = self.prj_cd
            if int(x[6:8]) > 60:
                yr = "19" + x[6:8]
            else:
                yr = "20" + x[6:8]
            return yr


    def get_event_points(self):
        '''get the coordinates of events associated with this lot.  Returns a
        list of tuples.  Each tuple contains the fs_event id, dd_lat and
        dd_lon'''

        points = Event.objects.filter(lot__id=self.id).values_list(
            'fs_event', 'geom')

        return points

class Event(models.Model):

    lot = models.ForeignKey(Lot)
    prj_cd =  models.CharField(max_length=13)
    year = models.IntegerField()
    fs_event = models.IntegerField(unique=True)
    lotsam = models.CharField(max_length=8, null=True, blank=True)
    event_date = models.DateTimeField(editable=True, null=True, blank=True)
    clipa = models.CharField(max_length=3, null=True, blank=True)
    fish_age = models.IntegerField()
    stkcnt = models.IntegerField()
    fish_wt = models.FloatField(null=True, blank=True)
    record_biomass_calc = models.FloatField(null=True, blank=True)
    reartem = models.FloatField(null=True, blank=True)
    sitem = models.FloatField(null=True, blank=True)
    transit_mortality_count = models.IntegerField(null=True, blank=True)

    site = models.ForeignKey(StockingSite)
    dd_lat = models.FloatField()
    dd_lon = models.FloatField()

    geom = models.PointField(srid=4326,
                             help_text='Represented as (longitude, latitude)')

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
                                      default=99)

    TRANSIT_METHOD_CHOICES = (
        ('ATV','All-terrain vehicle'),
        ('BOAT','Boat'),
        ('PLANE','Fixed wing Airplane'),
        ('TUG','Great Lakes Tug'),
        ('HELICOPTER','Helicopter'),
        ('INCUBATOR','In-stream incubation'),
        ('BACKPACK','Personal backpack'),
        ('SNOWMOBILE','Snowmobile'),
        ('TRUCK','Truck'),
        ('UNKNOWN','Unknown'), )
    transit = models.CharField(max_length=20,
                                      choices=TRANSIT_METHOD_CHOICES,
                                      default='UNKNOWN',
                                      null=True, blank=True)

    STOCKING_METHOD_CHOICES = (
        ('AERIAL DROP','Areal Drop'),
        ('ICE','Under Ice'),
        ('SUBMERGED','Submerged'),
        ('SUBSURFACE','Subsurface'),
        ('SURFACE','surface'),
        ('UNKNOWN','Unknown'),
        )
    stocking_method  = models.CharField(max_length=20,
                                      choices=STOCKING_METHOD_CHOICES,
                                      default='UNKNOWN',
                                      null=True, blank=True)

    STOCKING_PURPOSE_CHOICES = (
        ('UNKN', 'Unknown'),
        ('A', 'Rehabilitation'),
        ('AC', 'Rehabilitation/Supplemental'),
        ('AD', 'Rehabilitation/Research'),
        ('AE', 'Rehabilitation/Assessment'),
        ('B', 'Introduction'),
        ('C', 'Supplemental'),
        ('D', 'Research'),
        ('DI', 'Research/Re-Introduction'),
        ('EG', 'Assessment/Put-Grow-and-Take'),
        ('EI', 'Assessment/Re-introduction'),
        ('F', 'Put-and-Take'),
        ('G', 'Put-Grow-and Take'),
        ('I', 'Re-introduction'),
        )

    stocking_purpose =  models.CharField(max_length=4,
                                      choices=STOCKING_PURPOSE_CHOICES,
                                      default='UNKNOWN',
                                      null=True, blank=True)
    objects = models.GeoManager()

    class Meta:
        ordering = ['-event_date']

    def __unicode__(self):
        return 'fsis event : %s' % self.fs_event

    def get_absolute_url(self):
        return ('event_detail', (), {'pk':self.id})


    def save(self, *args, **kwargs):
        if not self.geom:
            self.geom = Point(float(self.dd_lon), float(self.dd_lat))
        super(Event, self).save( *args, **kwargs)


    def get_cwts(self):
        '''a simple method to get all of the cwts associated with a stocking
        event. (this should be optimized, but for now it works.)'''

        cwts=[]
        te = self.taggingevent_set.values_list('id')
        if te:
            cwts = CWTs_Applied.objects.filter(tagging_event__in=te)
        return cwts

    def get_year(self):
        '''a function to grab the year from the project code
        associated with the stocking event.  We don\'t always have a
        date so we have to use project code.'''

        yr = datetime.strptime(self.prj_cd[6:8], '%y').year
        return(yr)


class TaggingEvent(models.Model):
    stocking_event= models.ForeignKey(Event)
    fs_tagging_event_id = models.IntegerField(unique=True)
    retention_rate_pct = models.FloatField(null=True, blank=True)
    retention_rate_sample_size = models.IntegerField(null=True, blank=True)
    retention_rate_pop_size = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    TAG_TYPE_CHOICES = (
        (1, 'Streamer'),
        (2, 'Tubular Vinyl'),
        (5, 'Anchor'),
        (6, 'Coded Wire'),
        (17, 'Sequential_CWT')
        )

    tag_type =  models.IntegerField(choices=TAG_TYPE_CHOICES,
                                     default=6)

    TAG_POSITION_CHOICES = (
        (1, 'Flesh of Back'),
        (2, 'Operculum'),
        (3, 'Posterior Dorsal Fins'),
        (4, 'Snout'),
        )

    tag_position =  models.IntegerField(
                                     choices=TAG_POSITION_CHOICES,
                                     default=4)

    TAG_ORIGIN_CHOICES = (
       ('CFP', 'Community Fisheries Involvement Program(CFIP)'),
       ('MNR', 'Ontario Ministry of Natural Resources'),
       )

    tag_origins =  models.CharField(max_length=3,
                                     choices=TAG_ORIGIN_CHOICES,
                                     default='MNR')


    TAG_COLOUR_CHOICES = (
       ('BLK', 'Black'),
       ('BLU', 'Blue'),
       ('GRN', 'Green'),
       ('NON', 'Colourless'),
       ('OTH', 'Other'),
       ('UNK', 'Unknown'),
       ('YEL', 'Yellow'),
       )
    tag_colour =  models.CharField(max_length=3,
                                     choices=TAG_COLOUR_CHOICES,
                                     default='NON')

    def __unicode__(self):
        return 'tagging event :%s' % self.id

       #def get_absolute_url(self):
       #return ('event_detail', (), {'pk':self.id})


class CWTs_Applied(models.Model):
    #tagging = models.ManyToMany(TaggingEvent)
    tagging_event = models.ForeignKey(TaggingEvent)
    fs_tagging_event_id = models.IntegerField()
    cwt = models.CharField(max_length=6)

    def __unicode__(self):
        cwt = str(self.cwt)
        string = '-'.join((cwt[:2], cwt[2:4], cwt[4:]))
        return string

        #def get_absolute_url(self):
        #
        #return ('cwt_events', self.cwt)

    def get_stocking_events(self):
        pass


class LTRZ(models.Model):
    '''a class to hold geometries associated wth lake trout rehab-zones.
    Used to find stocking events, cwts, and cwt recoveries occurred in
    (or potentially near) specific LTRZs.
    '''
    ltrz = models.IntegerField('LTRZ')
    geom = models.MultiPolygonField(srid=26917)

    def __unicode__(self):
        ret = 'LTRZ-{0}'.format(self.ltrz)
        return ret


class QMA(models.Model):
    '''a class to hold geometries associated wth Quota Management Areas.
    Used to find stocking events, cwts, and cwt recoveries that
    occurred in (or potentially near) specific areas.
    '''
    qma = models.CharField('QMA', max_length=6)
    geom = models.MultiPolygonField(srid=26917)

    def __unicode__(self):
        return self.qma
