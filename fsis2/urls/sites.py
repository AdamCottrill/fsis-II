'''
=============================================================
c:/1work/Python/djcode/fsis2/fsis2/urls/sites.py
Created: 06 Oct 2015 09:28:42


DESCRIPTION:

urls associated with stocking sites

A. Cottrill
=============================================================
'''


from django.conf.urls import url

from fsis2.views import (SiteDetailView,
                         SiteListView,
                         SiteCreateView,
                         SiteUpdateView,
                         find_sites)


urlpatterns = [

        #================
        #    STOCKING SITEs

        #create stocking site
        url(
            regex=r'add$',
            view=SiteCreateView.as_view(),
            name='site_create'
            ),

        #update stocking site
        url(
            regex=r'update/(?P<pk>\d+)$',
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
            regex=r'detail/(?P<pk>\d+)$',
            view=SiteDetailView.as_view(),
            name='site_detail'
            ),

        url(regex=r'^find_sites/$',
            view=find_sites,
            name='find_sites'),
]
