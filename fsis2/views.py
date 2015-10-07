from datetime import datetime
#from django.contrib.auth.models import User
#from django.core.context_processors import csrf
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.db.models.aggregates import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib import messages
from django.http import Http404

from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.dates import YearArchiveView
from django.views.generic import CreateView, UpdateView

from olwidget.widgets import InfoMap, InfoLayer, Map

from .models import (Event, Lot, TaggingEvent, CWTs_Applied, StockingSite,
                     Proponent, Species, Strain,
                     ManagementUnit, Lake)

from cwts.models import CWT, USgrid, CWT_recovery

from .forms import GeoForm

from fsis2.utils import (timesince, footer_string, prj_cd_Year,
                         get_basin_totals, calc_aac, get_totals)


#==============================================================
#these are olwidget views that will eventually be replaced with
#leaflet equivalents

def get_map(event_points):
    """a helper function that will return an info map object containing
    the points in event_points

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
    return map


def empty_map():
    """returns and empty map zoomed to Lake Huron.  Used when no points
    are available.
    Arguments:
    - None

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


def get_recovery_map(stocking_points, recovery_points, roi=None):

    """This map function takes a list of stocking points and second
    list of recovery points.

    used by views cwt_detail to illustrate where a cwt was stocked and
    subsequently recovered.

    Arguments: -
    `stocking_points`: a list of points objects and their event numbers
    `recovery_points`: a list of recovery point objects and their id string
    'roi': region of interest used to select event points

    """
    layers = []

    if roi:
        #if there was a region of interest, add it first so its on the bottom
        style = {'overlay_style': {'fill_color': '#7DF9FF',
                           'fill_opacity': 0,
                           'stroke_color':'#7DF9FF'},
                 'name':'Region of Interest'}
        #polygon = InfoLayer([roi,style])
        polygon =  InfoLayer([[roi.wkt, "Region Of Interest"]] ,style)
        try:
            layers.extend(polygon)
        except TypeError:
            layers.append(polygon)

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

    if len(stocking_points) > 0:
        for pt in stocking_points:
            pt_layer = InfoLayer([[pt[1].wkt,
                                   str(pt[0])]], {'name': str(pt[0])})
            try:
                layers.extend(pt_layer)
            except TypeError:
                layers.append(pt_layer)

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


#==============================================================





class EventDetailView(DetailView):

    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)

        #this appends associated cwt objects from the cwt application
        #rather than cwts associated with this stocking event in FSIS.
        #Is this what we want to do?

        event = kwargs.get('object')
        cwts = [x.cwt for x in event.get_cwts()]
        context['cwt_list'] = CWT.objects.filter(cwt__in=cwts)

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
            queryset = Event.objects.filter(fs_event__contains=event_id)
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
            queryset = Lot.objects.filter(fs_lot__contains=lot_id)
        else:
            queryset = Lot.objects.filter(
                        event__pk__isnull=False).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LotListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()
        return context


class LotDetailView(DetailView):
    '''A simple view to show the details associated with a lot of fish.
    The rendered template will contain a map of stocking locations and a
    summary table of associated events.
    '''
    model = Lot

    def get_context_data(self, **kwargs):
        context = super(LotDetailView, self).get_context_data(**kwargs)
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

        #sites = StockingSite.objects.all()
        #site_points = [[x.site_name, x.geom] for x in sites]
        #mymap = get_map(site_points)
        #context['map'] = mymap

        return context



class SiteDetailView(DetailView):
    '''a detail view that returns a map of stocking location (and events
    associated with this location), a table of site attributes, and a
    list of stocking events that have occurred here.  If there are
    stocking events with lat-lon that differ from the lat-lon
    associated with the stocking site lookup table they will be
    plotted in a different colour around the stocking site.
    '''

    model = StockingSite
    template_name = "fsis2/site_detail.html"

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        site = kwargs.get('object')
        site_point = [[site.fsis_site_id, site.geom]]
        #some sites have events that have actual lat-long associated with them
        sql = """select e.id, e.fs_event, e.geom from fsis2_event e join
                 fsis2_stockingsite s on e.site_id=s.id
                 where st_equals(e.geom, s.geom)=FALSE and s.site_name='{0}';"""
        sql = sql.format(site.site_name)
        stocking_pts = Event.objects.raw(sql)

        stocking_pts = [[x.fs_event, x.geom] for x in stocking_pts]
        #mymap = get_map(site_point)
        mymap = get_recovery_map(site_point, stocking_pts)
        events = (Event.objects.filter(site__site_name=site.site_name).order_by(
            '-event_date'))
        context['events'] = events
        context['map'] = mymap
        context['footer'] = footer_string()
        return context


def find_sites(request):
    '''render a map in a form and return a list of stocking sites
    contained in the selected poygon.  If the form is valid, a map
    containing the selected region and selected point are passed to a
    different template.

    '''

    if request.method == 'POST':
        form = GeoForm(request.POST)
        if form.is_valid():
            roi = form.cleaned_data['selection'][0]
            species = form.cleaned_data.get('species')
            #import pdb; pdb.set_trace()
            if roi.geom_type=='Polygon':
                if species:
                    sites = StockingSite.objects.filter(
                        event__lot__species__in=species).filter(
                            geom__within=roi).distinct()
                else:
                    sites = StockingSite.objects.filter(
                            geom__within=roi)

                site_points = [[x.site_name, x.geom] for x in sites]
                mymap = get_map2(event_points=site_points, roi=roi)

            return render_to_response('fsis2/show_sites_gis.html',
                              {'map':mymap,
                               'object_list':sites,},
                            context_instance = RequestContext(request))


    else:
        form = GeoForm() # An unbound form
        return render_to_response('fsis2/find_events_gis.html',
                                  {'form':form, 'what':'sites'},
                                  context_instance = RequestContext(request)
        )







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



#class AnnualStockingBySpcView(ListView):
#    '''render a view that plots the stocking events associated with a
#    species in a particular year on a map and summarizes those events in a
#    table:
#
#    NOTE: AnnualStockingBySpcStrainView should be re-written to be a
#    special case of AnnualStockingBySpcView.  the are essentailly the
#    same, except that strain view has a little more informarion and
#    the queryset is a subset of the other. - for now it works.
#
#    '''
#
#    template_name = "fsis2/annual_stocking_events.html"
#
#    def get_queryset(self):
#        self.spc = self.kwargs.get('spc', None)
#        self.yr = self.kwargs.get('year', None)
#        project = 'LHA_FS%s_001' % self.yr[2:]
#
#        queryset = Event.objects.filter(lot__species__species_code=self.spc,
#                                        prj_cd=project)
#        return queryset
#
#    def get_context_data(self, **kwargs):
#        context = super(AnnualStockingBySpcView,
#                         self).get_context_data(**kwargs)
#
#        events = kwargs.get('object_list')
#        event_points = [[x.fs_event, x.geom] for x in events]
#        mymap = get_map(event_points)
#        context['map'] = mymap
#        context['footer'] = footer_string()
#
#        spc = self.kwargs.get('spc', None)
#        yr = self.kwargs.get('year', None)
#
#        context['year'] = yr
#        context['species'] = get_object_or_404(Species, species_code=spc)
#
#        #get the lists required for this view:
#        context['species_list'] = Species.objects.all()
#        context['strain_list'] = Strain.objects.filter(
#            species__species_code=81).values(
#                'strain_name','strain_code').distinct()
#
#        project_list = Event.objects.filter(lot__species__species_code=spc,
#                    ).values('prj_cd').distinct()
#        year_list = [prj_cd_Year(x['prj_cd']) for x in project_list]
#        #get unique values and return it to  list
#        year_list = list(set(year_list))
#        year_list.sort(reverse=True)
#        context['year_list'] = year_list
#
#        basin_totals = get_basin_totals(year=yr, spc=spc)
#        context['basin_totals'] = basin_totals
#
#        return context



#class AnnualStockingByHatcherySpcView(ListView):
#    '''render a view that plots the stocking events associated with a
#    species in a particular year from a particular proponent on a map
#    and summarizes those events in a table:
#
#    NOTE: AnnualStockingBySpcStrainView should be re-written to be a
#    special case of AnnualStockingBySpcView.  the are essentailly the
#    same, except that strain view has a little more informarion and
#    the queryset is a subset of the other. - for now it works.
#
#    '''
#
#    template_name = "fsis2/annual_stocking_events.html"
#
#    def get_queryset(self):
#        self.spc = self.kwargs.get('spc', None)
#        self.hatchery = self.kwargs.get('hatchery', None)
#        #self.strain = self.kwargs.get('strain', None)
#        self.yr = self.kwargs.get('year', None)
#        project = 'LHA_FS%s_001' % self.yr[2:]
#
#        queryset = Event.objects.filter(lot__species__species_code=self.spc,
#                                        prj_cd=project,
#                                        lot__proponent__abbrev=self.hatchery)
#        return queryset
#
#    def get_context_data(self, **kwargs):
#        context = super(AnnualStockingByHatcherySpcView,
#                         self).get_context_data(**kwargs)
#
#        events = kwargs.get('object_list')
#        event_points = [[x.fs_event, x.geom] for x in events]
#        mymap = get_map(event_points)
#        context['map'] = mymap
#        context['footer'] = footer_string()
#
#        spc = self.kwargs.get('spc', None)
#        yr = self.kwargs.get('year', None)
#        hatchery = self.kwargs.get('hatchery', None)
#
#        context['year'] = yr
#        context['species'] = get_object_or_404(Species, species_code=spc)
#        context['hatchery'] = get_object_or_404(Proponent, abbrev=hatchery)
#
#        #get the lists required for this view:
#        context['species_list'] = Species.objects.all()
#        context['strain_list'] = Strain.objects.filter(
#            species__species_code=81).values(
#                'strain_name','strain_code').distinct()
#
#        project_list = Event.objects.filter(lot__species__species_code=spc,
#                    ).values('prj_cd').distinct()
#        year_list = [prj_cd_Year(x['prj_cd']) for x in project_list]
#        #get unique values and return it to  list
#        year_list = list(set(year_list))
#        year_list.sort(reverse=True)
#        context['year_list'] = year_list
#
#        return context
#


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


#==============================================


def annual_events(request, year):
    """Render a view with all of the stocking events associated in a
    particular year.  Events for all species and hatcheries will be
    returned along with a list of other_years with stocking data.

    """

    year = int(year)

    if year > datetime.today().year:
        msg = "Dates in the future not allowed!!"
        messages.error(request, msg)
        raise Http404()

    events = Event.objects.filter(year=year).\
             select_related('lot__proponent__abbrev',
                            'lot__species__common_name',
                            'lot__species__species_code',
                            'lot__strain__strain_name',
                            'site__site_name',
                            'site__id',
                            ).\
             order_by('lot__species__common_name').all()

    totals = get_totals(events)

    tmp = Event.objects.all().\
          order_by('-year').values('year').distinct('year')

    other_years = [x['year'] for x in tmp]

    return render_to_response('fsis2/annual_events.html',
                              {   'object_list':events,
                                  'year':year,
                                  'totals':totals,
                                  'footer':footer_string(),
                                  'other_years':other_years},
                              context_instance=RequestContext(request))


def most_recent_events(request):
    """Get the most recent year of stockin and
    pass the information onto our annual_events view.
    """

    latest = Event.objects.all().aggregate(Max('year'))
    year = latest.get('year__max')

    return annual_events(request, year)



def proponent_annual_events(request, hatchery, year):
    """Render a view with all of the stocking events associated with a
    particular proponent in a particular year.  This view will
    complement the annual stocking event report.
    """

    try:
        proponent = Proponent.objects.get(abbrev=hatchery)
    except Proponent.DoesNotExist:
        msg = "Proponent with abbreviation {} does not exist.".format(hatchery)
        messages.error(request, msg)
        raise Http404()

    year = int(year)

    if year > datetime.today().year:
        msg = "Dates in the future not allowed!!"
        messages.error(request, msg)
        raise Http404()

    events = Event.objects.filter(lot__proponent=proponent, year=year).\
             select_related('lot__proponent__abbrev',
                            'lot__species__common_name',
                            'lot__species__species_code',
                            'lot__strain__strain_name',
                            'site__site_name',
                            'site__id',
                            ).\
             order_by('lot__species__common_name').all()

    totals = get_totals(events)

    tmp = Event.objects.filter(lot__proponent=proponent).\
              order_by('-year').values('year').distinct('year')

    other_years = [x['year'] for x in tmp]


    return render_to_response('fsis2/annual_events.html',
                              {   'object_list':events,
                                  'proponent':proponent,
                                  'year':year,
                                  'totals':totals,
                                  'footer':footer_string(),
                                  'other_years':other_years},
                              context_instance=RequestContext(request))


def proponent_most_recent_events(request, hatchery):
    """Get the most recent year of stocking for the requested hatchery and
    pass the information onto our proponent_annual_events view.
    """

    latest = Event.objects.filter(lot__proponent__abbrev=hatchery).\
                 aggregate(Max('year'))
    year = latest.get('year__max')

    return proponent_annual_events(request, hatchery, year)



def species_annual_events(request, spc, year):
    """Render a view with all of the stocking events associated with a
    particular species in a particular year.  This view will
    complement the annual stocking event report.
    """

    try:
        species = Species.objects.get(species_code=spc)
    except Species.DoesNotExist:
        msg = "Species with species code {} does not exist.".format(spc)
        messages.error(request, msg)
        raise Http404()

    year = int(year)

    if year > datetime.today().year:
        msg = "Dates in the future not allowed!!"
        messages.error(request, msg)
        raise Http404()

    events = Event.objects.filter(lot__species=species, year=year).\
                      select_related('lot__proponent__abbrev',
                                     'lot__species__common_name',
                                     'lot__species__species_code',
                                     'lot__strain__strain_name',
                                     'site__site_name',
                                     'site__id',
                               ).\
                               order_by('lot__species__common_name').all()

    totals = get_totals(events)

    tmp = Event.objects.filter(lot__species=species).\
              order_by('-year').values('year').distinct('year')

    other_years = [x['year'] for x in tmp]

    return render_to_response('fsis2/annual_events.html',
                              {   'object_list':events,
                                  'species':species,
                                  'totals':totals,
                                  'year':year,
                                  'footer':footer_string(),
                                  'other_years':other_years},
                              context_instance=RequestContext(request))






class SpeciesListView(ListView):
    '''render a list of species that have stocking events associated
    with them
    '''
    #queryset = Species.objects.all()
    #add on the most recent stocking year for each species:
    queryset = Species.objects.annotate(latest=Max('lot__event__year'))
    template_name = "fsis2/SpeciesList.html"

    def get_context_data(self, **kwargs):
        '''add the timestamped footer to the page'''
        context = super(SpeciesListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()
        return context


class ManagementUnitListView(TemplateView):
#class ManagementUnitListView(ListView):
    '''render a list of species that have stocking events associated
    with them
    '''
    #queryset = ManagementUnit.objects.all().order_by('lake','mu_type','label')
    #queryset = Lake.objects.all()
    template_name = "fsis2/ManagementUnitList.html"

    def get_context_data(self, **kwargs):
        '''add the timestamped footer to the page'''
        context = super(ManagementUnitListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()
        context['object_list'] = get_management_unit_dict()
        return context


def get_management_unit_dict():
    '''get a nested dictionary of dictionaries containing the management
    unit labels and types in each lake.
    1st level - lake name
    2nd level - management unit type
    3rd level - management unit labels

    dictionary is iterated over in managment list template. - one tab
    per list, collapsing panels containing management unit labels

    '''
    lakes = Lake.objects.all()
    object_dict = {}
    for lake in lakes:
        mus = ManagementUnit.objects.filter(lake=lake).order_by('mu_type',
                                                                'label')
        mu_dict = {}
        for mu in mus:
            mu_dict.setdefault(mu.get_mu_type_display(), []).append(
                dict(slug=mu.slug, label=mu.label))
        object_dict[lake.lake] = mu_dict
    return object_dict


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
                                  {'form':form, 'what':'events'},
                                  context_instance = RequestContext(request)
        )



def get_recovery_points(recoveries):
    '''a helper function to extract the project composite key and the
    point of recovery given a list/queryset of recoveries.

    returns a list of list pairs of the form [composite key, geom]

    '''
    if recoveries:
        try:
            recovery_points = [[x.composite_key, x.geom] for x in recoveries]
        except:
            recovery_points = [[recoveries.composite_key, recoveries.geom]]
    else:
        recovery_points = []
    return recovery_points


def get_stocking_points(stocking_events):
    '''a helper function to extract the stocking event identifier and point
    geometry given a list/queryset of stocking events.

    returns a list of list pairs of the form [fs_event, geom]

    '''
    if stocking_events:
        try:
            event_points = [[x.fs_event, x.geom] for x in stocking_events]
        except:
            event_points = [[stocking_event.fs_event, stocking_event.geom]]
    else:
        event_points = []
    return event_points



def cwt_detail_view(request, cwt_number):
    '''The view returns all of the available information associated
    with a specific cwt number.  The view attemps to create a map
    illustrating location of stocking events.  For Ontario tags, it
    first looks for associated stocking events, if no events are
    found, it will query usgrid for an associated grid number and
    point.  If multiple events are found in cwts_cwt, a template
    tha accomodates multiple tagging events and includes a warning is
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
                us_events = []
            else:
                us_events = [[cwt.agency, cwt.us_grid_no.geom]]
            mymap = get_recovery_map(us_events, recovery_pts)
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
        return render_to_response('fsis2/multiple_cwt_detail.html',
                                  {'cwt_number': cwt_number,
                                   'cwt_list': cwt_list,
                                   'event_list': events,
                                   'recovery_list': recoveries,
                                   'map': mymap},
                                  context_instance=RequestContext(request))


def cwt_recovered_mu(request, slug):
    """a view to find all of the cwt recovered in a managment unit and their
    associated stocking information

    **Context:**

    ``slug`` a slug representing a unique management unit name.
        Management unit slugs are derived from their lake, management
        unit type and label.  It must be defined as a multi-polygon in
        the table ManagementUnits.  Only cwt numbers recovered inside
        the management unit are returned and plotted on map.

    :template:`fsis2/cwt_recovered_mu.html`

    """

    mu_poly = ManagementUnit.objects.get(slug=slug)

    recovered_cwts = get_recovered_cwts(mu_poly)

    #pull out the elements we need to make our map
    recovery_pts = get_recovery_points(recovered_cwts['recoveries'])

    event_pts = get_stocking_points(recovered_cwts['events'])

    US_events = recovered_cwts['US_events']
    #if there are US events, add them to the list of points to be plotted:
    if US_events:
        for event in US_events:
            if event.us_grid_no:
                event_pts.append([event.plant_site, event.us_grid_no.geom])
    #make the map
    mymap = get_recovery_map(event_pts, recovery_pts,
                             roi=mu_poly.geom)

    #add the map and management unit name to the context dictionary
    recovered_cwts['map'] = mymap
    recovered_cwts['mu'] = mu_poly

    return render_to_response('fsis2/cwt_recovered_mu.html',
                              recovered_cwts,

                   context_instance=RequestContext(request))


def get_recovered_cwts(mu_poly, year=None, strain=None):
    """A helper function to actually get the cwt stocking and recovery
    data.  Given a management unit polygon, find all of the cwt
    recoveries from that polygon as well as their associated stocking events.

    Returns a dictionary containing the following keys:

    cwts = a cwt queryset of that contains only those cwts recovered
    in this management unit
    recoveries = recovery events for this managemnet unit(year and strain)
    events = Ontario stocking events associated with the cwts recovered
    US_events = U.S stocking events associated with the cwts recovered

    """

    recoveries = CWT_recovery.objects.filter(geom__within=mu_poly.geom)

    #these are all of the cwt recoveries - all strains and species
    if year:
        recoveries = recoveries.filter(recovery_year=year)

    #cwts = []
    #[cwts.append(x.cwt) for x in recoveries]
    #cwts= list(set(cwts))

    cwts = [x.cwt for x in recoveries]
    recovery_count = dict([(i, cwts.count(i)) for i in set(cwts)])

    cwts = recovery_count.keys()

    #now that we have a list cwts recovered in the roi and year
    #get the stocking events associated with them and filter by the strain:
    filtered_cwts=[]

    #canadian stocking events
    events = (Event.objects.filter(taggingevent__cwts_applied__cwt__in=cwts).
              distinct().order_by('fs_event'))
    if strain:
        events = events.filter(lot__strain__strain_code=strain)

    for event in events:
        tmp = event.get_cwts()
        if tmp:
            filtered_cwts.extend([x.cwt for x in tmp])

    #filtered cwts include only those cwts we recovered in this roi
    #and have stocking event associated with them (this eliminates cwts
    #that may not have been recovered but are associated with same
    #stocking events)
    filtered_cwts = list(set(filtered_cwts).intersection(set(cwts)))

    #US stocking events
    US_events = (CWT.objects.filter(cwt__in=cwts).exclude(agency='OMNR').
                 order_by('year_class'))

    filtered_cwts.extend(list(set([x.cwt for x in US_events])))

    filtered_cwts = CWT.objects.filter(cwt__in=filtered_cwts)
    for x in filtered_cwts:
        x.recovery_count = recovery_count.get(x.cwt, 0)

    #add recovery_count to each of the cwt numbers:
    #import pdb; pdb.set_trace()

    ret = dict( cwts = filtered_cwts,
                 recoveries = recoveries, events = events,
                 US_events = US_events)

    return(ret)



def cwt_stocked_mu(request, slug):
    """a view to find all of the cwts stocked in a mu and their
    associated recovery information

    **Context:**

    ``mu`` a Management Unit name.  Used to select
        appropriate mu polygon from fsis2_MU table.  Only cwt
        numbers stocked inside the mu are returned and plotted on
        map.

    :template:`fsis2/cwt_stocked_mu.html`


    """
    mu_poly = ManagementUnit.objects.get(slug=slug)

    stocked_cwts = get_cwts_stocked_mu(mu_poly)

    #pull out the elements we need to make our map
    recovery_pts = get_recovery_points(stocked_cwts['recoveries'])
    event_pts = get_stocking_points(stocked_cwts['events'])

    mymap = get_recovery_map(event_pts, recovery_pts,
                             roi=mu_poly.geom)

    #add the name of the management unit and the map we just created
    #to the stocked_cwt dictionary.
    stocked_cwts['mu'] = mu_poly
    stocked_cwts['map'] = mymap

    return render_to_response('fsis2/cwt_stocked_mu.html',
                              stocked_cwts,
                              context_instance=RequestContext(request))


def get_cwts_stocked_mu(mu_poly, year=None, strain=None):
    """A helper function to actually get the cwt stocking and recovery
    data for cwts stocked in a management unit.  Given a management unit
    polygon, find all of the stocking events that have occured inside
    of it, and then get all of their associated recovery events.

    Returns a dictionary containing the following keys:
    cwts = set of unique cwt numbers recovered in this management unit
    recoveries = recovery events for this management unit (year and strain)
    events = Ontario stocking events associated with the cwts recovered

    """
    #get all of the stocking events with a cwt tagging event that have
    #occured in the management unit
    events = (Event.objects.filter(taggingevent__tag_type=6).
              filter(geom__within=mu_poly.geom))
    if year:
        events = events.filter(year=year)
    if strain:
        events = events.filter(lot__strain__strain_code='SI')

    #extract the unique cwts associated with those events
    cwt_numbers = []
    for event in events:
        tmp = event.get_cwts()
        if tmp:
            cwt_numbers.extend([x.cwt for x in tmp])
    cwt_numbers=list(set(cwt_numbers))

    #get the all recovery instances from the set of cwts
    recoveries = CWT_recovery.objects.filter(cwt__in=cwt_numbers)
    cwts = CWT.objects.filter(cwt__in=cwt_numbers)

    #we need to add the number of recoveries to each cwt instance:

    #pull out just the cwt numbers and put them in a list
    foo = [x.cwt for x in recoveries]
    #create a dictionary of counts by cwt number
    recovery_counts = dict([(i, foo.count(i)) for i in set(foo)])

    for x in cwts:
        x.recovery_count = recovery_counts.get(x.cwt, 0)

    return(dict( cwts=cwts, events = events,
                 recoveries = recoveries))
