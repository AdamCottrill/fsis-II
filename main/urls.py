from django.conf.urls import include, url
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from fsis2.views import most_recent_events

urlpatterns = [
    url(r'^fsis2/', include('fsis2.urls')),

                       url(r'^$', most_recent_events, name='home'),
    url(r'^$', most_recent_events, name='index'),

                       url(r'^accounts/', include('simple_auth.urls')),
    #url(r'^password_reset/',
    #    include('password_reset.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^coregonusclupeaformis/admin/', admin.site.urls),


    ##url(r'^accounts/login/$', 'django.contrib.auth.views.login',
    ##        {'template_name':'auth/login.html'}, name='login'),
    ##url(r'^accounts/logout/$', 'main.views.logout_view', name='logout'),
    ##
    ##url(r'^accounts/register/$', 'main.views.register', name='register'),
    ##
    ##url(r'^accounts/change_password/$', 'main.views.change_password',
    ##    name='change_password'),


]
