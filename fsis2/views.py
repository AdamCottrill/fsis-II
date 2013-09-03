#from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
#from django.core.context_processors import csrf
from django.http import HttpResponseRedirect
#from django.http import HttpResponse
#from django.shortcuts import get_object_or_404, render_to_response
#from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.dates import YearArchiveView
from django.views.generic import CreateView, UpdateView

#from olwidget.widgets import InfoMap

from .models import (Event, Lot, TaggingEvent, CWTs_Applied, StockingSite)

import pdb


class EventDetailView(DetailView):

    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        return context

    #@method_decorator(login_required)
    #def dispatch(self, *args, **kwargs):
    #    return super(EventDetailView, self).dispatch(*args, **kwargs)

    #event_detail = EventDetailView.as_view()


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

    ## @method_decorator(login_required)
    ## def dispatch(self, *args, **kwargs):
    ##     return super(EventList, self).dispatch(*args, **kwargs)
    ## 
    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['cwt'] = self.kwargs.get('cwt',None)
        #context['year'] = self.kwargs.get('year',None)
        return context
    
    def get_queryset(self):
        self.cwt = self.kwargs.get('cwt',None)
        #self.tag = self.kwargs.get('year',None)
        if self.cwt:
            #get the list of tagging events associated with that tag number
            te = TaggingEvent.objects.filter(
                    cwts_applied__cwt=self.cwt).values_list('stocking_event')
            #filter the stocking events to those in te
            queryset = Event.objects.filter(id__in=te)
        #elif self.year:
            #queryset = Event.objects.filter(year=self.year)
        else:
            queryset = Event.objects.all()
        return queryset


    #event_list = EventList.as_view()
#events_in_year = EventList.as_view()
#event_by_lot_list = EventList.as_view()


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




#@login_required
#def edit_event(request, event_id):
#    event = get_object_or_404(Event, pk=event_id)
#    if request.user.id != event.author.id:
#        return HttpResponseRedirect(event.get_absolute_url())
#    if request.method == "POST":
#        form = EventForm(author=request.user, instance=event,
#                           data=request.POST)
#        if form.is_valid():
#            form.save()
#            tags = form.cleaned_data['tags']
#            event.tags.add(*tags)
#            return HttpResponseRedirect(event.get_absolute_url())
#    else:
#        form = EventForm(author=request.user, instance=event)
#    return render_to_response("events/event_form.html",
#                            {'form':form, 'add':False},
#                            context_instance = RequestContext(request))
#
#@login_required
#def add_event(request):
#    if request.method =="POST":
#        form = EventForm(author=request.user, data=request.POST)
#        if form.is_valid():
#            new_event = form.save(commit=False)
#            new_event.author=request.user
#            new_event.save()
#            tags = form.cleaned_data['tags']
#            new_event.tags.add(*tags)
#            return HttpResponseRedirect(new_event.get_absolute_url())
#    else:
#        form = EventForm(author=request.user)
#    return render_to_response('events/event_form.html',
#                            {"form":form, 'add':True},
#                            context_instance = RequestContext(request))
#


#==================
#   LOTS

class LotListView(ListView):
    #includes any lots that don't have any events yet:
    queryset = Lot.objects.filter(
                        event__pk__isnull=False).distinct()
    template_name = "LotList.html"
    paginate_by = 20
    ##@method_decorator(login_required)
    ##def dispatch(self, *args, **kwargs):
    ##    return super(LotList, self).dispatch(*args, **kwargs)

    #lot_list = LotList.as_view()



class LotDetailView(DetailView):
    model = Lot
    def get_context_data(self, **kwargs):
        context = super(LotDetailView, self).get_context_data(**kwargs)
        return context

    #lot_detail = LotDetailView.as_view()


###============================
### LOT FORMS
##@login_required
##def edit_lot(request, slug):
##
##    lot = get_object_or_404(Lot, slug=slug)
##    if request.method == "POST":
##        form = LotForm(data=request.POST)
##        if form.is_valid():
##            form = LotForm(instance=lot,
##                           data=request.POST)
##            form.save()
##            return HttpResponseRedirect(lot.get_absolute_url())
##    else:
##        form = LotForm(instance=lot)
##    return render_to_response("events/lot_form.html",
##                            {'form':form, 'add':False},
##                            context_instance = RequestContext(request))
##
##@login_required
##def add_lot(request):
##    if request.method =="POST":
##        form = LotForm(data=request.POST)
##        if form.is_valid():
##            cd = form.cleaned_data
##            new_lot = Lot(name = cd['name'],
##                                    lot_code = cd['lot_code'],
##                                    mime_type = cd['mime_type'])
##            new_lot.save()
##            return HttpResponseRedirect(new_lot.get_absolute_url())
##    else:
##        form = LotForm()
##    return render_to_response('events/lot_form.html',
##                            {"form":form, 'add':True},
##                            context_instance = RequestContext(request))



class CwtListView(ListView):
    
    #queryset = CWTs_Applied.objects.values('cwt').order_by('cwt').distinct()
    template_name='fsis2/cwt_list.html'
    paginate_by = 20
    ##@method_decorator(login_required)
    ##def dispatch(self, *args, **kwargs):
    ##    return super(CwtListView, self).dispatch(*args, **kwargs)



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
