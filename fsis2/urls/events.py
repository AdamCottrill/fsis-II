'''
=============================================================
c:/1work/Python/djcode/fsis2/fsis2/urls/events.py
Created: 06 Oct 2015 09:22:12


DESCRIPTION:

urls associated with stocking events

A. Cottrill
=============================================================
'''

from django.conf.urls import patterns, url

from fsis2.views import (EventDetailView,
                    EventListView,
                    EventUpdateView,
                    EventCreateView,
                    AnnualStockingBySpcStrainView,
                    annual_events,
                    proponent_annual_events,
                    proponent_most_recent_events,
                    species_annual_events)


urlpatterns = patterns('',

        #event list <lot>

        #event list
        url(
            regex=r'^$',
            view=EventListView.as_view(),
            name='event_list'
            ),


        #event detail
        url(
            regex=r'detail/(?P<pk>\d+)$',
            view=EventDetailView.as_view(),
            name='event_detail'
            ),

        #create event
        url(
            regex=r'add$',
            view=EventCreateView.as_view(),
            name='event_create'
            ),

        #update event
        url(
            regex=r'update/(?P<pk>\d+)$',
            view=EventUpdateView.as_view(),
            name='event_update'
            ),


        url(r'find_events/$', 'fsis2.views.find_events', name='find_events'),

        #event list <year>
        url(r'(?P<year>\d{4})/$',
            view=annual_events,
            name="annual_events"),

        #events associated with cwt
        #url(r'^events/(?P<cwt>\d{6})/$',
        #    EventListView.as_view(template_name='fsis2/event_list.html'),
        #    name="event_cwt_list"),

        url(
            #regex = r'annual/(?P<spc>\d{2,3})/(?P<year>\d{4})$',
            regex = r'(?P<spc>\d{2,3})/(?P<year>\d{4})$',
            view = species_annual_events,
            name='species_annual_events'
            ),

        url(
            regex=r'hatchery/(?P<hatchery>\w{1,7})/(?P<year>\d{4})$',
            view = proponent_annual_events,
            name='hatchery_annual_events'
            ),

        url(
            regex=r'hatchery/most_recent/(?P<hatchery>\w{1,7})$',
            view = proponent_most_recent_events,
            name='hatchery_most_recent_events'
            ),

        # annual stocking by strain - where did they go?
        url(
            regex=
            r'annual/(?P<spc>\d{2,3})/(?P<strain>\w{2,4})/(?P<year>\d{4})$',
            view = AnnualStockingBySpcStrainView.as_view(),
            name = 'annual_stocking_events_by_strain'
            ),


)
