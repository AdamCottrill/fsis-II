from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('',
                       
                #===========
                #CWT list
                url(regex = r"^$",
                    view = cwtListView.as_view(),
                    name="cwt_list"),
)