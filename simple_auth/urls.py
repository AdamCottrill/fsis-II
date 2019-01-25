from django.conf.urls import url
#from django.core.urlresolvers import reverse

from django.contrib.auth.views import login, logout
#from django.contrib.auth.views import LoginView, LogoutView

from simple_auth.views import (register, change_password, recover)

urlpatterns = [
                       url(r'^login/$', login,
                           {'template_name': 'auth/login.html',
                            'extra_context': {'next':'/'}},
                           name='login'),

                       url(r'^logout/$', logout,
                           {'template_name': 'auth/logout.html'},
                           name='logout'),



#    url(r'^login/$', LoginView.as_view(template_name='auth/login.html'),
#        name='login'),

#
#    url(r'^logout/$', LogoutView.as_view(template_name='auth/logout.html'),
#        name='logout'),


                       url(r'^register/$', register,
                           name='register'),

                       url(r'^change_password/$',
                           change_password,
                           name='change_password'),

                       url(r'^reset/$', recover,
                           name="password_reset"),
]
