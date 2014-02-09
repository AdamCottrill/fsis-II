from datetime import datetime
#from django.contrib.auth.models import User
#from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.core.exceptions import MultipleObjectsReturned

from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.dates import YearArchiveView
from django.views.generic import CreateView, UpdateView
from django.db.models import Sum


from olwidget.widgets import InfoMap, InfoLayer, Map

from .models import (Event, Lot, TaggingEvent, CWTs_Applied, StockingSite,
                     Proponent, Species, Strain, BuildDate, Readme)

from cwts.models import CWT, USgrid, CWT_recovery

from .forms import GeoForm

def timesince(dt, default="just now"):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    from:http://flask.pocoo.org/snippets/33/
    """

    now = datetime.utcnow()
    diff = now - dt
    
    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:
        
        if period:
            return "%d %s ago" % (period, singular if period == 1 else plural)

    return default    


def footer_string():
    '''Build the footer string that indicates when the website
    database as last build and when the data was last downloaded from
    fsis.  This string will appear at the bottom of a number of
    standard views
    '''
    
    build_date = BuildDate.objects.latest('build_date').build_date
    build_date = build_date.strftime("%b-%d-%Y")

    download_date = Readme.objects.latest('date')
    download_date = download_date.get_download_date()
    delta = timesince(download_date) #lapse time
    download_date = download_date.strftime("%b-%d-%Y") #time as a string
        
    ftr_str="FSIS-II built on {0} using data downloaded from FSIS on {1} ({2})"
    ftr_str = ftr_str.format(build_date, download_date, delta)
    return ftr_str
   

def prj_cd_Year(x):
    '''format LHA_IA12_000 as 2012'''
    if int(x[6:8]) > 60:
        yr = "".join(["19", x[6:8]])
    else:
        yr = "".join(["20", x[6:8]])        
    return yr


def get_map(event_points):
    """

    Arguments:
    - `event_points`:
    """
    if len(event_points)>0:
        geoms = [[x[1],x[0]] for x in event_points]
        map = InfoMap(
            geoms,
            {'default_lat': 45,
            'default_lon': -82.0,
            'default_zoom': 7,
            'zoom_to_data_extent': False,
            'map_div_style': {'width': '700px', 'height': '600px'},
            }
            )
    else:
        map=None
    #import pdb; pdb.set_trace()
    return map


def empty_map():
    """
    Arguments:
    - `event_points`:
    """
    map = InfoMap(
        None,
        {'default_lat': 45,
         'default_lon': -82.0,
         'default_zoom': 7,
         'zoom_to_data_extent': False,
         'map_div_style': {'width': '700px', 'height': '600px'}})
    return map



def get_map2(event_points, roi=None):
    """This map function taks a list of points and a region of
    interest and returns a map that is zoomed to spatial extent of the
    roi.  The roi and all of the points it contains are rendered.

    used by views find_events
    
    Arguments: -
    `event_points`: a list of points objects and their event numbers
    'roi': region of interest used to select event points

    """
    layers = []
    zoom_to_extent = False    
    if len(event_points)>0:
        if roi:
            style = {'overlay_style': {'fill_color': '#0000FF',
                               'fill_opacity': 0,
                               'stroke_color':'#0000FF'},
                     'name':'Region of Interest'}
            #polygon = InfoLayer([roi,style])
            polygon =  InfoLayer([[roi.wkt, "Region Of Interest"]] ,style)
            try:
                layers.extend(polygon)
            except TypeError:
                layers.append(polygon)
            zoom_to_extent = True

        for pt in event_points:
            pt_layer = InfoLayer([[pt[1].wkt, str(pt[0])]],{'name':str(pt[0])})
            try:
                layers.extend(pt_layer)
            except TypeError:
                layers.append(pt_layer)
            
        mymap = Map(
            layers,
            {'default_lat': 45,
            'default_lon': -82.0,
            'default_zoom':7,
            'zoom_to_data_extent': zoom_to_extent,
            'map_div_style': {'width': '700px', 'height': '600px'},
             
            }
            )
    else:
        mymap = empty_map()
    return mymap




def get_recovery_map(stocking_points, recovery_points):

    """This map function taks a list of stocking points and second
    list of recoveries.

    used by views cwt_detail

    
    Arguments: -
    `stocking_points`: a list of points objects and their event numbers
    'roi': region of interest used to select event points

    """
    layers = []
    if len(stocking_points) > 0:
        for pt in stocking_points:
            pt_layer = InfoLayer([[pt[1].wkt,
                                   str(pt[0])]], {'name': str(pt[0])})
            try:
                layers.extend(pt_layer)
            except TypeError:
                layers.append(pt_layer)

    if recovery_points:
        for pt in recovery_points:        
            recovery_layer = InfoLayer([[pt[1].wkt, str(pt[0])]],
                                   {'name':str(pt[0]),
                                    'overlay_style': {'fill_color': '#00FF00',
                                                      'fill_opacity': 0.2,
                                                      'stroke_color':'#00FF00'},
                                })
            try:
                layers.extend(recovery_layer)
            except TypeError:
                layers.append(recovery_layer)

    if len(layers) > 0:
        mymap = Map(
            layers,
            {'default_lat': 45,
             'default_lon': -82.0,
             'default_zoom': 7,
             'zoom_to_data_extent': False,
             'map_div_style': {'width': '700px', 'height': '600px'},
            })
    else:
        mymap = empty_map()
    return mymap
    

    

def get_basin_totals(year, spc, strain=None):
    '''A helper function to retrieve the number of fish stocked by
    basin given a species and year.

    This function uses raw sql - the django orm still doesn't seem to
    to aggregation well.'
    
    Returns a dictionary that includes keys for 'North Channel',
    'Georgian Bay', 'Main Basin' and 'total''

    '''
    from django.db import connection
        
    #spc ignoring strain
    sql = '''select basin, sum(stkcnt) from fsis2_event 
         join fsis2_lot on fsis2_lot.id=fsis2_event.lot_id
         join fsis2_species on fsis2_species.id = fsis2_lot.species_id
         join fsis2_stockingsite on fsis2_stockingsite.id = fsis2_event.site_id
         group by basin, year, species_code having 
         fsis2_event.year=%(year)s and
         fsis2_species.species_code=%(spc)s;
         '''

    cursor = connection.cursor()
    cursor.execute(sql, {'year':year, 'spc':spc})
    rs = cursor.fetchall()

    basin_dict = dict()
    for basin in rs:
        #remove any spaces and turn them into lowercase
        basin_name = basin[0].lower().replace(" ","")
        basin_dict[basin_name] = int(basin[1])
    basin_dict['total']=sum(basin_dict.values())

    return basin_dict



def calc_aac(yc):
    """given a year class that a cwt was associated with calculate
    age-at-capture for every year between age 0 and today
    
    returns a list of two element tuples.  each tuple contains the
    year and the age the fish would have been if it had been captured
    in that year.  If yc is greater than the current year it returns None.

    """

    from datetime import datetime
    this_year = datetime.now().year
    if this_year < yc:
        return None
    else:
        yrs = range(yc, this_year + 1)
        aac = list(enumerate(yrs, start=0))
        aac.sort(reverse=True, key=lambda x: x[1])
        return aac


    

class EventDetailView(DetailView):

    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)

        #import pdb; pdb.set_trace()
        event = kwargs.get('object')

        cwts = [x.cwt for x in event.get_cwts()]
        context['cwt_list'] = CWT.objects.filter(cwt__in=cwts)       
        
        event_point = [[ event.fs_event, event.geom]]
        mymap = get_map(event_point)
        context['map'] = mymap
        context['footer'] = footer_string()
        return context


class EventYearArchiveView(YearArchiveView):
    queryset = Event.objects.all()
    date_field = "event_date"
    make_object_list = True
    allow_future = True
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super(EventYearArchiveView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()
        years = Event.objects.values('year').distinct().order_by('-year')
        context['years'] = years
        return context

    
class EventListView(ListView):
    '''render a list of events optionally filtered by year or lot'''
    queryset = Event.objects.all()
    template_name = "EventList.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)

        years = Event.objects.values('year').distinct().order_by('-year')
        
        cwt = self.kwargs.get('cwt',None)
        context['cwt'] = cwt
        context['footer'] = footer_string()
        context['years'] = years
        
        #if this is cwt view, we want to include a map
        if cwt:
            events = kwargs.get('object_list')
            event_points = [[x.fs_event, x.geom] for x in events]
            mymap = get_map(event_points)
            context['map'] = mymap
        return context

    def get_queryset(self):
        # Get the q GET parameter
        event_id = self.request.GET.get("event")
        if event_id:
            # Return a filtered queryset
            queryset = Event.objects.filter(fs_event=event_id)
        else:
            queryset = Event.objects.all().order_by('-year','event_date')
        return queryset


class EventCreateView(CreateView):
    model = Event
    
    def get_context_data(self, **kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()        
        return context
    
class EventUpdateView(UpdateView):
    model = Event


class LotCreateView(CreateView):
    model = Lot

class LotUpdateView(UpdateView):
    model = Lot


class SiteCreateView(CreateView):
    model = StockingSite


class SiteUpdateView(UpdateView):
    model = StockingSite


#==================
#   LOTS

class LotListView(ListView):
    #includes any lots that don't have any events yet:
    template_name = "LotList.html"
    paginate_by = 20

    def get_queryset(self):
        # Get the q GET parameter
        lot_id = self.request.GET.get("lot")
        if lot_id:
            # Return a filtered queryset
            queryset = Lot.objects.filter(fs_lot=lot_id)
        else:
            queryset = Lot.objects.filter(
                        event__pk__isnull=False).distinct()
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(LotListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()        
        return context

    
class LotDetailView(DetailView):
    model = Lot

    def get_context_data(self, **kwargs):
        context = super(LotDetailView, self).get_context_data(**kwargs)
        lot = kwargs.get('object')
        event_points = lot.get_event_points()
        mymap = get_map(event_points)
        context['map'] = mymap
        context['footer'] = footer_string()        
        return context


class CwtListView(ListView):

    model = CWT
    
    template_name='fsis2/cwt_list.html'
    paginate_by = 30

    def get_queryset(self):
        # Fetch the queryset from the parent get_queryset
        #queryset = super(CwtListView, self).get_queryset()
        queryset = CWT.objects.all().order_by('-year_class')
        # Get the q GET parameter
        cwt = self.request.GET.get("cwt")
        if cwt:
            # Return a filtered queryset
            cwt = cwt.replace('-','')
            return queryset.filter(cwt__icontains=cwt)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CwtListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()        
        return context

        

class SiteListView(ListView):
    queryset = StockingSite.objects.all()
    template_name = "fsis2/site_list.html"
    paginate_by = 20

    def get_queryset(self):
        # Fetch the queryset from the parent get_queryset
        #queryset = super(CwtListView, self).get_queryset()
        queryset = StockingSite.objects.all()
        # Get the q GET parameter
        q = self.request.GET.get("q")
        if q:
            # Return a filtered queryset
            return queryset.filter(site_name__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SiteListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()        
        return context


        
class SiteDetailView(DetailView):
    model = StockingSite
    template_name = "fsis2/site_detail.html"

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        site = kwargs.get('object')
        site_point = [[site.fsis_site_id, site.geom]]
        mymap = get_map(site_point)
        context['map'] = mymap
        context['footer'] = footer_string()        
        return context


class AnnualTotalSpcView(ListView):
    '''renders a view summarizing total number of fish stocked
    annually by species and Proponent.  Spc is passed in as an
    argument.
    '''
    
    template_name = "fsis2/annual_total_stkcnt_list.html"

    def get_queryset(self):
        self.spc = self.kwargs.get('spc', None)
        queryset = Proponent.objects.filter(
            lot__species__species_code=self.spc).values('proponent_name',
            'lot__event__prj_cd').annotate(total=Sum('lot__event__stkcnt'
                                                 )).order_by('-lot__event__year')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AnnualTotalSpcView, self).get_context_data(**kwargs)
        
        spc = self.kwargs.get('spc', None)
        context['species'] = get_object_or_404(Species, species_code=spc)
        context['species_list'] = Species.objects.all()
        context['strain_list'] = Strain.objects.filter(
            species__species_code=81).values('strain_name').distinct()
        context['footer'] = footer_string()
      
        return context


        
class AnnualStockingBySpcStrainView(ListView):
    '''render a view that plots the stocking events associated with a
    strain and year on a map and summarizes those events in a
    table:'''
    
    template_name = "fsis2/annual_stocking_events.html"
    
    def get_queryset(self):
        self.spc = self.kwargs.get('spc', None)
        self.strain = self.kwargs.get('strain', None)
        self.yr = self.kwargs.get('year', None)
        project = 'LHA_FS%s_001' % self.yr[2:]

        queryset = Event.objects.filter(lot__species__species_code=self.spc,
                                        lot__strain__strain_code=self.strain,
                                        prj_cd=project)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AnnualStockingBySpcStrainView,
                         self).get_context_data(**kwargs)

        events = kwargs.get('object_list')
        event_points = [[x.fs_event, x.geom] for x in events]
        mymap = get_map(event_points)
        context['map'] = mymap
        
        spc = self.kwargs.get('spc', None)
        strain = self.kwargs.get('strain', None)
        yr = self.kwargs.get('year', None)

        context['footer'] = footer_string()        
        context['year'] = yr
        context['species'] = get_object_or_404(Species, species_code=spc)
        context['strain'] = Strain.objects.filter(species__species_code=spc,
                                                  strain_code=strain).values_list(
                                                      'strain_name').distinct()[0][0]

        context['strain_code'] = Strain.objects.filter(species__species_code=spc,
                                                  strain_code=strain).values_list(
                                                      'strain_code').distinct()[0][0]
        #get the lists required for this view:
        context['species_list'] = Species.objects.all()
        context['strain_list'] = Strain.objects.filter(species__species_code=81
                                ).values('strain_name','strain_code').distinct()
        
        project_list = Event.objects.filter(lot__species__species_code=spc,
                                        lot__strain__strain_code=strain,
                                        ).values('prj_cd').distinct()
        year_list = [prj_cd_Year(x['prj_cd']) for x in project_list]
        #get unique values and return it to  list
        year_list = list(set(year_list))        
        year_list.sort(reverse=True)
        context['year_list'] = year_list
       
        return context



class AnnualStockingBySpcView(ListView):
    '''render a view that plots the stocking events associated with a
    species in a particular year on a map and summarizes those events in a
    table:

    NOTE: AnnualStockingBySpcStrainView should be re-written to be a
    special case of AnnualStockingBySpcView.  the are essentailly the
    same, except that strain view has a little more informarion and
    the queryset is a subset of the other. - for now it works.

    '''
    
    template_name = "fsis2/annual_stocking_events.html"

    def get_queryset(self):
        self.spc = self.kwargs.get('spc', None)
        self.yr = self.kwargs.get('year', None)
        project = 'LHA_FS%s_001' % self.yr[2:]

        queryset = Event.objects.filter(lot__species__species_code=self.spc,
                                        prj_cd=project)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AnnualStockingBySpcView,
                         self).get_context_data(**kwargs)

        events = kwargs.get('object_list')
        event_points = [[x.fs_event, x.geom] for x in events]
        mymap = get_map(event_points)
        context['map'] = mymap
        context['footer'] = footer_string()
        
        spc = self.kwargs.get('spc', None)
        yr = self.kwargs.get('year', None)

        context['year'] = yr
        context['species'] = get_object_or_404(Species, species_code=spc)
        
        #get the lists required for this view:
        context['species_list'] = Species.objects.all()
        context['strain_list'] = Strain.objects.filter(
            species__species_code=81).values(
                'strain_name','strain_code').distinct()
        
        project_list = Event.objects.filter(lot__species__species_code=spc,
                    ).values('prj_cd').distinct()
        year_list = [prj_cd_Year(x['prj_cd']) for x in project_list]
        #get unique values and return it to  list
        year_list = list(set(year_list))
        year_list.sort(reverse=True)
        context['year_list'] = year_list

        basin_totals = get_basin_totals(year=yr, spc=spc)
        context['basin_totals'] = basin_totals
        
        return context



class AnnualStockingByHatcherySpcView(ListView):
    '''render a view that plots the stocking events associated with a
    species in a particular year from a particular proponent on a map
    and summarizes those events in a table:

    NOTE: AnnualStockingBySpcStrainView should be re-written to be a
    special case of AnnualStockingBySpcView.  the are essentailly the
    same, except that strain view has a little more informarion and
    the queryset is a subset of the other. - for now it works.

    '''
    
    template_name = "fsis2/annual_stocking_events.html"

    def get_queryset(self):
        self.spc = self.kwargs.get('spc', None)
        self.hatchery = self.kwargs.get('hatchery', None)
        #self.strain = self.kwargs.get('strain', None)
        self.yr = self.kwargs.get('year', None)
        project = 'LHA_FS%s_001' % self.yr[2:]

        queryset = Event.objects.filter(lot__species__species_code=self.spc,
                                        prj_cd=project,
                                        lot__proponent__abbrev=self.hatchery)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AnnualStockingByHatcherySpcView,
                         self).get_context_data(**kwargs)

        events = kwargs.get('object_list')
        event_points = [[x.fs_event, x.geom] for x in events]
        mymap = get_map(event_points)
        context['map'] = mymap
        context['footer'] = footer_string()
        
        spc = self.kwargs.get('spc', None)
        yr = self.kwargs.get('year', None)
        hatchery = self.kwargs.get('hatchery', None)

        context['year'] = yr
        context['species'] = get_object_or_404(Species, species_code=spc)
        context['hatchery'] = get_object_or_404(Proponent, abbrev=hatchery)
        
        #get the lists required for this view:
        context['species_list'] = Species.objects.all()
        context['strain_list'] = Strain.objects.filter(
            species__species_code=81).values(
                'strain_name','strain_code').distinct()
        
        project_list = Event.objects.filter(lot__species__species_code=spc,
                    ).values('prj_cd').distinct()
        year_list = [prj_cd_Year(x['prj_cd']) for x in project_list]
        #get unique values and return it to  list
        year_list = list(set(year_list))
        year_list.sort(reverse=True)
        context['year_list'] = year_list
       
        return context

        

class ProponentListView(ListView):
    '''Render a list of proponents who have stocked fish'''    
    queryset = Proponent.objects.all()
    template_name = "fsis2/ProponentList.html"
    
    def get_context_data(self, **kwargs):
        context = super(ProponentListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()        
        return context
    
class ProponentLotListView(ListView):
    '''Render a list of lots stocked by a specific proponent'''
    template_name = "LotList.html"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        '''if lot is included in the request, see if it exists, and if
        so, jump to its detail page
        '''
        lot = self.request.GET.get("lot")
        if lot:
            lot = get_object_or_404(Lot, fs_lot = lot)        
        if lot:
            url = reverse('lot_detail', kwargs={'pk': lot.id})
            return HttpResponseRedirect(url)
        else:
            return super(ProponentLotListView, self).dispatch(request,
                                                              *args, **kwargs)
            
    def get_queryset(self, **kwargs):
        '''get a list of events associated with this hatchery'''
        self.hatchery = self.kwargs.get('hatchery', None)
        queryset = Lot.objects.filter(proponent__abbrev=self.hatchery)
        return queryset  
            
    def get_context_data(self, **kwargs):
        '''add the timestamped footer to the page'''
        context = super(ProponentLotListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()        
        return context


class SpeciesListView(ListView):
    '''render a list of species that have stocking events associated
    with them
    '''
    queryset = Species.objects.all()
    template_name = "fsis2/SpeciesList.html"
    
    def get_context_data(self, **kwargs):
        '''add the timestamped footer to the page'''        
        context = super(SpeciesListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()        
        return context


def find_events(request):
    '''render a map in a form and return a list of stocking events
    contained in the selected poygon.  If the form is valid, the
    selected events and a map containing the selected region and
    selected point are passed to a different template.
    '''

    if request.method == 'POST':
        form = GeoForm(request.POST)
        if form.is_valid():
            roi = form.cleaned_data['selection'][0]
            species = form.cleaned_data.get('species')            
            #import pdb; pdb.set_trace()
            if roi.geom_type=='Polygon':
                if species:
                    events = Event.objects.filter(
                        lot__species__in=species).filter(
                            geom__within=roi).order_by('-year')
                else:
                    events = Event.objects.filter(
                            geom__within=roi).order_by('-year')

                event_points = [[x.fs_event, x.geom] for x in events]
                mymap = get_map2(event_points=event_points, roi=roi)
                                    
            return render_to_response('fsis2/show_events_gis.html',
                              {'map':mymap,
                               'object_list':events,},
                            context_instance = RequestContext(request))

            
    else:
        form = GeoForm() # An unbound form
        return render_to_response('fsis2/find_events_gis.html',
                                  {'form':form},
                                  context_instance = RequestContext(request)
        )



def get_recovery_points(recoveries):
    '''a helper function to extract the project composite key and the
    point of recovery given a list/queryset of recoveries.
    '''
    if recoveries:
        try:
            recovery_points = [[x.composite_key, x.geom] for x in recoveries]
        except:
            recovery_points = [[recoveries.composite_key, recoveries.geom]]
    else:
        recovery_points = None
    return recovery_points

        
def cwt_detail_view(request, cwt_number):
    '''The view returns all of the available information associated
    with a specific cwt number.  The view attemps to create a map
    illustrating location of stocking events.  For Ontario tags, it
    first looks for associated stocking events, if no events are
    found, it will query usgrid for an associated grid number and
    point.  If multiple events are found in cwts_cwt, a template
    accomodates that multiple tagging events and includes a warning is
    used instead.
    
    **Context:**

    ``cwt``
        a :model:`cwts.CWT` object if only one cwt is found in cwt

    ``aac``    
        a dictionary contain year of catpture and age pairs calculated
        for this cwt based on its year class.  Dynamically calculated
        when view is called.

    ``cwt_number``
        only returned if multiple cwt records are found. Used to label
        multiple cwt template.
    
    ``cwt_list``
        a query set of :model:`cwts.CWT` filtered by cwt_number.  None
        if cwt_number returns only one record.
    
    ``event_list``
        a list of :model:`fsis2.Event` objects associated with this
        cwt.

    ``map``
        a olwidget map contain stocking points associated with this cwt.
    
    **Templates:**

    :template:`fsis2/cwt_detail.html`
    :template:`fsis2/multiple_cwt_detail.html`

    '''
    
    cwt = None
    cwt_qs = None

    try:
        cwt = CWT.objects.get(cwt=cwt_number)
    except MultipleObjectsReturned:
        cwt_qs = CWT.objects.filter(cwt=cwt_number).order_by(
            'seq_start', '-stock_year')

    recoveries = CWT_recovery.objects.filter(cwt=cwt_number).order_by(
        '-recovery_year', '-recovery_date')
    recovery_pts = get_recovery_points(recoveries)

    events = Event.objects.filter(taggingevent__cwts_applied__cwt=cwt_number)
    #make the map
    if events:
        event_points = [[x.fs_event, x.geom] for x in events]
        mymap = get_recovery_map(event_points, recovery_pts)

    else:
        #see if there are US sites associated with this tag
        if cwt:
            if cwt.us_grid_no is None:
                #if not, just pass in an empty list
                events = []
            else:
                events = [[cwt.agency, cwt.us_grid_no.geom]]            
            mymap = get_recovery_map(events, recovery_pts)
        else:
            event_points = [[x.fs_event, x.geom] for x in cwt_qs]
            mymap = get_recovery_map(event_points, recovery_pts)

    if cwt:
    #get age at capture dictionary
        aac = calc_aac(cwt.year_class)
        return render_to_response('fsis2/cwt_detail.html',
                                  {'cwt': cwt,
                                   'aac': aac,
                                   'event_list': events,
                                   'recovery_list': recoveries,
                                   'map': mymap},
                                  context_instance=RequestContext(request))
    else:
        cwt_list = []
        for cwt in cwt_qs:
            aac = calc_aac(cwt.year_class)
            cwt_list.append({'cwt': cwt, 'aac': aac})
        #import pdb; pdb.set_trace()
        return render_to_response('fsis2/multiple_cwt_detail.html',
                                  {'cwt_number': cwt_number,
                                   'cwt_list': cwt_list,
                                   'event_list': events,
                                   'recovery_list': recoveries,
                                   'map': mymap},
                                  context_instance=RequestContext(request))
            
            
