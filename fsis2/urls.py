from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
#from django.conf.urls.default import *
#from django.views.generic.list_detail import object_list, object_detail
#from django.views.generic.list import ListView
#from django.views.generic.detail import DetailView


from .views import (EventDetailView, EventListView, EventYearArchiveView, 
                    LotDetailView, LotListView)

urlpatterns = patterns("",

        #================
        #    Lots

        #lot detail
        url(
            regex=r'^lot_detail/(?P<pk>\d+)$',
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





        #================
        #    Events
        #event detail
        url(
            regex=r'^event_detail/(?P<pk>\d+)$',
            view=EventDetailView.as_view(),
            name='event_detail'
            ),
            
        #event list
        #event list <year>

        url(r'^events/(?P<year>\d{4})/$',
            EventYearArchiveView.as_view(template_name='fsis2/event_list.html'),
            name="event_year_list"),
           

        #event list <lot>
        url(
            regex=r'^events/$',
            view=EventListView.as_view(),
            name='event_list'
            ),

        #================
        #    CWTs


        #================
        #    ABOUT
        url(r'^about', TemplateView.as_view(template_name='about.html'),
         name='about'),


    )
