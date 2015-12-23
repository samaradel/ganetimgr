from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # create a user
        self.user = User(
            email='test@test.com',
            username='test',
        )
        self.user.save()

    def test_registration_url(self):
        res = self.client.get(reverse('registration.views.register'))
        self.assertEqual(res.status_code, 200)

    def test_login_url(self):
        res = self.client.get(settings.LOGIN_URL, follow=True)
        self.assertEqual(res.status_code, 200)

    def test_activate_url(self):
        res = self.client.get(reverse('activate_account', kwargs={'activation_key': 'test'}))
        self.assertEqual(res.status_code, 200)

    def test_register(self):
        data = {
            'name': 'test2',
            'surname': 'Test2',
            'phone': '1212',
            'email': 'test2@test.com',
            'username': 'test2',
            'recaptcha': 'test',
            'password1': 'test',
            'password2': 'test',
        }
        res = self.client.post(reverse('registration.views.register'), data)
        # make sure the user is redirected - form is valid
        self.assertEqual(res.status_code, 302)

        # there should be the user we just created in the db
        user = User.objects.get(email='test2@test.com')

        # make sure this new user is not active
        self.assertFalse(user.is_active)

    def test_user_profile(self):
        # there should also be a user profile
        self.user.userprofile.first_login


class UserNetworkTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # create a user
        self.user = User.objects.create_user('accounttest', 'test@test.com', 'accounttest')

    def test_user_networks(self):
        networks = self.user.userprofile.usernetwork_set.all()
        self.assertEqual(len(networks), 0)
        self.client.login(username='accounttest', password='accounttest')

        # make sure the user logged in successfully
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

        self.user.userprofile.usernetwork_set.create(network='1.1.11.1/32', user=self.user)
        networks = self.user.userprofile.usernetwork_set.all()
        self.assertEqual(len(networks), 1)

        # make a request in order to be logged out
        self.client.get('/')

        # make sure the user was logged out
        self.assertEqual(self.client.session.get('_auth_user_id'), None)
