from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('fsis2.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^coregonusclupeaformis/admin/', include(admin.site.urls)),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
            {'template_name':'auth/login.html'}, name='login'),
    url(r'^accounts/logout/$', 'main.views.logout_view', name='logout'),

    url(r'^accounts/register/$', 'main.views.register', name='register'),

    url(r'^accounts/change_password/$', 'main.views.change_password',
        name='change_password'),


)
