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
                    SiteUpdateView, CwtListView, AnnualTotalSpcView,
                    AnnualStockingBySpcStrainView, AnnualStockingBySpcView,
                    ProponentListView, ProponentLotListView, SpeciesListView,
                    AnnualStockingByHatcherySpcView, find_events,
                    cwt_detail_view)

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
        #url(r'^events/(?P<cwt>\d{6})/$',
        #    EventListView.as_view(template_name='fsis2/event_list.html'),
        #    name="event_cwt_list"),


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


        url(r'^find_events/$', 'fsis2.views.find_events', name='find_events'),
                       
        #================
        #    CWTs

        #event list <lot>
        url(
            regex=r'^cwts/$',
            view=CwtListView.as_view(),
            name='cwt_list'
            ),

        url(
            #regex=r'^cwts/detail/(?P<cwt>\d{2}\-\d{2}-\d{2})$',
            regex=r'^cwts/detail/(?P<cwt_number>\d{6})$',
            view=cwt_detail_view,
            name='cwt_detail'
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
        #Proponent List
        url(
            regex=r'^hatcheries/$',
            view = ProponentListView.as_view(),
            name='hatchery_list'
            ),

        url(
            regex=r'^hatchery/lots/(?P<hatchery>\w{1,7})$',
            view = ProponentLotListView.as_view(),
            name='hatchery_lot_list'
            ),

#        url(
#            regex=r'^hatchery/events/(?P<hatchery>\d{2})$',
#            view = ProponentLotListView.as_view(),
#            name='hatchery_event_list'
#            ),
#
                       

        #================                       
        #SPECIES
        url(
            regex=r'^species/$',
            view = SpeciesListView.as_view(),
            name='species_list'
            ),

         # url(
         #     regex=r'^species/lots/(?P<hatchery>\w{1,7})$',
         #     view = ProponentLotListView.as_view(),
         #     name='hatchery_lot_list'
         #     ),

                       

                       
        #================
        #    ABOUT
        url(r'^about', TemplateView.as_view(template_name='about.html'),
         name='about'),


        #================================
        #    ANNUAL TOTAL BY SPECIES

        #annual stocking by proponent
        url(
            regex=r'^annual/(?P<spc>\d{2,3})$',
            view=AnnualTotalSpcView.as_view(),
            name='annual_total_spc'
            ),


        # annual stocking by species - where did they go?
        url(
            regex=
            r'^annual/(?P<spc>\d{2,3})/(?P<year>\d{4})$',
            view = AnnualStockingBySpcView.as_view(),
            name = 'annual_stocking_events_by_spc'
            ),
                       

        # annual stocking by strain - where did they go?
        url(
            regex=
            r'^annual/(?P<spc>\d{2,3})/(?P<strain>\w{2,4})/(?P<year>\d{4})$',
            view = AnnualStockingBySpcStrainView.as_view(),
            name = 'annual_stocking_events_by_strain'
            ),



        # annual stocking by species by proponent - where did they go?
        url(
            regex=
            r'^annual/(?P<hatchery>\w{1,7})/(?P<spc>\d{2,3})/(?P<year>\d{4})$',
            view = AnnualStockingByHatcherySpcView.as_view(),
            name = 'annual_stocking_events_by_spc_hatchery'
            ),

                       

    )
