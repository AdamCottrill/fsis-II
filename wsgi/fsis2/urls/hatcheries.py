'''
=============================================================
c:/1work/Python/djcode/fsis2/fsis2/urls/hatcheries.py
Created: 06 Oct 2015 09:21:13


DESCRIPTION:

urls associated with hatcheries/proponents

A. Cottrill
=============================================================
'''


from fsis2.views import (ProponentListView,
                         ProponentLotListView,
#                         ProponentEventListView
)


from django.conf.urls import patterns, url

urlpatterns = patterns('',
        #================
        #Proponent Lists
        url(
            regex=r'hatchery_list/$',
            view = ProponentListView.as_view(),
            name='hatchery_list'
            ),

        url(
            regex=r'^lots/(?P<hatchery>\w{1,7})$',
            view = ProponentLotListView.as_view(),
            name='hatchery_lot_list'
            ),


        #NOTE - THIS VIEW MAY NOT EXIST YET!!
#        url(
#            regex=r'^hatchery/events/(?P<hatchery>\d{2})$',
#            view = ProponentEventListView.as_view(),
#            name='hatchery_event_list'
#            ),

)
