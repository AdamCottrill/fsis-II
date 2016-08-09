from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from simple_auth.tests.factories import UserFactory


class TestRegisterNewUser(TestCase):

    def setUp(self):
        self.client = Client()


    def test_register_get_request_empty_form(self):

        response = self.client.get(reverse('register'))
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertContains(response, "New User Registration")
        self.assertContains(response, "Please enter your user name")
        self.assertContains(response, "password (again")


    def test_can_create_user(self):
        users = User.objects.all().count()
        self.assertEqual(users, 0)

        postdata = {'username': 'Homer',
                    'password1': 'Simpson1',
                    'password2': 'Simpson1', }

        response = self.client.post(reverse('register'), postdata)

        users = User.objects.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, 'Homer')

    def test_register_missing_username(self):
        users = User.objects.all().count()
        self.assertEqual(users, 0)

        postdata = {
            'password1': 'Simpson1',
            'password2': 'Simpson1', }

        response = self.client.post(reverse('register'), postdata)
        msg = "This field is required"
        self.assertContains(response, msg)
        users = User.objects.all()
        self.assertEqual(users.count(), 0)

    def test_register_missing_password(self):
        users = User.objects.all().count()
        self.assertEqual(users, 0)

        postdata = {
            'password1': 'Simpson1',
            'password2': 'Simpson1', }

        response = self.client.post(reverse('register'), postdata)
        msg = "This field is required"
        self.assertContains(response, msg)
        users = User.objects.all()
        self.assertEqual(users.count(), 0)

    def test_register_missing_mismatched_passwords(self):
        users = User.objects.all().count()
        self.assertEqual(users, 0)

        postdata = {'username': 'Homer',
                    'password1': 'Simpson1',
                    'password2': 'sampson1', }

        response = self.client.post(reverse('register'), postdata)

        msg = "Passwords do not match"
        self.assertContains(response, msg)
        users = User.objects.all()
        self.assertEqual(users.count(), 0)

    def test_register_existing_username(self):

        user = UserFactory(username='Homer')

        users = User.objects.all().count()
        self.assertEqual(users, 1)

        postdata = {'username': 'Homer',
                    'password1': 'Simpson1',
                    'password2': 'Simpson1', }

        response = self.client.post(reverse('register'), postdata)

        msg = "Username already in use."
        self.assertContains(response, msg)
        users = User.objects.all()
        self.assertEqual(users.count(), 1)

    def tearDown(self):
        pass


class TestCanLogin(TestCase):

    def setUp(self):
        self.client = Client()
        self.password = "FirstPassword1"
        self.user = UserFactory(username='Homer', password=self.password)

    def test_can_login_user(self):

        postdata = {'username': 'Homer',
                    'password': self.password, }

        response = self.client.post(reverse('login'), postdata, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/index.html')

    def test_login_no_user(self):

        postdata = {'password': self.password}

        response = self.client.post(reverse('login'), postdata)

        msg = "This field is required."
        self.assertContains(response, msg)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_login_no_password(self):

        postdata = {'username': 'Homer'}

        response = self.client.post(reverse('login'), postdata)

        msg = "This field is required."

        self.assertContains(response, msg)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_login_wrong_password(self):

        postdata = {'username': 'Homer', 'password': 'WrongPassword2'}

        response = self.client.post(reverse('login'), postdata)

        msg = ("Please enter a correct username and password. " +
               "Note that both fields may be case-sensitive.")
        self.assertContains(response, msg)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def tearDown(self):
        self.user.delete()


class TestCanLogout(TestCase):

    def setUp(self):
        self.client = Client()
        self.password = "FirstPassword1"
        self.user = UserFactory(username='Homer', password=self.password)

    def test_user_can_logout(self):

        login = self.client.login(username=self.user.username,
                                  password=self.password)
        self.assertTrue(login)
        self.assertIn('_auth_user_id', self.client.session)

        response = self.client.get(reverse('logout'), follow=True)

        #_auth_user_id will not be session id if we've logged out
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/logout.html')


class TestChangePassword(TestCase):

    def setUp(self):
        self.client = Client()
        self.password = "FirstPassword1"
        self.user = UserFactory(username='Homer', password=self.password)

    def test_change_password_get_request(self):
        '''A get request to the change password view should render an empty
        form'''

        login = self.client.login(username=self.user.username,
                                  password=self.password)
        self.assertTrue(login)

        response = self.client.get(reverse('change_password'), follow=True)

        self.assertTemplateUsed(response, 'auth/change_password.html')
        self.assertContains(response, "Change Password")
        self.assertContains(response, "New Password")
        self.assertContains(response, "New Password (again")

    def test_can_change_password(self):
        '''our user should be able to change their own password'''

        login = self.client.login(username=self.user.username,
                                  password=self.password)
        self.assertTrue(login)

        postdata = {'new_password1': 'NewPassword1',
                    'new_password2': 'NewPassword1'}
        response = self.client.post(reverse('change_password'),
                                    postdata, follow=True)

        self.assertTemplateUsed(response, 'auth/password_changed.html')

    def test_user_not_logged_in(self):
        '''unlogged user should not be able to view page but should be
        redirected to the login page'''

        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('change_password'),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_change_password_missing_password(self):
        '''If one of the password fields is left blank it we should be
        returned to the form'''

        login = self.client.login(username=self.user.username,
                                  password=self.password)
        self.assertTrue(login)

        postdata = {'new_password2': 'sampson'}
        response = self.client.post(reverse('change_password'), postdata)
        msg = "This field is required."
        self.assertContains(response, msg)
        self.assertTemplateUsed(response, 'auth/change_password.html')

    def test_change_password_mismatched_passwords(self):
        '''If the passwords do not match, we should be
        returned to the form'''

        login = self.client.login(username=self.user.username,
                                  password=self.password)
        self.assertTrue(login)

        postdata = {'new_password1': 'Simpson1',
                    'new_password2': 'sampsoN1'}
        response = self.client.post(reverse('change_password'), postdata)

        msg = "Passwords do not match"
        self.assertContains(response, msg)
        self.assertTemplateUsed(response, 'auth/change_password.html')

    def tearDown(self):
        pass


class TestPasswordReset(TestCase):

    def setUp(self):
        #we will need two users - one must be a super user
        self.password = "FirstPassword1"
        self.user1 = UserFactory(first_name='Homer', last_name='Simpson',
                                 username='hsimpson', is_superuser=True,
                                 password=self.password)

        self.user2 = UserFactory(first_name='George', last_name='Costanza',
                                 username='gconstanza', password=self.password)

    def test_non_logged_in_user(self):
        '''if a user is not logged in they should be redirected to the login
        form'''
        response = self.client.post(reverse('password_reset'), follow=True)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_non_superuser_redirected_to_index(self):
        '''if a user is logged, but is not a superuser they will be redirected
        to index'''

        login = self.client.login(username=self.user2.username,
                                  password=self.password)
        self.assertTrue(login)

        postdata = {'username_or_email': self.user1.username}

        response = self.client.post(reverse('password_reset'),
                                    postdata, follow=True)

        self.assertTemplateUsed(response, 'auth/index.html')

    def test_superuser_can_request_password_reset(self):
        ''' super user succefully requests reset for george '''
        login = self.client.login(username=self.user1.username,
                                  password=self.password)
        self.assertTrue(login)

        postdata = {'username_or_email': self.user2.username}

        response = self.client.post(reverse('password_reset'), postdata)

        self.assertContains(response, self.user2.username)
        msg = ("You -- or someone pretending to be you -- has " +
               "requested a password reset")
        self.assertContains(response, msg)

        self.assertTemplateUsed(response,
                                'auth/password_reset_message.html')

    def test_superuser_password_reset_for_nonexistant_user(self):
        '''super user accidentally request a passord reset for a user that
           does not exists.  He should be returned to the password reset form
           with a message explaining the problem.
        '''

        login = self.client.login(username=self.user1.username,
                                  password=self.password)
        self.assertTrue(login)

        postdata = {'username_or_email': 'kramer'}

        url = reverse('password_reset')
        response = self.client.post(url, postdata)

        msg = 'An active user could not be found.'
        self.assertContains(response, msg)
        self.assertTemplateUsed(response,
                                'auth/reset_password.html')


    def test_user_tries_access_invalid_link(self):
        """if a user tries to access an incorrect/expired reset link with a
        get request an appropritate message should be included in the
        response.
        """

        login = self.client.login(username=self.user2.username,
                                  password=self.password)
        self.assertTrue(login)
        response = self.client.post(reverse('password_reset_confirm',
                                           kwargs={'uidb64': 'MW7',
                                                   'token': '1234'}),
                                    follow=True)
        self.assertTemplateUsed(response, 'auth/change_password.html')
        msg = 'The reset password link is no longer valid.'
        self.assertContains(response, msg)

    def tearDown(self):
        pass
