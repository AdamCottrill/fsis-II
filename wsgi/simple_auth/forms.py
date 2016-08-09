from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

class UserForm(forms.Form):
    username = forms.CharField(max_length=30)
    password1 = forms.CharField(widget=forms.PasswordInput(), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(), label="Password")

    def clean_username (self):
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("Username already in use.")

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data


class ChangePasswordForm(forms.Form):

    new_password1 = forms.CharField(widget=forms.PasswordInput(),
                                    label="Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput(),
                                    label="Password")

    def clean(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return self.cleaned_data

#=================================================

class PasswordResetRequestForm(forms.Form):

    username_or_email = forms.CharField(
        label=("Email Or Username"), max_length=254)

    def clean(self):
        """we need to make sure that the username or email are associated with
        one and only one active user.  We also need to make sure that
        the form is not valid if we submit an empty string - which
        might match users without an e-mail address.

        Arguments:
        - `self`:

        """
        data = self.cleaned_data.get('username_or_email')
        try:
            User.objects.get(Q(email=data) | Q(username=data))
            return self.cleaned_data
        except User.DoesNotExist:
            raise forms.ValidationError("An active user could not be found.")
