from django.conf.urls import include, url
from django.views.generic import TemplateView

from fsis2.views import (SpeciesListView, AnnualTotalSpcView)

urlpatterns = [
        #================
        #SPECIES
        url(
            regex=r'^species/$',
            view = SpeciesListView.as_view(),
            name='species_list'
            ),


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

    ]


urlpatterns = urlpatterns + [
    url(r'^lots/', include('fsis2.urls.lots')),
    url(r'^hatcheries/', include('fsis2.urls.hatcheries')),
    url(r'^events/', include('fsis2.urls.events')),
    url(r'^sites/', include('fsis2.urls.sites')),
    url(r'^cwts/', include('fsis2.urls.cwts')),
                                 ]
