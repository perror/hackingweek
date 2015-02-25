from django.contrib.auth.models import User
from django.test import Client, TestCase
from htmlvalidator.client import ValidatingClient

from hackingweek.models import Category, Challenge, UserProfile

def wrong_challenge():
    chall = Challenge()
    chall.category = 'a'

class ChallengeMethodTests(TestCase):

    def test_unknown_category(self):
        self.assertRaises(ValueError, wrong_challenge)

    def test_Challenge_creation(self):
        chall = Challenge()
        mycat = Category('my category')
        chall.category = mycat
        chall.name = 'my challenge'
        chall.author = 'anonymous'
        chall.body = 'No comment'
        chall.key = '12345'


class CheckPublicPages(TestCase):
    """Check if all public pages are accessible to anonymous users."""

    def setUp(self):
        self.client = ValidatingClient()

    def test_public_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_public_team_list(self):
        response = self.client.get('/team/list/')
        self.assertEqual(response.status_code, 200)

    def test_public_contestant_list(self):
        response = self.client.get('/contestant/list/')
        self.assertEqual(response.status_code, 200)

    def test_public_challenges(self):
        response = self.client.get('/challenges/')
        self.assertEqual(response.status_code, 200)

    def test_public_ranking(self):
        response = self.client.get('/ranking/')
        self.assertEqual(response.status_code, 200)

    def test_public_rules(self):
        response = self.client.get('/rules/')
        self.assertEqual(response.status_code, 200)

    def test_public_about(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

    def test_public_login(self):
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_public_account_signup(self):
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)


class CheckRedirectionFromPrivatePages(TestCase):
    """Check if all private pages are properly redirected to public pages."""
    def setUp(self):
        self.client = ValidatingClient()

    def test_redirection_account_settings(self):
        response = self.client.get('/accounts/settings/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/accounts/settings/',
                             status_code=302, target_status_code=200)

    def test_redirection_account_password(self):
        response = self.client.get('/accounts/password/', follow=True)
        self.assertRedirects(response, '/accounts/password/reset/',
                             status_code=302, target_status_code=200)

    def test_redirection_account_delete(self):
        response = self.client.get('/accounts/delete/', follow=True)
        self.assertRedirects(response, '/',
                             status_code=302, target_status_code=200)


class CheckLoggedUserPages(TestCase):
    """Check if a logged user can access to private and public pages."""
    def setUp(self):
        self.client = ValidatingClient()
        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.client.login(username='test_user', password='secret')

    def test_logged_user_account_settings(self):
        response = self.client.get('/accounts/settings/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_account_password(self):
        response = self.client.get('/accounts/password/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_account_delete(self):
        response = self.client.get('/accounts/delete/')
        self.assertEqual(response.status_code, 200)

    def test_public_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_public_team_list(self):
        response = self.client.get('/team/list/')
        self.assertEqual(response.status_code, 200)

    def test_public_contestant_list(self):
        response = self.client.get('/contestant/list/')
        self.assertEqual(response.status_code, 200)

    def test_public_challenges(self):
        response = self.client.get('/challenges/')
        self.assertEqual(response.status_code, 200)

    def test_public_ranking(self):
        response = self.client.get('/ranking/')
        self.assertEqual(response.status_code, 200)

    def test_public_rules(self):
        response = self.client.get('/rules/')
        self.assertEqual(response.status_code, 200)

    def test_public_about(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
            self.user.delete()
