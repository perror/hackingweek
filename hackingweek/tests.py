from datetime import datetime, timedelta

from htmlvalidator.client import ValidatingClient

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils import timezone

from hackingweek.models import Category, Challenge, Team, TeamJoinRequest, Validation
from hackingweek.forms import ChallengeValidationForm

def one_day_before():
    date = timezone.now() + timedelta(days=-1)
    return date.strftime('%Y-%m-%d %H:%M')

def two_days_before():
    date = timezone.now() + timedelta(days=-2)
    return date.strftime('%Y-%m-%d %H:%M')

def one_day_after():
    date = timezone.now() + timedelta(days=1)
    return date.strftime('%Y-%m-%d %H:%M')

def two_days_after():
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
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_days_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)

    def test_public_team_list_empty(self):
        self.team.delete()

        response = self.client.get(reverse('team_list'))
        self.assertEqual(response.status_code, 200)

        self.team.save()

    def test_public_team_list(self):
        response = self.client.get(reverse('team_list'))
        self.assertEqual(response.status_code, 200)

    def test_public_contestant_list_empty(self):
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            self.user.delete()

            response = self.client.get(reverse('contestant_list'))
            self.assertEqual(response.status_code, 200)

        self.user.save()

    def test_public_contestant_list(self):
        response = self.client.get(reverse('contestant_list'))
        self.assertEqual(response.status_code, 200)

    def test_public_challenge_list_empty(self):
        self.challenge.delete()

        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.get(reverse('challenges'))
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get(reverse('challenges'))
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_days_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get(reverse('challenges'))
            self.assertEqual(response.status_code, 200)

        self.challenge.save()

    def test_public_challenge_list(self):
        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.get(reverse('challenges'))
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get(reverse('challenges'))
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_days_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get(reverse('challenges'))
            self.assertEqual(response.status_code, 200)

    def test_public_ranking_list_empty(self):
        self.validation.delete()
        self.team.is_active = False
        self.team.save()

        response = self.client.get(reverse('ranking'))
        self.assertEqual(response.status_code, 200)

        self.team.is_active = True
        self.team.save()
        self.validation.save()

    def test_public_ranking_list(self):
        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.get(reverse('ranking'))
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get(reverse('ranking'))
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_days_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get(reverse('ranking'))
            self.assertEqual(response.status_code, 200)

    def test_public_rules(self):
        response = self.client.get(reverse('rules'))
        self.assertEqual(response.status_code, 200)

    def test_public_about(self):
        response = self.client.get(reverse('about'))
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
        self.assertRedirects(response, reverse('home'),
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
        self.assertRedirects(response, reverse('home'),
                             status_code=302, target_status_code=200)

    def test_redirection_team_create(self):
        response = self.client.get(reverse('team_create'), follow=True)
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
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.get('/accounts/signup/')
            self.assertEqual(response.status_code, 200)

            data = response.context['form'].initial
            data['username'] = 'user'
            data['password'] = 'password'
            data['password_confirm'] = 'password'
            data['email'] = 'user@mail.net'
            data['bio'] = ''
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
        data['bio'] = ''
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
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.get(reverse('team_create'), follow=True)
            self.assertEqual(response.status_code, 200)

            data = response.context['form'].initial
            data['name'] = 'team'

            response = self.client.post(reverse('team_create'), data)


class CheckTeamJoin(TestCase):
    def setUp(self):
        self.client = ValidatingClient()

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()
        self.client.login(username='test_user', password='secret')

        self.user0 = User.objects.create_user('test_user0', 'user0@test.net', 'secret')
        self.user0.save()

        self.team = Team(name='team')
        self.team.save()
        self.team.members.add(self.user0)
        self.team.save()

    def tearDown(self):
        self.user.delete()
        self.team.delete()

    def test_logged_user_team_join(self):
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            url = '/team/join/request/' + str(self.team.pk) + '/'

            response = self.client.get(url)
            response = self.client.post(url, {})

            self.assertRedirects(response, reverse('team_list'),
                                 status_code=302, target_status_code=200)

            # Trying to resubmit
            response = self.client.post(url, {})

            self.assertRedirects(response, reverse('team_list'),
                                 status_code=302, target_status_code=200)

            self.client.logout()
            self.client.login(username='test_user0', password='secret')

            fake_key = '1'
            url = '/team/join/accept/' + str(self.team.pk) + '/' + fake_key + '/'
            response = self.client.post(url, {})

            key = TeamJoinRequest.objects.get(pk=1).key
            url = '/team/join/accept/' + str(self.team.pk) + '/' + key + '/'
            response = self.client.post(url, {})


class CheckTeamQuit(TestCase):
    """Check if all private pages are properly redirected to public pages."""
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()
        self.client.login(username='test_user', password='secret')

        self.team = Team(name='team')
        self.team.save()
        self.team.members.add(self.user)
        self.team.save()

    def tearDown(self):
        self.team.delete()
        self.user.delete()

    def test_team_quit(self):
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            url = '/team/quit/' + str(self.team.pk) + '/'

            response = self.client.get(url)
            response = self.client.post(url, {})

            self.assertRedirects(response, reverse('team_list'),
                                 status_code=302, target_status_code=200)


class CheckValidatingChallenge(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user('test_user', 'user@test.net', 'secret')
        self.user.save()

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

    def tearDown(self):
        self.challenge.delete()
        self.category.delete()
        self.team.delete()
        self.user.delete()
        self.team0.delete()
        self.user0.delete()

    def test_unlogged_attempt_challenge(self):
        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, '/accounts/login/?next=/validate/1/',
                                 status_code=302, target_status_code=200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, '/accounts/login/?next=/validate/1/',
                                 status_code=302, target_status_code=200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_days_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, '/accounts/login/?next=/validate/1/',
                                 status_code=302, target_status_code=200)

    def test_invalid_get_challenge(self):
        self.client.login(username='test_user', password='secret')

        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get('/validate/1/')
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)

    def test_invalid_challenge(self):
        self.client.login(username='test_user', password='secret')

        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.post('/validate/1/', {'key' : '1'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.post('/validate/1/', {'key' : '1'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_days_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.post('/validate/1/', {'key' : '1'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)

    def test_validate_breakthrought_challenge(self):
        self.client.login(username='test_user', password='secret')

        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_days_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)

    def test_validate_normal_challenge(self):
        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            # First validation (breakthrough)
            self.client.login(username='test_user', password='secret')

            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)
            self.client.logout()
            # Second validation (normal)
            self.client.login(username='test_user0', password='secret')

            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)

            # Re-validation (normal)
            self.client.login(username='test_user0', password='secret')

            response = self.client.post('/validate/1/', {'key' : '12345'})
            self.assertRedirects(response, reverse('challenges'),
                                 status_code=302, target_status_code=200)


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
        # Before contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)

        # During contest
        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)

        # After contest
        with self.settings(CONTEST_BEGIN_DATE=two_days_before(),
                           CONTEST_END_DATE=one_day_before()):
            response = self.client.get(reverse('home'))
            self.assertEqual(response.status_code, 200)

    def test_logged_user_team_list(self):
        with self.settings(CONTEST_BEGIN_DATE=one_day_after(),
                           CONTEST_END_DATE=two_days_after()):
            self.team.delete()
            response = self.client.get(reverse('team_list'))
            self.assertEqual(response.status_code, 200)
            self.team.save()

        with self.settings(CONTEST_BEGIN_DATE=one_day_before(),
                           CONTEST_END_DATE=one_day_after()):
            response = self.client.get(reverse('team_list'))
            self.assertEqual(response.status_code, 200)

    def test_logged_user_team_create_with_a_team(self):
        response = self.client.get(reverse('team_create'), follow=True)
        self.assertRedirects(response, '/?next=/team/create/',
                             status_code=302, target_status_code=200)

    def test_logged_user_team_quit(self):
        response = self.client.get('/team/quit/1/')
        self.assertEqual(response.status_code, 200)

    def test_logged_user_non_existing_team_quit(self):
        response = self.client.get('/team/quit/10/')
        self.assertEqual(response.status_code, 404)

    def test_logged_user_contestant_list(self):
        response = self.client.get(reverse('contestant_list'))
        self.assertEqual(response.status_code, 200)

    def test_logged_user_challenge_list(self):
        response = self.client.get(reverse('challenges'))
        self.assertEqual(response.status_code, 200)

    def test_logged_user_ranking_list(self):
        response = self.client.get(reverse('ranking'))
        self.assertEqual(response.status_code, 200)

    def test_logged_user_rules(self):
        response = self.client.get(reverse('rules'))
        self.assertEqual(response.status_code, 200)

    def test_logged_user_about(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
