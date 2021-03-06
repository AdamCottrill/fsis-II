'''=============================================================
c:/1work/Python/djcode/fsis2/fsis2/views.py
Created: 08 Oct 2015 10:31:32


DESCRIPTION:

This file contains all of the views associated with fsis2.  It has
been completely re-orgainzied to reflect the hierarchy in the model
objects.

The view start out with high level parent/lookup objects - species,
management units, stocking sites, and propornents.  THese are then
followed by lots, stocking events and cwts.  Finally, there are a
number of summary views that present often requested summaries of
stocking data.

Each section starts with class based views - list views, detail views,
create and update.  Followed by specialized view functions that
present some subset of the data in a logical way.


A. Cottrill
=============================================================

'''

from datetime import datetime
from django.core.exceptions import MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db.models import Sum, Q
from django.db.models.aggregates import Max, Min, Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext

from django.contrib import messages
from django.contrib.gis.geos import Polygon
from django.http import Http404

from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.dates import YearArchiveView
from django.views.generic import CreateView, UpdateView

from .models import (Event, Lot, TaggingEvent, CWTs_Applied, StockingSite,
                     Proponent, Species, Strain,
                     ManagementUnit, Lake)

from cwts.models import CWT, CWT_recovery    #, USgrid

from .forms import GeoForm

from fsis2.utils import (timesince, footer_string, prj_cd_Year,
                         get_basin_totals, get_totals,
                         get_management_unit_dict,
                         get_recovery_points,
                         get_stocking_points,
                         get_recovered_cwts,
                         get_cwts_stocked_mu,
                         get_map,
                         #get_map2,
                         #empty_map,
                         get_recovery_map)

#==============================================================
#                  SPECIES stocked


class SpeciesListView(ListView):
    '''
    Render a list of species that have stocking events associated
    with them
    '''
    #queryset = Species.objects.all()
    #add on the most recent stocking year for each species:
    queryset = Species.objects.annotate(latest=Max('lot__event__year')).\
               annotate(earliest=Min('lot__event__year')).\
               filter(latest__isnull=False)
    template_name = "fsis2/SpeciesList.html"

    def get_context_data(self, **kwargs):
        '''add the timestamped footer to the page'''
        context = super(SpeciesListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()
        return context


#==============================================================
#                  MANAGEMENT UNITS

class ManagementUnitListView(TemplateView):
    '''
    Render a list of species that have stocking events associated
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


#==============================================================
#                  STOCKING SITES


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
            return queryset.filter(site_name__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SiteListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()

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

        context['sites'] = site
        events = (Event.objects.filter(site__site_name=site.site_name).order_by(
            '-event_date')).select_related('lot__species',
                                           'lot__strain',
                                           'lot__proponent')

        context['events'] = events
        context['footer'] = footer_string()
        return context


class SiteCreateView(CreateView):
    model = StockingSite


class SiteUpdateView(UpdateView):
    model = StockingSite


def find_sites(request):
    '''render a map in a form and return a list of stocking sites
    contained in the selected poygon.  If the form is valid, a map
    containing the selected region and selected point are passed to a
    different template.

    '''

    if request.method == 'POST':
        form = GeoForm(request.POST)
        if form.is_valid():
            roi = form.cleaned_data.get('selection')[0]
            species = form.cleaned_data.get('species')
            first_year = form.cleaned_data.get('earliest')
            last_year = form.cleaned_data.get('latest')

            if roi.geom_type=='LinearRing':
                roi = Polygon(roi)

            sites = StockingSite.objects.filter(geom__within=roi)


            #import pdb;pdb.set_trace()

            #now filter for our optional fields:
            if species:
                sites = sites.filter(event__lot__species__in=species)
            if first_year:
                sites = sites.filter(event__year__gte=first_year)
            if last_year:
                sites = sites.filter(event__year__lte=last_year)

            sites = sites.annotate(event_count=Count('event'))

            return render(request, 'fsis2/show_sites_gis.html',
                                      {'roi': roi,
                                       'sites': sites})
        else:
            return render(request,
                          'fsis2/find_events_gis.html',
                          {'form': form, 'what': 'sites'})

    else:
        form = GeoForm()   # An unbound form
        return render(request, 'fsis2/find_events_gis.html',
                      {'form': form, 'what': 'sites'})


#==============================================================
#   PROPONENTS/HATCHERIES


class ProponentListView(ListView):
    '''Render a list of proponents who have stocked fish'''
    template_name = "fsis2/ProponentList.html"


    def get_queryset(self):
        # Get the q GET parameter
        q = self.request.GET.get("q")
        queryset = Proponent.objects.all().\
                   annotate(latest=Max('lot__event__year')).\
                   annotate(earliest=Min('lot__event__year')).\
                   filter(latest__isnull=False)
        if q:
            return queryset.filter(Q(abbrev__icontains=q) |
                                   Q(proponent_name__icontains=q))
        return queryset

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
            lot = get_object_or_404(Lot, fs_lot=lot)
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


#==============================================================
#                       LOTS

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

class LotCreateView(CreateView):
    model = Lot

class LotUpdateView(UpdateView):
    model = Lot


#==============================================================
#                  STOCKING EVENTS


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

        cwt = self.kwargs.get('cwt', None)
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
            first_year = form.cleaned_data.get('earliest')
            last_year = form.cleaned_data.get('latest')

            if roi.geom_type == 'LinearRing':
                roi = Polygon(roi)

            events = Event.objects.filter(geom__within=roi).order_by('-year')

            if species:
                events = events.filter(lot__species__in=species)
            if first_year:
                events = events.filter(year__gte=first_year)
            if last_year:
                events = events.filter(year__lte=last_year)

            return render(request, 'fsis2/show_events_gis.html',
                          {'roi': roi, 'events': events})

        else:
            return render(request, 'fsis2/find_events_gis.html',
                          {'form': form, 'what': 'events'})

    else:
        form = GeoForm()     # An unbound form
        return render(request, 'fsis2/find_events_gis.html',
                      {'form': form, 'what': 'events'})



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
             select_related('lot__proponent',
                            'lot__species',
                            'lot__strain',
                            'site').\
                            order_by('lot__species__common_name').all()


    totals = get_totals(events)

    tmp = Event.objects.all().\
          order_by('-year').values('year').distinct('year')

    other_years = [x['year'] for x in tmp]

    return render(request, 'fsis2/annual_events.html',
                              {'object_list': events,
                               'year': year,
                               'totals': totals,
                               'footer': footer_string(),
                               'other_years': other_years})


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
             select_related('lot__proponent',
                            'lot__species',
                            'lot__strain',
                            'site',
                            ).\
             order_by('lot__species__common_name').all()

    totals = get_totals(events)

    tmp = Event.objects.filter(lot__proponent=proponent).\
              order_by('-year').values('year').distinct('year')

    other_years = [x['year'] for x in tmp]

    return render(request, 'fsis2/annual_events.html',
                              {'object_list': events,
                               'proponent': proponent,
                               'year': year,
                               'totals': totals,
                               'footer': footer_string(),
                               'other_years': other_years})


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
                        select_related('lot__proponent',
                                       'lot__species',
                                       'lot__strain',
                                       'site',
                        ).\
                        order_by('lot__species__common_name').all()

    totals = get_totals(events)

    tmp = Event.objects.filter(lot__species=species).\
              order_by('-year').values('year').distinct('year')

    other_years = [x['year'] for x in tmp]

    return render(request, 'fsis2/annual_events.html',
                  {'object_list': events,
                   'species': species,
                               'totals': totals,
                               'year': year,
                               'footer': footer_string(),
                               'other_years': other_years})


#==============================================================
#                   CWTS

class CwtListView(ListView):

    model = CWT
    template_name = 'fsis2/cwt_list.html'
    paginate_by = 50

    def get_queryset(self):
        # Fetch the queryset from the parent get_queryset
        #queryset = super(CwtListView, self).get_queryset()
        queryset = CWT.objects.all().order_by('-year_class').\
                   select_related('spc')
        # Get the q GET parameter
        cwt = self.request.GET.get("cwt")
        if cwt:
            # Return a filtered queryset
            cwt = cwt.replace('-', '')
            return queryset.filter(cwt__icontains=cwt)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CwtListView, self).get_context_data(**kwargs)
        context['footer'] = footer_string()
        return context


def cwt_detail_view(request, cwt_number):
    '''The view returns all of the available information associated
    with a specific cwt number.  The view attemps to create a map
    illustrating location of stocking events.  For Ontario tags, it
    first looks for associated stocking events, if no events are
    found, it will query usgrid for an associated grid number and
    point.  If multiple events are found in cwts_cwt, a template
    that accomodates multiple tagging events and includes a warning is
    used instead.

    **Context: **

    ``cwt``
        a : model: `cwts.CWT` object if only one cwt is found in cwt


    ``cwt_number``
        only returned if multiple cwt records are found. Used to label
        multiple cwt template.

    ``cwt_list``
        a query set of : model: `cwts.CWT` filtered by cwt_number.  None
        if cwt_number returns only one record.

    ``event_list``
        a list of : model: `fsis2.Event` objects associated with this
        cwt.

    **Templates: **

    : template: `fsis2/cwt_detail.html`
    : template: `fsis2/multiple_cwt_detail.html`

    '''

    #the cwt detail page required:
    # cwt(s) - from cwts_cwt that match cwt_number
    # events - omnr stocking events associated with cwt_number
    # us_events - subset of cwts match cwt_number where agency != OMNR
    # recoveries - queryset containing all mnr recoveries of this cwt number

    try:
        #cwt = CWT.objects.get(cwt=cwt_number)
        cwt = get_object_or_404(CWT, cwt=cwt_number)
        multiple = False
    except MultipleObjectsReturned:
        cwt = CWT.objects.filter(cwt=cwt_number).order_by(
            'seq_start', '-stock_year')
        if cwt:
            multiple = True
        else:
            multiple = None

    recoveries = CWT_recovery.objects.filter(cwt=cwt_number).order_by(
        '-recovery_year', '-recovery_date')

    events = Event.objects.filter(taggingevent__cwts_applied__cwt=cwt_number).\
             select_related('site')

    us_events = CWT.objects.filter(cwt=cwt_number).exclude(agency='OMNR').\
                order_by('seq_start', '-stock_year')

    return render(request, 'fsis2/cwt_detail.html',
                              {'cwt': cwt,
                               'events': events,
                               'us_events': us_events,
                               'recoveries': recoveries,
                               'multiple': multiple,
                               })



def cwt_recovered_roi(request):
    '''render a map in a form and return a list of cwt recovered within in
    the selected polygon.  The returned map includes the selected
    region of interest, any filters or species selected, points for
    each of the stocking and recovery points, and summary tables of
    the cwt details, the cwt recovery events, and the associated
    stocking events.

    this view uses the stored procedure cwts_stocking_events_geom() to
    get the stocking events for the cwts recovered in the region of
    interest.

    '''
    what = "cwt recoveries"
    subcaption = "Where did these fish come from?"

    if request.method == 'POST':
        form = GeoForm(request.POST)
        if form.is_valid():
            roi = form.cleaned_data.get('selection')[0]
            species = form.cleaned_data.get('species')
            first_year = form.cleaned_data.get('earliest')
            last_year = form.cleaned_data.get('latest')

            if roi.geom_type == 'LinearRing':
                roi = Polygon(roi)

            #stocking events
            if species:
                #spc_ids = ','.join([str(x.id) for x in species])
                spc_ids = [x.id for x in species]
                sql = ('select * from cwts_stocking_events_geom(%s,' +
                       ' %s, %s, %s);')
                #import pdb;pdb.set_trace()
                events = Event.objects.raw(sql, (roi.wkt, first_year,
                                                 last_year, spc_ids))
            else:
                sql = 'select * from cwts_stocking_events_geom(%s, %s, %s);'
                events = Event.objects.raw(sql, (roi.wkt, first_year,
                                                 last_year))

            #can't serialize a raw query set. Creat list of points to plot:
            event_pts = []
            for event in events:
                event_pts.append({'geom': event.geom,
                                  'popup_text': event.popup_text})

            #count the number of records - raw queryset don't have count()
            events_count = len(event_pts)

            #get cwt recovery events and apply filters
            recoveries = CWT_recovery.objects.filter(geom__within=roi)
            if first_year:
                recoveries = recoveries.filter(recovery_year__gte=first_year)
            if last_year:
                    recoveries = recoveries.filter(recovery_year__lte=last_year)
            if species:
                recoveries = recoveries.filter(spc__in=species)

            #distinct cwts in our recoveries
            distinct_cwts = recoveries.values_list('cwt').distinct()
            cwts = CWT.objects.filter(cwt__in=distinct_cwts)

            #add on the number of recaptures of each tag:
            tmp = recoveries.values('cwt').annotate(N=Count('cwt'))
            recovery_count = {x['cwt']: x['N'] for x in tmp}

            for x in cwts:
                x.recovery_count = recovery_count.get(x.cwt, 0)

            #this should also include a join on species
            us_events = CWT.objects.filter(cwt__in=distinct_cwts).\
                        exclude(agency='OMNR').\
                        order_by('seq_start', '-stock_year')

            return render(request, 'fsis2/cwt_recovered_mu.html',
                          {'mu': 'the Region of Interest',
                           'species': species,
                           'fyear': first_year,
                           'lyear': last_year,
                           'roi': roi,
                           'what': what,
                           'cwts': cwts,
                           'recoveries': recoveries,
                           'events': events,
                           'events_count': events_count,
                           'event_pts': event_pts,
                           'us_events': us_events
                          })

        else:
            return render(request, 'fsis2/find_events_gis.html',
                          {'form': form, 'what': what,
                           'subcaption': subcaption})
    else:
        form = GeoForm()    # An unbound form
        return render(request, 'fsis2/find_events_gis.html',
                      {'form': form, 'what': what,
                       'subcaption': subcaption})




def cwt_stocked_roi(request):
    '''render a map in a form and return a list of cwts stocked within in
    the selected polygon.  The returned map includes the selected
    region of interest, any filters or species selected, points for
    each of the stocking and subsequen recovery points, and summary
    tables of the cwt details, the cwt recovery events, and the
    associated stocking events.

    this view uses the stored procedure cwts_recovered_geom() to
    get the recovery events for the cwts stocked in the region of
    interest.

    '''
    what = "cwts stocked"
    subcaption = "Where did these fish go?"

    if request.method == 'POST':
        form = GeoForm(request.POST)
        if form.is_valid():
            roi = form.cleaned_data.get('selection')[0]
            species = form.cleaned_data.get('species')
            first_year = form.cleaned_data.get('earliest')
            last_year = form.cleaned_data.get('latest')

            if roi.geom_type == 'LinearRing':
                roi = Polygon(roi)

            #stocking events
            if species:
                #spc_ids = ','.join([str(x.id) for x in species])
                spc_ids = [x.id for x in species]
                sql = ('select * from cwts_recovered_geom(%s,' +
                       ' %s, %s, %s);')
                recoveries = CWT_recovery.objects.raw(sql, (roi.wkt,
                                                            first_year,
                                                            last_year, spc_ids))
            else:
                sql = 'select * from cwts_recovered_geom(%s, %s, %s);'
                recoveries = CWT_recovery.objects.raw(sql, (roi.wkt,
                                                            first_year,
                                                            last_year))

            #can't serialize a raw query set. Creat list of points to
            #plot and a dictionary containing the number of recaps for
            #each cwt:
            recovery_pts = []
            recovered_numbers = {}
            for x in recoveries:
                recovery_pts.append({'geom': x.geom,
                                     'popup_text': x.popup_text})
                if recovered_numbers.get(x.cwt):
                    recovered_numbers[x.cwt] += 1
                else:
                    recovered_numbers[x.cwt] = 1

            #count the number of records - raw queryset don't have count()
            recovery_count = len(recovery_pts)

            #get cwt stocking events with cwts that occured in the roi
            #and apply filters
            events = Event.objects.filter(geom__within=roi).\
                     filter(taggingevent__tag_type='6').\
                     filter(year__gte=first_year).\
                     filter(year__lte=last_year)
            if species:
                events = events.filter(lot__species__in=species)

            #this should also include a join on species
            us_events = CWT.objects.filter(cwt__in=recovered_numbers.keys()).\
                        exclude(agency='OMNR').\
                        order_by('seq_start', '-stock_year')

            #get the distinct list of cwt numbers that have been stocked in
            #those events
            distinct_cwts = events.values_list(
                'taggingevent__cwts_applied__cwt').distinct()
            #get those cwt numbers to filter the cwt objects
            tmp = [x[0] for x in distinct_cwts]
            cwts = CWT.objects.filter(cwt__in=tmp)
            recoveries = CWT_recovery.objects.filter(cwt__in=tmp)

            for x in cwts:
                x.recovery_count = recovered_numbers.get(x.cwt, 0)

            return render(request, 'fsis2/cwt_recovered_mu.html',
                          {'mu': 'the Region of Interest',
                           'species': species,
                           'fyear': first_year,
                           'lyear': last_year,
                           'roi': roi,
                           'what': what,
                           'cwts': cwts,
                           'recoveries': recoveries,
                           'recovery_count': recovery_count,
                           'recovery_pts': recovery_pts,
                           'events': events,
                           'us_events': us_events
                          })

        else:
            return render(request, 'fsis2/find_events_gis.html',
                          {'form': form, 'what': what,
                           'subcaption': subcaption})

    else:
        form = GeoForm()              # An unbound form
        return render(request, 'fsis2/find_events_gis.html',
                      {'form': form, 'what': what,
                       'subcaption': subcaption})


def cwt_recovered_mu(request, slug):
    """a view to find all of the cwt recovered in a managment unit and their
    associated stocking information

    **Context: **

    ``slug`` a slug representing a unique management unit name.
        Management unit slugs are derived from their lake, management
        unit type and label.  It must be defined as a multi-polygon in
        the table ManagementUnits.  Only cwt numbers recovered inside
        the management unit are returned and plotted on map.

    : template: `fsis2/cwt_recovered_mu.html`

    """

    mu_poly = ManagementUnit.objects.get(slug=slug)
    recoveries = CWT_recovery.objects.filter(geom__within=mu_poly.geom)

    #filter the recoveries based on first year, last year and species
    fyear = 1950
    lyear = 2019
    #species = ""
    if fyear:
        recoveries = recoveries.filter(recovery_year__gte=fyear)
    if lyear:
        recoveries = recoveries.filter(recovery_year__lte=lyear)

    #Look into creating a specialized view in POSTgres that is
    #declared in Django as an unmanaged table.  The view would join
    #our recoveries to cwts using both cwt number and species.

    #get the list of distinct cwts in our recoveries
    cwt_nums = recoveries.values_list('cwt').distinct()

    cwts = CWT.objects.filter(cwt__in=cwt_nums)

    #add on the number of recaptures of each tag:
    tmp = recoveries.values('cwt').annotate(N=Count('cwt'))
    recovery_count = {x['cwt']: x['N'] for x in tmp}

    for x in cwts:
        x.recovery_count = recovery_count.get(x.cwt, 0)

    #now get the stocking events associated with these cwts:
    #this does not account for sequential CWTS!!!
    events = Event.objects.filter(taggingevent__cwts_applied__cwt__in=cwt_nums)

    us_events = CWT.objects.filter(cwt__in=cwt_nums).exclude(agency='OMNR').\
                order_by('seq_start', '-stock_year')

    #recovered_cwts = get_recovered_cwts(mu_poly)
    #
    ##pull out the elements we need to make our map
    #recovery_pts = get_recovery_points(recovered_cwts['recoveries'])
    #
    #event_pts = get_stocking_points(recovered_cwts['events'])
    #
    #US_events = recovered_cwts['US_events']
    ##if there are US events, add them to the list of points to be plotted:
    #if US_events:
    #    for event in US_events:
    #        if event.us_grid_no:
    #            event_pts.append([event.plant_site, event.us_grid_no.geom])
    ##make the map
    #mymap = get_recovery_map(event_pts, recovery_pts,
    #                         roi=mu_poly.geom)
    #
    ##add the map and management unit name to the context dictionary
    #recovered_cwts['map'] = mymap
    #recovered_cwts['mu'] = mu_poly

    return render(request, 'fsis2/cwt_recovered_mu.html',
                  {'mu': mu_poly.label,
                   'roi': mu_poly,
                   'what': 'recovery',
                   'cwts': cwts,
                   'recoveries': recoveries,
                   'events': events,
                   'us_events': us_events
                  })


def cwt_stocked_mu(request, slug):
    """a view to find all of the cwts stocked in a mu and their
    associated recovery information

    **Context: **

    ``mu`` a Management Unit name.  Used to select
        appropriate mu polygon from fsis2_MU table.  Only cwt
        numbers stocked inside the mu are returned and plotted on
        map.

    : template: `fsis2/cwt_stocked_mu.html`


    """
    mu_poly = ManagementUnit.objects.get(slug=slug)

    #events with cwts in the region of interest:
    events = Event.objects.filter(geom__within=mu_poly.geom).\
             filter(taggingevent__cwts_applied__cwt__isnull=False)

    fyear = 1950
    lyear = 2019
    #species = ""
    if fyear:
        events = events.filter(year__gte=fyear)
    if lyear:
        events = events.filter(year__lte=lyear)

    #get the distinct list of cwt numbers that have been stocked in those events
    cwt_nums = events.values_list('taggingevent__cwts_applied__cwt').distinct()
    #get those cwt numbers to filter the cwt objects
    tmp = [x[0] for x in cwt_nums]
    cwts = CWT.objects.filter(cwt__in=tmp)
    recoveries = CWT_recovery.objects.filter(cwt__in=tmp)

    #add on the number of recaptures of each tag:
    tmp = recoveries.values('cwt').annotate(N=Count('cwt'))
    recovery_count = {x['cwt']: x['N'] for x in tmp}

    for x in cwts:
        x.recovery_count = recovery_count.get(x.cwt, 0)

    return render(request, 'fsis2/cwt_stocked_mu.html',
                  {'mu': mu_poly.label,
                   'roi': mu_poly,
                   'what': 'stocked',
                   'cwts': cwts,
                   'recoveries': recoveries,
                   #'us_events': us_events,
                   'events': events,
                  })


    #stocked_cwts = get_cwts_stocked_mu(mu_poly)
    #
    ##pull out the elements we need to make our map
    #recovery_pts = get_recovery_points(stocked_cwts['recoveries'])
    #event_pts = get_stocking_points(stocked_cwts['events'])
    #
    #mymap = get_recovery_map(event_pts, recovery_pts,
    #                         roi=mu_poly.geom)
    #
    ##add the name of the management unit and the map we just created
    ##to the stocked_cwt dictionary.
    #stocked_cwts['mu'] = mu_poly
    #stocked_cwts['map'] = mymap
    #
    #return render_to_response('fsis2/cwt_stocked_mu.html',
    #                          stocked_cwts,
    #                          context_instance=RequestContext(request))



#==============================================================
#                 STOCKING  SUMMARIES


class AnnualTotalSpcView(ListView):
    '''renders a view summarizing total number of fish stocked
    annually by species and Proponent.  Spc is passed in as an
    argument.
    '''

    template_name = "fsis2/annual_total_stkcnt_list.html"

    def get_queryset(self):
        self.spc = self.kwargs.get('spc', None)
        queryset = Proponent.objects.filter(
            lot__species__species_code=self.spc).\
            values('proponent_name', 'lot__event__prj_cd').\
            annotate(total=Sum('lot__event__stkcnt')).\
            order_by('-lot__event__year')
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
    table: '''

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
                                                  strain_code=strain).\
            values_list('strain_name').distinct()[0][0]

        context['strain_code'] = Strain.objects.\
                                 filter(species__species_code=spc,
                                        strain_code=strain).\
                                 values_list('strain_code').distinct()[0][0]
        #get the lists required for this view:
        context['species_list'] = Species.objects.all()
        context['strain_list'] = Strain.objects.\
                                 filter(species__species_code=81).\
                                 values('strain_name', 'strain_code').distinct()

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
#        project = 'LHA_FS%s_001' % self.yr[2: ]
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
#        project = 'LHA_FS%s_001' % self.yr[2: ]
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
