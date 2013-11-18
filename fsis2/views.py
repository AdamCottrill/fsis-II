from datetime import datetime
#from django.contrib.auth.models import User
#from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.dates import YearArchiveView
from django.views.generic import CreateView, UpdateView
from django.db.models import Sum


from olwidget.widgets import InfoMap

from .models import (Event, Lot, TaggingEvent, CWTs_Applied, StockingSite,
                     Proponent, Species, Strain, BuildDate, Readme)

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
        points = [[x[1],x[0]] for x in event_points]
        map = InfoMap(
            points,
            {'default_lat': 45,
            'default_lon': -82.0,
            'default_zoom':7,
            'zoom_to_data_extent':False,
            'map_div_style': {'width': '700px', 'height': '600px'},
            }
            )
    else:
        map=None
    return map



class EventDetailView(DetailView):

    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)

        #import pdb; pdb.set_trace()
        event = kwargs.get('object')
        event_point = [[ event.fs_event, event.geom]]
        map = get_map(event_point)
        context['map'] = map
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
            map = get_map(event_points)
            context['map'] = map
        return context


    def dispatch(self, request, *args, **kwargs):
       
        event = self.request.GET.get("event")
        #import pdb; pdb.set_trace()
        if event:
            event = get_object_or_404(Event,fs_event = event)        
        if event:
            url = reverse('event_detail', kwargs={'pk': event.id})
            return HttpResponseRedirect(url)
            #return redirect(url)
        else:
            return super(EventListView, self).dispatch(request, *args, **kwargs)
        
    def get_queryset(self):
        self.cwt = self.kwargs.get('cwt', None)
        if self.cwt:
            #get the list of tagging events associated with that tag number
            te = TaggingEvent.objects.filter(
                    cwts_applied__cwt=self.cwt).values_list('stocking_event')
            #filter the stocking events to those in te
            queryset = Event.objects.filter(id__in=te)
        else:
            queryset = Event.objects.all()
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
    queryset = Lot.objects.filter(
                        event__pk__isnull=False).distinct()
    template_name = "LotList.html"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):      
        lot = self.request.GET.get("lot")
        if lot:
            lot = get_object_or_404(Lot,fs_lot = lot)        
        if lot:
            url = reverse('lot_detail', kwargs={'pk': lot.id})
            return HttpResponseRedirect(url)
        else:
            return super(LotListView, self).dispatch(request, *args, **kwargs)
    
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
        map = get_map(event_points)
        context['map'] = map
        context['footer'] = footer_string()        
        return context


class CwtListView(ListView):

    template_name='fsis2/cwt_list.html'
    paginate_by = 80

    def get_queryset(self):
        # Fetch the queryset from the parent get_queryset
        #queryset = super(CwtListView, self).get_queryset()
        queryset = CWTs_Applied.objects.values('cwt').order_by('cwt').distinct()
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
        map = get_map(site_point)
        context['map'] = map
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
            'lot__event__prj_cd').annotate(total=Sum('lot__event__stkcnt'))
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
        map = get_map(event_points)
        context['map'] = map
        
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
        map = get_map(event_points)
        context['map'] = map
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
        map = get_map(event_points)
        context['map'] = map
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
    contained in the selected poygon
    '''

    if request.method == 'POST':
        #import pdb; pdb.set_trace()
        form = GeoForm(request.POST)
        if form.is_valid():
            roi = form.cleaned_data['selection'][0]
            selected = []
            if roi.geom_type=='Polygon':
                selected = Event.objects.filter(
                    geom__contained=roi).order_by('-year')
            return render_to_response('fsis2/find_events_gis.html',
                              {'form':form,
                               'object_list':selected,},
                              context_instance = RequestContext(request))
    else:
        form = GeoForm() # An unbound form
        return render_to_response('fsis2/find_events_gis.html',
                                  {'form':form},
                                  context_instance = RequestContext(request)
        )
        