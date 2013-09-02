from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
#from django.conf.urls.default import *
#from django.views.generic.list_detail import object_list, object_detail
#from django.views.generic.list import ListView
#from django.views.generic.detail import DetailView


from .views import (EventDetailView, EventListView, EventYearArchiveView, 
                    EventUpdateView, EventCreateView,
                    LotDetailView, LotListView, LotCreateView, LotUpdateView,
                    SiteDetailView, SiteListView, SiteCreateView, 
                    SiteUpdateView, CwtListView,)

urlpatterns = patterns("",

        #================
        #    Lots

        #lot detail
        url(
            regex=r'^lot/detail/(?P<pk>\d+)$',
            view=LotDetailView.as_view(),
            name='lot_detail'
            ),

        #lot list year
        #url(r'^lots/(?P<year>\d{4})/$',
        #    LotYearArchiveView.as_view(template_name='fsis2/lot_list.html'),
        #    name="lot_year_list"),


        #lot list
        url(
            regex=r'^lots/$',
            view=LotListView.as_view(),
            name='lot_list'
            ),


        #create lot 
        url(
            regex=r'^lot/add$',
            view=LotCreateView.as_view(),
            name='lot_create'
            ),

        #update lot 
        url(
            regex=r'^lot/update/(?P<pk>\d+)$',
            view=LotUpdateView.as_view(),
            name='lot_update'
            ),




        #================
        #    Events
        #event detail
        url(
            regex=r'^event/detail/(?P<pk>\d+)$',
            view=EventDetailView.as_view(),
            name='event_detail'
            ),
            
        #event list
        #event list <year>

        url(r'^events/(?P<year>\d{4})/$',
            EventYearArchiveView.as_view(template_name='fsis2/event_list.html'),
            name="event_year_list"),
           
        #events associated with cwt
        url(r'^events/(?P<cwt>\d{6})/$',
            EventListView.as_view(template_name='fsis2/event_list.html'),
            name="event_cwt_list"),


        #event list <lot>
        url(
            regex=r'^events/$',
            view=EventListView.as_view(),
            name='event_list'
            ),


        #create event 
        url(
            regex=r'^event/add$',
            view=EventCreateView.as_view(),
            name='event_create'
            ),

        #update event 
        url(
            regex=r'^event/update/(?P<pk>\d+)$',
            view=EventUpdateView.as_view(),
            name='event_update'
            ),

        #================
        #    CWTs

        #event list <lot>
        url(
            regex=r'^cwts/$',
            view=CwtListView.as_view(),
            name='cwt_list'
            ),

        #================
        #    STOCKING SITEs

        #create stocking site
        url(
            regex=r'^site/add$',
            view=SiteCreateView.as_view(),
            name='site_create'
            ),

        #update stocking site
        url(
            regex=r'^site/update/(?P<pk>\d+)$',
            view=SiteUpdateView.as_view(),
            name='site_update'
            ),

        #stocking sites
        url(
            regex=r'^sites/$',
            view=SiteListView.as_view(),
            name='site_list'
            ),

        #stocking site details
        url(
            regex=r'^site/detail/(?P<pk>\d+)$',
            view=SiteDetailView.as_view(),
            name='site_detail'
            ),

        #================
        #    ABOUT
        url(r'^about', TemplateView.as_view(template_name='about.html'),
         name='about'),




    )
