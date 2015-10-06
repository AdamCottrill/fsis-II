'''
=============================================================
c:/1work/Python/djcode/fsis2/fsis2/urls/lots.py
Created: 06 Oct 2015 09:19:48

DESCRIPTION:

Urls associated with fish lots

A. Cottrill
=============================================================
'''

from fsis2.views import (LotDetailView,
                         LotListView,
                         LotCreateView,
                         LotUpdateView)

from django.conf.urls import patterns, url

urlpatterns = patterns('',

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

)
