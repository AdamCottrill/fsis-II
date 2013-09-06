#from django.contrib.auth.models import User
#from django.core.context_processors import csrf
#from django.http import HttpResponse
from django.shortcuts import get_object_or_404
#from django.template import RequestContext

from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.dates import YearArchiveView
from django.views.generic import CreateView, UpdateView
from django.db.models import Sum


from olwidget.widgets import InfoMap

from .models import (Event, Lot, TaggingEvent, CWTs_Applied, StockingSite,
                     Proponent, Species, Strain)


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

        return context


class EventYearArchiveView(YearArchiveView):
    queryset = Event.objects.all()
    date_field = "event_date"
    make_object_list = True
    allow_future = True

class EventListView(ListView):
    '''render a list of events optionally filtered by year or lot'''
    queryset = Event.objects.all()
    template_name = "EventList.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        cwt = self.kwargs.get('cwt',None)
        context['cwt'] = cwt

        #if this is cwt view, we want to include a map
        if cwt:
            events = kwargs.get('object_list')
            event_points = [[x.fs_event, x.geom] for x in events]
            map = get_map(event_points)

            context['map'] = map

        return context

    def get_queryset(self):
        self.cwt = self.kwargs.get('cwt',None)
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


class LotDetailView(DetailView):
    model = Lot

    def get_context_data(self, **kwargs):
        context = super(LotDetailView, self).get_context_data(**kwargs)
        lot = kwargs.get('object')
        event_points = lot.get_event_points()
        map = get_map(event_points)
        context['map'] = map
        return context


class CwtListView(ListView):

    template_name='fsis2/cwt_list.html'
    paginate_by = 20

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

class SiteDetailView(DetailView):
    model = StockingSite
    template_name = "fsis2/site_detail.html"

    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        site = kwargs.get('object')
        site_point = [[site.fsis_site_id, site.geom]]
        map = get_map(site_point)
        context['map'] = map
        return context


class AnnualTotalSpcView(ListView):
    template_name = "fsis2/annual_total_stkcnt_list.html"

    def get_queryset(self):
        self.spc = self.kwargs.get('spc', None)
        queryset = Proponent.objects.filter(
            lot__species__species_code=self.spc).values('proponent_name',
            'lot__event__prj_cd').annotate(total=Sum('lot__event__stkcnt'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AnnualTotalSpcView, self).get_context_data(**kwargs)
        #import pdb; pdb.set_trace()

        spc = self.kwargs.get('spc', None)
        context['species'] = get_object_or_404(Species, species_code=spc)
        context['species_list'] = Species.objects.all()
        context['strain_list'] = Strain.objects.filter(
            species__species_code=81).values('strain_name').distinct()
        return context
