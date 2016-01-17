from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from simple_auth.tests.factories import UserFactory


class TestPasswordRecoveryIntegration(WebTest):
    '''user successfully accesses reset link and is able to change
    their password.
    '''

    csrf_checks = False

    def setUp(self):
        '''we will need two users - one is a super user, one a regular user
        '''

        self.password = "FirstPassword1"
        self.user1 = UserFactory(first_name='Homer', last_name='Simpson',
                                 username='hsimpson', is_superuser=True,
                                 password=self.password)

        self.user2 = UserFactory(first_name='George', last_name='Costanza',
                                 username='gconstanza', password=self.password)

    def test_password_recovery(self):
        '''This test simulates a super user requesting a password
        reset token for a user, followed by that user accessing the
        token and changing his/her password.
        '''

        url = ''
        response = self.app.get(reverse('password_reset'),
                                user=self.user1)

        form = response.forms['password_recovery']
        form['username_or_email'] = self.user2.username
        response = form.submit()

        # this would be better with reverse(something) but this url
        # does not exist anywhere that I can find.
        reset_url = '/account/reset_password_confirm/'
        for a in response.html.findAll('a'):
            if reset_url in a['href']:
                url = a['href']

        response2 = self.app.get(url)
        self.assertTemplateUsed(response2, 'auth/change_password.html')

        #make sure the response2 contains the expected elements
        msg = 'Please choose your new password'
        self.assertContains(response2, msg)
        #self.assertContains(response2, self.user2.username)

        #fill in the form with the new password
        new_password="NewPassword123"
        form = response2.forms['password_reset']
        form['new_password1'] = new_password
        form['new_password2'] = new_password
        response2 = form.submit()

        #make sure that the user's password has infact changed:
        user2 = User.objects.get(id=self.user2.id)
        self.assertTrue(check_password(new_password, user2.password))
