from django.conf.urls import url

from .views import *

urlpatterns = [
                url(regex = r"^$",
                    view = cwtListView.as_view(),
                    name="cwt_list"),
]
