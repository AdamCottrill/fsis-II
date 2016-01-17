from django.conf.urls import patterns, url
from simple_auth.views import ResetPasswordRequestView, PasswordResetConfirmView
#from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset_done

urlpatterns = patterns('',

                       url(r'^login/$', 'django.contrib.auth.views.login',
                           {'template_name': 'auth/login.html'},
                           name='login'),

                       url(r'^logout/$', 'django.contrib.auth.views.logout',
                           {'template_name': 'auth/logout.html'},
                           name='logout'),

                       url(r'^register/$', 'simple_auth.views.register',
                           name='register'),

                       url(r'^change_password/$',
                           'simple_auth.views.change_password',
                           name='change_password'),

                       url(r'^account/reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                           PasswordResetConfirmView.as_view(),
                           name='password_reset_confirm'),

                       url(r'^account/reset_password',
                           ResetPasswordRequestView.as_view(),
                           name="password_reset"),

)
