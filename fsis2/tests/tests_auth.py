from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from fsis2.tests.factories import *

#class TestRegisterNewUser(TestCase):
#    
#    def setUp(self):
#        self.client = Client() 
#
#    def test_can_create_user(self):
#        users = User.objects.all().count()
#        self.assertEqual(users, 0)
#
#        postdata = {'username':'Homer', 
#                    'password1':'Simpson1',
#                    'password2':'Simpson1',}
#
#        response = self.client.post(reverse('register'), postdata)
#
#        users = User.objects.all()
#        self.assertEqual(users.count(), 1)
#        self.assertEqual(users[0].username, 'Homer')
#
#
#    def test_register_missing_username(self):
#        users = User.objects.all().count()
#        self.assertEqual(users, 0)
#
#        postdata = { 
#                    'password1':'Simpson1',
#                    'password2':'Simpson1',}
#
#        response = self.client.post(reverse('register'), postdata)
#        msg = "This field is required"
#        self.assertContains(response, msg)
#        users = User.objects.all()
#        self.assertEqual(users.count(),0)
#
#
#    def test_register_missing_password(self):
#        users = User.objects.all().count()
#        self.assertEqual(users, 0)
#
#        postdata = { 
#                    'password1':'Simpson1',
#                    'password2':'Simpson1',}
#
#        response = self.client.post(reverse('register'), postdata)
#        msg = "This field is required"
#        self.assertContains(response, msg)
#        users = User.objects.all()
#        self.assertEqual(users.count(),0)
#
#
#    def test_register_missing_mismatched_passwords(self):
#        users = User.objects.all().count()
#        self.assertEqual(users, 0)
#
#        postdata = {'username':'Homer',
#                    'password1':'Simpson1',
#                    'password2':'sampson1',}
#
#        response = self.client.post(reverse('register'), postdata)
#
#        msg = "Passwords do not match"
#        self.assertContains(response, msg)
#        users = User.objects.all()
#        self.assertEqual(users.count(),0)
#
#
#    def test_register_existing_username(self):
#
#        user = UserFactory(username='Homer')
#
#        users = User.objects.all().count()
#        self.assertEqual(users, 1)
#
#        postdata = {'username':'Homer',
#                    'password1':'Simpson1',
#                    'password2':'Simpson1',}
#
#        response = self.client.post(reverse('register'), postdata)
#
#        msg = "Username already in use."
#        self.assertContains(response, msg)
#        users = User.objects.all()
#        self.assertEqual(users.count(),1)
#            
#    def tearDown(self):
#        pass
#        
#
#class TestCanLogin(TestCase):
#    
#    def setUp(self):
#        self.client = Client() 
#        self.password = "FirstPassword1"
#        self.user = UserFactory(username='Homer', password=self.password)
#
#    def test_can_login_user(self):
#
#        postdata = {'username':'Homer',
#                    'password':self.password,}
#
#        response = self.client.post(reverse('login'), postdata, follow=True)
#        
#        self.assertEqual(response.status_code, 200)
#        #self.assertTemplateUsed(response, 'snippets/snippet_list.html')
#
#
#
#    def test_login_no_user(self):
#
#        postdata = {
#                    'password':self.password,}
#
#        response = self.client.post(reverse('login'), postdata)
#
#        msg = "Sorry, that's not a valid username or password"
#        self.assertContains(response, msg)
#
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'auth/login.html')
#
#    def test_login_no_password(self):
#
#        postdata = {'username':'Homer',}
#
#        response = self.client.post(reverse('login'), postdata)
#
#        msg = "Sorry, that's not a valid username or password"
#        self.assertContains(response, msg)
#
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'auth/login.html')
#
#
#
#    def test_login_wrong_password(self):
#
#        postdata = {'username':'Homer',
#                    'password':'WrongPassword2',}
#
#        response = self.client.post(reverse('login'), postdata)
#
#        msg = "Sorry, that's not a valid username or password"
#        self.assertContains(response, msg)
#
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'auth/login.html')
#
#
#    def tearDown(self):
#        self.user.delete()
#
#
#class TestChangePassword(TestCase):
#    
#    def setUp(self):
#        self.client = Client() 
#        self.password = "FirstPassword1"
#        self.user = UserFactory(username='Homer', password=self.password)
#
#    def test_can_change_password(self):
#        '''our user should be able to change their own password'''
#
#        login = self.client.login(username = self.user.username, 
#                          password = self.password)
#        self.assertTrue(login)
#
#        postdata = {
#                    'new_password1':'NewPassword1',
#                    'new_password2':'NewPassword1',}
#        response = self.client.post(reverse('change_password'), 
#                                    postdata, follow=True)
#
#        self.assertTemplateUsed(response, 'password_changed.html')
#
#    def test_user_not_logged_in(self):
#        '''unlogged user should not be able to view page but should be
#        redirected to the login page'''
#
#        response = self.client.get(reverse('change_password'))
#        self.assertEqual(response.status_code, 302)
#
#        response = self.client.get(reverse('change_password'), 
#                                   follow=True)
#        self.assertEqual(response.status_code, 200)
#        self.assertTemplateUsed(response, 'auth/login.html')
#
#
#    def test_change_password_missing_password(self):
#        '''If one of the password fields is left blank it we should be
#        returned to the form'''
#        
#        login = self.client.login(username = self.user.username, 
#                          password = self.password)
#        self.assertTrue(login)
#
#        postdata = {
#        
#                    'new_password2':'sampson',}
#        response = self.client.post(reverse('change_password'), postdata)
#        msg = "This field is required."
#        self.assertContains(response, msg)
#        self.assertTemplateUsed(response, 'auth/change_password.html')
#
#    def test_change_password_mismatched_passwords(self):
#        '''If the passwords do not match, we should be
#        returned to the form'''
#
#        login = self.client.login(username = self.user.username, 
#                          password = self.password)
#        self.assertTrue(login)
#
#        postdata = {
#                    'new_password1':'Simpson1',
#                    'new_password2':'sampsoN1',}
#        response = self.client.post(reverse('change_password'), postdata)
#
#        print "response = %s" % response
#
#        msg = "Passwords do not match"
#        self.assertContains(response, msg)
#        self.assertTemplateUsed(response, 'auth/change_password.html')
#
#
#    def tearDown(self):
#        pass
