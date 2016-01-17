
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.edit import FormView

from .forms import UserForm, ChangePasswordForm, PasswordResetRequestForm


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


class ResetPasswordRequestView(SuperUserRequiredMixin, FormView):
    '''This class implements a standard django password reset except
     that instead of sending an e-mail when the form is valid, it
     renders the message (including the link) in a web-page. The
     contents of the message can then be copied and sent to the
     appropriate recipient by a site administrator. This functionality
     addressed the situation where e-mail access is not available, but
     private password reset is still desirable.
    '''

    #code for template is given below the view's code
    template_name = "auth/reset_password.html"
    success_url = '/auth/login'
    form_class = PasswordResetRequestForm

    def form_valid(self, form):
        """If the form is valid, generate a token and render the template with
        reset link.

        Arguments:
        - `self`:

        """

        data = form.cleaned_data["username_or_email"]
        user = User.objects.get(Q(email=data) | Q(username=data))
        current_site = get_current_site(self.request)
        site_name = current_site.name
        domain = self.request.get_host()

        context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'http',
            }
        return render_to_response(
            'auth/password_reset_message.html',
            {'context': context},
            context_instance=RequestContext(self.request))


class PasswordResetConfirmView(FormView):
    template_name = "auth/change_password.html"
    success_url = settings.LOGIN_REDIRECT_URL

    form_class = ChangePasswordForm

    def get_context_data(self, *args, **kwargs):
        context = super(PasswordResetConfirmView,
                        self).get_context_data(*args, **kwargs)
        context['password_reset'] = True
        return context

    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.
        """
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user,
                                                                    token):
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Password reset was not successful.')
                return self.form_invalid(form)
        else:
            messages.error(request,
                           'The reset password link is no longer valid.')
            return self.form_invalid(form)


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
            auth.login(request, new_user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = UserForm()
    return render(request, 'auth/register.html', {'form': form})
