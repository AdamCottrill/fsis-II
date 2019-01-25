from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.requests import RequestSite
from django.core import signing
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render,  redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator

from password_reset.views import Recover

from .forms import UserForm, ChangePasswordForm


def index(request):
    return render(request, 'auth/index.html')


class SuperUserRequiredMixin(object):
    """View mixin which verifies that the logged in user is a superuser
    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect(reverse('index'))
        return super(SuperUserRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class MyRecover(SuperUserRequiredMixin, Recover):
    '''This class overrides the Recover class from django_password
    recovery.  Rather than sending an e-mail when the form is valid,
    it renders the message (including the link) in a web-page. The
    contents of the message can then be copied and sent to the
    appropriate recipient by a site administrator. This functionality
    addressed the situation where e-mail access is not available, but
    private password reset is still desirable.

    '''

    template_name = 'password_reset/recovery_form.html'
    email_template_name = 'password_reset/recovery_email.txt'
    email_subject_template_name = 'password_reset/recovery_email_subject.txt'

    def form_valid(self, form):
        self.user = form.cleaned_data['user']
        self.search_fields[0] == 'username'
        email = self.user.username
        self.mail_signature = signing.dumps(email, salt=self.url_salt)
        context = {
            'site': RequestSite(self.request),
            'user': self.user,
            'token': signing.dumps(self.user.pk, salt=self.salt),
            'secure': self.request.is_secure(),
            }
        return render(self.request,
            'password_reset/password_reset_message.html',
            {'context': context}
        )


recover = MyRecover.as_view()


@login_required
def change_password(request):
    """
    """
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            user = request.user
            user.set_password(new_password)
            user.save()
            return render(request, 'auth/password_changed.html')
    else:
        form = UserForm()
    return render(request, 'auth/change_password.html',
                  {'form': form})


def register(request):
    """
    """
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            new_user = User(username=username)
            new_user.set_password(password)
            new_user.save()
            new_user = authenticate(username=username, password=password)
            #auth.login(request, new_user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = UserForm()
    return render(request, 'auth/register.html', {'form': form})
