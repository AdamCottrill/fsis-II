'''
=============================================================
c:/1work/Python/djcode/fsis2/fsis2/urls/cwts.py
Created: 06 Oct 2015 09:24:10


DESCRIPTION:

urls associated with cwts

A. Cottrill
=============================================================
'''


from fsis2.views import (CwtListView,
                         cwt_detail_view,
                         cwt_stocked_mu,
                         cwt_stocked_roi,
                         cwt_recovered_mu,
                         cwt_recovered_roi,
                         ManagementUnitListView,)


from django.conf.urls import patterns, url

urlpatterns = patterns('',

        url(
            regex=r'^$',
            view=CwtListView.as_view(),
            name='cwt_list'
            ),

        url(
            regex=r'detail/(?P<cwt_number>\d{6})$',
            view=cwt_detail_view,
            name='cwt_detail'
            ),

        #recoveries in management unit
        url(
            regex=r'stocked_management_unit/(?P<slug>[-_A-Za-z0-9]+)$',
            view=cwt_stocked_mu,
            name='cwt_stocked_mu'
            ),

        #recoveries of cwt stocked in cwt
        url(
            regex=r'recovered_management_unit/(?P<slug>[-_A-Za-z0-9]+)$',
            view=cwt_recovered_mu,
            name='cwt_recovered_mu'
            ),


        #recoveries in a region of interest
        url(
            regex=r'recovered_roi/$',
            view=cwt_recovered_roi,
            name='cwt_recovered_roi'
            ),

        #cwts stocked in a region of interest
        url(
            regex=r'stocked_roi/$',
            view=cwt_stocked_roi,
            name='cwt_stocked_roi'
            ),


        #================
        #Managment Unit list
        url(
            regex=r'^management_units/$',
            view=ManagementUnitListView.as_view(),
            name='mu_list'
            ),

)
