from datetime import datetime, timedelta

from htmlvalidator.client import ValidatingClient

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from hackingweek.models import Category, Challenge, Team, Validation

import hackingweek.settings

def one_day_before():
    date = timezone.now() + timedelta(days=-1)
    return date.strftime('%Y-%m-%d %H:%M')

def two_day_before():
    date = timezone.now() + timedelta(days=-2)
    return date.strftime('%Y-%m-%d %H:%M')

def one_day_after():
    date = timezone.now() + timedelta(days=1)
    return date.strftime('%Y-%m-%d %H:%M')

def two_day_after():
    date = timezone.now() + timedelta(days=2)
    return date.strftime('%Y-%m-%d %H:%M')


class CheckPublicPages(TestCase):
    """Check if all public pages are accessible to anonymous users."""
    def setUp(self):
        self.now = timezone.now()

        self.client = ValidatingClient()
        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()

        self.team = Team(name='team', is_active=True)
        self.team.save()
        self.team.members.add(self.user)
        self.team.save()

        self.category = Category(name='category')
        self.category.save()

        self.challenge = Challenge(category=self.category,
                                   name='challenge', key='12345')
        self.challenge.save()

        self.validation = Validation(date=timezone.now(),
                                     user=self.user,
                                     team=self.team,
                                     challenge=self.challenge)
        self.validation.save()

    def tearDown(self):
        self.validation.delete()

        self.team.delete()
        self.user.delete()

        self.challenge.delete()
        self.category.delete()

    def test_public_homepage(self):
        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_day_after()):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_day_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

    def test_public_team_list_empty(self):
        self.team.delete()

        response = self.client.get('/team/list/')
        self.assertEqual(response.status_code, 200)

        self.team.save()

    def test_public_team_list(self):
        response = self.client.get('/team/list/')
        self.assertEqual(response.status_code, 200)

    def test_public_contestant_list_empty(self):
        self.user.delete()

        response = self.client.get('/contestant/list/')
        self.assertEqual(response.status_code, 200)

        self.user.save()

    def test_public_contestant_list(self):
        response = self.client.get('/contestant/list/')
        self.assertEqual(response.status_code, 200)

    def test_public_challenge_list_empty(self):
        self.challenge.delete()

        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_day_after()):
            response = self.client.get('/challenges/')
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get('/challenges/')
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_day_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get('/challenges/')
            self.assertEqual(response.status_code, 200)

        self.challenge.save()

    def test_public_challenge_list(self):
        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_day_after()):
            response = self.client.get('/challenges/')
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get('/challenges/')
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_day_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get('/challenges/')
            self.assertEqual(response.status_code, 200)

    def test_public_ranking_list_empty(self):
        self.validation.delete()

        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_day_after()):
            response = self.client.get('/ranking/')
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get('/ranking/')
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_day_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get('/ranking/')
            self.assertEqual(response.status_code, 200)

        self.validation.save()

    def test_public_ranking_list(self):
        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_day_after()):
            response = self.client.get('/ranking/')
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get('/ranking/')
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_day_before(),
                           CONTEST_END_DATE=one_day_before()):
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

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()

        self.team = Team(name='team')
        self.team.save()
        self.team.members.add(self.user)
        self.team.save()

        self.client = ValidatingClient()

    def tearDown(self):
        self.team.delete()
        self.user.delete()

    def test_redirection_accounts_logout(self):
        response = self.client.get('/accounts/logout/', follow=True)
        self.assertRedirects(response, '/',
                             status_code=302, target_status_code=200)

    def test_redirection_accounts_settings(self):
        response = self.client.get('/accounts/settings/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/accounts/settings/',
                             status_code=302, target_status_code=200)

    def test_redirection_accounts_password(self):
        response = self.client.get('/accounts/password/', follow=True)
        self.assertRedirects(response, '/accounts/password/reset/',
                             status_code=302, target_status_code=200)

    def test_redirection_accounts_delete(self):
        response = self.client.get('/accounts/delete/', follow=True)
        self.assertRedirects(response, '/',
                             status_code=302, target_status_code=200)

    def test_redirection_team_create(self):
        response = self.client.get('/team/create/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/team/create/',
                             status_code=302, target_status_code=200)

    def test_redirection_team_quit(self):
        response = self.client.get('/team/quit/1/', follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/team/quit/1/',
                             status_code=302, target_status_code=200)


class CheckSignUp(TestCase):
    def setUp(self):
        self.client = ValidatingClient()

    def test_signup(self):
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_day_after()):
            response = self.client.get('/accounts/signup/')
            self.assertEqual(response.status_code, 200)

            data = response.context['form'].initial
            data['username'] = 'user'
            data['password'] = 'password'
            data['password_confirm'] = 'password'
            data['email'] = 'user@mail.net'
            data['first_name'] = 'firstname'
            data['last_name'] = 'lastname'
            data['status'] = 'Bac+1'
            data['organisation'] = 'organisation'

            response = self.client.post('/accounts/signup/', data)


class CheckSettings(TestCase):
    def setUp(self):
        self.client = ValidatingClient()

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()
        self.client.login(username='test_user', password='secret')

    def test_updating_settings(self):
        response = self.client.get('/accounts/settings/')
        self.assertEqual(response.status_code, 200)

        data = response.context['form'].initial
        data['first_name'] = 'firstname'
        data['last_name'] = 'lastname'
        data['status'] = 'Bac+1'
        data['organisation'] = 'organisation'

        response = self.client.post('/accounts/settings/', data)


class CheckTeamCreation(TestCase):
    def setUp(self):
        self.client = ValidatingClient()

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()
        self.client.login(username='test_user', password='secret')

    def tearDown(self):
        self.user.delete()

    def test_logged_user_team_create(self):
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_day_after()):
            response = self.client.get('/team/create/', follow=True)
            self.assertEqual(response.status_code, 200)

            data = response.context['form'].initial
            data['name'] = 'team'

            response = self.client.post('/team/create/', data)


class CheckValdatingChallenge(TestCase):
    def setUp(self):
        self.client = ValidatingClient(enforce_csrf_checks=True)

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()
        self.client.login(username='test_user', password='secret')

        self.team = Team(name='team', is_active=True)
        self.team.save()
        self.team.members.add(self.user)
        self.team.save()

        self.category = Category(name='category')
        self.category.save()

        self.challenge = Challenge(category=self.category,
                                   name='challenge', key='12345')
        self.challenge.save()

    def tearDown(self):
        self.challenge.delete()
        self.category.delete()
        self.team.delete()
        self.user.delete()

    def test_validate_challenge(self):
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get('/challenges/', follow=True)
            self.assertEqual(response.status_code, 200)
# TODO !!!
#            data = response.context['id-1'].initial
#            data['input-1'] = '12345'

#            response = self.client.post('/validate/1/', data)


class CheckLoggedUserPages(TestCase):
    """Check if a logged user can access to private and public pages."""
    def setUp(self):
        self.now = timezone.now()

        self.client = ValidatingClient()

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()
        self.client.login(username='test_user', password='secret')

        self.team = Team(name='team', is_active=True)
        self.team.save()
        self.team.members.add(self.user)
        self.team.save()

        self.user0 = User.objects.create_user('test_user0', 'user0@test.net', 'secret')
        self.user0.save()

        self.team0 = Team(name='team0', is_active=True)
        self.team0.save()
        self.team0.members.add(self.user0)
        self.team0.save()

        self.category = Category(name='category')
        self.category.save()

        self.challenge = Challenge(category=self.category,
                                   name='challenge', key='12345')
        self.challenge.save()

        self.validation = Validation(date=self.now,
                                     user=self.user,
                                     team=self.team,
                                     challenge=self.challenge)
        self.validation.save()

        self.validation0 = Validation(date=self.now,
                                     user=self.user0,
                                     team=self.team0,
                                     challenge=self.challenge)
        self.validation0.save()

    def tearDown(self):
        self.validation0.delete()
        self.validation.delete()

        self.team0.delete()
        self.user0.delete()

        self.team.delete()
        self.user.delete()

        self.challenge.delete()
        self.category.delete()

    def test_logged_user_accounts_logout(self):
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_accounts_settings(self):
        response = self.client.get('/accounts/settings/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_accounts_password(self):
        response = self.client.get('/accounts/password/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_accounts_delete(self):
        response = self.client.get('/accounts/delete/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_team_list(self):
        response = self.client.get('/team/list/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_team_create_with_a_team(self):
        response = self.client.get('/team/create/', follow=True)
        self.assertRedirects(response, '/?next=/team/create/',
                             status_code=302, target_status_code=200)

    def test_logged_user_team_quit(self):
        response = self.client.get('/team/quit/1/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_non_existing_team_quit(self):
        response = self.client.get('/team/quit/10/')
        self.assertEqual(response.status_code, 404)

    def test_logged_user_contestant_list(self):
        response = self.client.get('/contestant/list/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_challenge_list(self):
        response = self.client.get('/challenges/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_ranking_list(self):
        response = self.client.get('/ranking/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_rules(self):
        response = self.client.get('/rules/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_about(self):
        response = self.client.get('/about/')
        self.assertEqual(response.status_code, 200)
