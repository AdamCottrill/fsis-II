from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from simple_auth.tests.factories import UserFactory


class TestPasswordRecoveryIntegration(WebTest):
    '''user successfully accesses reset link and is able to change
    their password.
    '''

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

        response = self.app.get(reverse('password_reset'),
                                user=self.user1)

        form = response.forms['password_recovery']
        form['username_or_email'] = self.user2.username
        response = form.submit()

        # this would be better with reverse(something) but this url
        # does not exist anywhere that I can find.
        reset_url = '/password_reset/reset/'
        for a in response.html.findAll('a'):
            if reset_url in a['href']:
                url = a['href']
        token = url.split(reset_url)[1].strip("/")

        #now call get request with the other user to reset_password,
        #with args=token
        reset_url = '/password_reset/reset/{0}/'.format(token)
        response = self.app.get(reset_url, user= self.user2)
        #reverse stopped working here to.
        #response = self.app.get(reverse('password_reset_reset',
        #                                kwargs={'token': token}),
        #                        user= self.user2)

        #make sure the response contains the expected elements
        msg = 'Please choose your new password'
        self.assertContains(response, msg)
        self.assertContains(response, self.user2.username)

        #fill in the form with the new password
        new_password="NewPassword123"
        form = response.forms['password_reset']
        form['password1'] = new_password
        form['password2'] = new_password
        response = form.submit()

        #make sure that the user's password has infact changed:
        user2 = User.objects.get(id=self.user2.id)
        self.assertTrue(check_password(new_password, user2.password))
