from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView

import account.views

from hackingweek.decorators import has_team_required
from hackingweek.forms import SettingsForm, SignupForm, ChallengeValidationForm
from hackingweek.models import Challenge, Team, TeamJoinRequest, UserProfile, Validation
from hackingweek.utils import begin_date, end_date

def validate(request, pk):
   errors = []
   _messages = {
      "invalid_key": {
         "level": messages.ERROR,
         "text": _("Sorry, wrong key. Try again !")
         },
      "valid_key": {
         "level": messages.SUCCESS,
         "text": _("Congratulation, you found the key !")
         },
      "breakthrough": {
         "level": messages.WARNING,
         "text": _("Great, you just made a breakthrough !")
         },
      "already_done": {
         "level": messages.INFO,
         "text": _("This challenge was already done by your team !")
         },
      "before_start": {
         "level": messages.INFO,
         "text": _("The contest is not yet started !")
         },
      "after_end": {
         "level": messages.INFO,
         "text": _("The contest is finished !")
         },
      }

   # Check if the contest is open
   now = timezone.now()

   if (now <= begin_date()):
      messages.add_message(request,
                           _messages['before_start']['level'],
                           _messages['before_start']['text'])

      return HttpResponseRedirect('/challenges/')

   if (now >= end_date()):
      messages.add_message(request,
                           _messages['after_end']['level'],
                           _messages['after_end']['text'])
      return HttpResponseRedirect('/challenges/')

   if request.method == 'POST':
      form = ChallengeValidationForm(request.POST)

      if form.is_valid():
         key = form.cleaned_data['key']

         if key == Challenge.objects.get(pk=pk).key:
            # Key is valid
            messages.add_message(request,
                                 _messages['valid_key']['level'],
                                 _messages['valid_key']['text'])

            team = request.user.team_set.filter()[:1].get()
            challenge = Challenge.objects.get(pk=pk)
            try:
               Validation.objects.filter(challenge=challenge)[:1].get()
               # Not a breakthrough
               try:
                  Validation.objects.get(challenge=challenge, team=team)
                  # Team has already validated this challenge
                  messages.add_message(request,
                                       _messages['already_done']['level'],
                                       _messages['already_done']['text'])

                  return HttpResponseRedirect('/challenges/')

               except Validation.DoesNotExist:
                  # Validation was not already registered, creating it
                  validation = Validation(date=now,
                                          team=team,
                                          user=request.user,
                                          challenge=challenge)
                  validation.save()
                  team.is_active = True
                  team.save()

            except Validation.DoesNotExist:
               # Breakthrough !
               messages.add_message(request,
                                    _messages['breakthrough']['level'],
                                    _messages['breakthrough']['text'])
               validation = Validation(date=now,
                                       team=team,
                                       user=request.user,
                                       challenge=challenge)
               validation.save()
               team.is_active = True
               team.save()

            # Recompute score for everybody #
            # ############################# #
            teams =  Team.objects.filter(is_active=True).all()
            teams_count = teams.count()

            # Compute the score for each challenge and the first team
            challenge_scores = {}
            for challenge in Challenge.objects.all():
               validations = Validation.objects.filter(challenge=challenge)

               first_validation = validations.first()
               if (first_validation is not None):
                  first_team = first_validation.team
               else:
                  first_team = None

               count = validations.count()

               # challenge_score contains the score for a challenge and the
               # team which make de the breakthrough (None otherwise).
               challenge_scores[challenge.pk] = \
                           (teams_count * (teams_count - count + 1), first_team)

            # Compute the score for each team
            for team  in teams:
               score = 0
               breakthroughs = 0
               validations = Validation.objects.filter(team=team)
               for validation in validations:
                  score_challenge, first_team = challenge_scores[validation.challenge.pk]
                  score += score_challenge
                  # Get the bonus if team has a breakthrough
                  if (team == first_team):
                     score += teams_count
                     breakthroughs += 1

               team.score = score
               team.breakthroughs = breakthroughs
               team.save()

         else:
            # Key is not valid
            messages.add_message(request,
                                 _messages['invalid_key']['level'],
                                 _messages['invalid_key']['text'])

   else:
      form = ChallengeValidationForm()
      messages.add_message(request,
                           _messages['invalid_key']['level'],
                           _messages['invalid_key']['text'])

   return HttpResponseRedirect('/challenges/')


def is_contest_started():
   return timezone.now() >= begin_date()


class HomepageView(TemplateView):

   def get_context_data(self, **kwargs):
      context = super(HomepageView, self).get_context_data(**kwargs)
      context['is_contest_started'] = is_contest_started()
      context['contest_begin_date'] = begin_date().strftime('%Y %B %d %H:%M:%S')
      context['contest_end_date']   = end_date().strftime('%Y %B %d %H:%M:%S')

      return context


class ContestantView(TemplateView):
   model = User

   def get_context_data(self, **kwargs):
      context = super(ContestantView, self).get_context_data(**kwargs)

      try:
         # Get user data
         contestant = User.objects.filter(pk=self.kwargs.get('pk', None))[0]
         context['is_valid'] = not contestant.is_staff
         context['contestant'] = contestant
         context['profile'] = contestant.userprofile

         # Get team data
         try:
            team = contestant.team_set.filter()[:1].get()
            context['has_team'] = True
            context['team'] = team
         except ObjectDoesNotExist:
            context['has_team'] = False

         # Get validations data
         try:
            user_validations = Validation.objects.filter(user=contestant)

            validations = []

            for item in user_validations:
               current_validations = Validation.objects.filter(challenge=item.challenge)
               breakthrough  = (team == current_validations[:1].get().team)

               validations.append({ 'validation': item,
                                    'count' : len(current_validations),
                                    'breakthrough' : breakthrough })

            context['validations'] = validations
         except ObjectDoesNotExist:
            pass

      except IndexError:
         context['is_valid'] = False

      return context

class TeamView(TemplateView):
   model = Team

   def get_context_data(self, **kwargs):
      context = super(TeamView, self).get_context_data(**kwargs)

      try:
         # Get team data
         team = Team.objects.filter(pk=self.kwargs.get('pk', None))[0]
         context['is_valid'] = True
         context['team'] = team

         # Get validations data
         try:
            team_validations = Validation.objects.filter(team=team)

            validations = []

            for item in team_validations:
               current_validations = Validation.objects.filter(challenge=item.challenge)
               breakthrough  = (team == current_validations[:1].get().team)

               validations.append({ 'validation': item,
                                    'count' : len(current_validations),
                                    'breakthrough' : breakthrough })

            context['validations'] = validations
         except ObjectDoesNotExist:
            pass

      except IndexError:
         context['is_valid'] = False
         
      return context


class ChallengeListView(ListView):
   model = Challenge
   success_url = reverse_lazy('challenges')

   def get_context_data(self, **kwargs):
      context = super(ChallengeListView, self).get_context_data(**kwargs)
      context['active_teams'] = Team.objects.filter(is_active=True).count()

      challenge_status = {}

      if self.request.user.is_authenticated():
         try:
            team  = self.request.user.team_set.filter()[:1].get()
         except Team.DoesNotExist:
            team = None
      else:
         team = None

      for challenge in Challenge.objects.all():
         validations = Validation.objects.filter(challenge=challenge)

         try:
            validations.filter(team=team).get()
            is_done = True

            try:
               is_breakthrough = (team == validations[:1].get().team)
            except Validation.DoesNotExist:
               is_breakthrough = False

         except Validation.DoesNotExist:
            is_done = False
            is_breakthrough = False

         # challenge_status contains the number of validations of this
         # challenge, if the current team has validated it or not and
         # if it is a breakthrough.
         challenge_status[challenge.pk] = \
             (validations.count(), is_done, is_breakthrough)

         context['has_team'] = (team <> None)
         context['challenge_status'] = challenge_status
         context['is_contest_started'] = is_contest_started()

      return context


class SignupView(account.views.SignupView):
   form_class = SignupForm

   def after_signup(self, form):
      self.create_profile(form)
      super(SignupView, self).after_signup(form)

   def create_profile(self, form):
      user = self.created_user
      user.save()

      profile = user.userprofile
      profile.status       = form.cleaned_data['status']
      profile.organisation = form.cleaned_data['organisation']
      profile.save()


class SettingsView(account.views.SettingsView):
   form_class = SettingsForm

   def get_initial(self):
      initial = super(SettingsView, self).get_initial()

      initial["status"]        = self.request.user.userprofile.status
      initial["organisation"]  = self.request.user.userprofile.organisation

      return initial

   def update_settings(self, form):
      super(SettingsView, self).update_settings(form)

      user = self.request.user
      user.save()

      profile = user.userprofile
      profile.status       = form.cleaned_data['status']
      profile.organisation = form.cleaned_data['organisation']
      profile.save()


class TeamListView(ListView):
   model = Team

   def get_context_data(self, **kwargs):
      context = super(TeamListView, self).get_context_data(**kwargs)
      context['is_contest_started'] = is_contest_started()

      return context


class RankingView(ListView):
   model = Team

   def get_context_data(self, **kwargs):
      context = super(RankingView, self).get_context_data(**kwargs)

      teams =  Team.objects.filter(is_active=True).all()
      teams_count = teams.count()

      if self.request.user.is_anonymous():
         user_team = None
      else:
         try:
            user_team  = self.request.user.team_set.filter()[:1].get()
         except Team.DoesNotExist:
            user_team = None

      # Get the score for each team
      ranking = []
      for team  in teams:
         ranking.append({'pk': team.pk,
                         'name': team.name,
                         'score': team.score,
                         'validations': Validation.objects.filter(team=team).count(),
                         'breakthroughs': team.breakthroughs,
                         'user_team': (team == user_team),
                         })

      import operator
      context['ranking'] = \
          sorted(ranking,
                 key=operator.itemgetter('score','validations','breakthroughs'),
                 reverse=True)

      return context


class ContestantListView(ListView):
   model = User

   def get_queryset(self):
      return User.objects.filter(is_active=True).exclude(is_staff=True)

   def get_context_data(self, **kwargs):
      context = super(ContestantListView, self).get_context_data(**kwargs)
      return context


class TeamCreateView(CreateView):
   model = Team
   success_url = reverse_lazy('team_list')
   fields = ['name']
   messages = {
      "team_created": {
         "level": messages.SUCCESS,
         "text": _("Team has been created.")
         },
      }

   def form_valid(self, form):
      self.object = form.save(commit=False)
      self.object.save()

      # Adding the creator to team members
      self.object.members.add(self.request.user)
      if self.messages.get("team_created"):
         messages.add_message(
            self.request,
            self.messages["team_created"]["level"],
            self.messages["team_created"]["text"]
            )

      return HttpResponseRedirect(self.get_success_url())


class TeamQuitView(DeleteView):
   model = Team
   success_url = reverse_lazy('team_list')
   messages = {
      "team_quit": {
         "level": messages.SUCCESS,
         "text": _("User has been removed from team.")
         },
      "team_delete": {
         "level": messages.WARNING,
         "text": _("Team has been supressed (empty team).")
         },
      }

   def delete(self, request, pk):
      team = Team.objects.get(pk=pk)
      team.members.remove(self.request.user)
      if self.messages.get("team_quit"):
         messages.add_message(
            self.request,
            self.messages["team_quit"]["level"],
            self.messages["team_quit"]["text"]
            )

      if (team.members.count() == 0):
         team.delete()
         if self.messages.get("team_delete"):
            messages.add_message(
               self.request,
               self.messages["team_delete"]["level"],
               self.messages["team_delete"]["text"]
               )

      return HttpResponseRedirect(reverse_lazy('team_list'))


class TeamJoinRequestView(UpdateView):
   template_name = 'team-join-request.html'
   model = Team
   fields = []
   success_url = reverse_lazy('team_list')
   messages = {
      "team_join_request": {
         "level": messages.SUCCESS,
         "text": _("A request to join the team have been sent to all members.")
         },
      }

   def form_valid(self, form):
      username = self.request.user.username

      # Sending a request to join to each team member
      for member in self.object.members.all():
         joinrequest = TeamJoinRequest.create(created=timezone.now(),
                                              team=self.object,
                                              requester=self.request.user,
                                              responder=member)
         if joinrequest <> None:
            joinrequest.send_join_request()

      if self.messages.get("team_join_request"):
         messages.add_message(
            self.request,
            self.messages["team_join_request"]["level"],
            self.messages["team_join_request"]["text"]
            )

      return HttpResponseRedirect(self.get_success_url())


class TeamJoinAcceptView(UpdateView):
   template_name = 'team-join-accept.html'
   model = TeamJoinRequest
   fields = []
   slug_field = 'key'
   success_url = reverse_lazy('team_list')
   messages = {
      "team_join_accept": {
         "level": messages.SUCCESS,
         "text": _("User has been accepted in the team.")
         },
      "already_has_team": {
         "level": messages.ERROR,
         "text": _("User request cannot be completed ! This user already joined a team.")
         },
      "wrong_team": {
         "level": messages.ERROR,
         "text": _("User request cannot be completed ! This key does not match this team.")
         },
      "request_does_not_exist": {
         "level": messages.ERROR,
         "text": _("User request cannot be completed ! This request does not exist.")
         },
      }

   def get_object(self, queryset=None):
      if queryset is None:
         queryset = self.get_queryset()
      try:
         _object = queryset.get(key=self.kwargs['key'])
         if _object.key_expired():
            raise Http404()
         return _object
      except TeamJoinRequest.DoesNotExist:
         raise Http404()

   def get_queryset(self):
      return TeamJoinRequest.objects.all()

   def form_valid(self, form):
      try:
         joinrequest = TeamJoinRequest.objects.get(key=self.kwargs['key'])
         team = Team.objects.get(pk=self.kwargs['pk'])

         # Check if the Request is for the right team
         if not team == joinrequest.team:
            if self.messages.get('wrong_team'):
               messages.add_message(
                  self.request,
                  self.messages['wrong_team']['level'],
                  self.messages['wrong_team']['text']
               )
            return HttpResponseRedirect(self.get_success_url())

      except ObjectDoesNotExist:
         if self.messages.get('request_does_not_exist'):
            messages.add_message(
               self.request,
               self.messages['request_does_not_exist']['level'],
               self.messages['request_does_not_exist']['text']
            )
         return HttpResponseRedirect(self.get_success_url())

      # Check if requester has already a team or not
      if not joinrequest.requester.team_set.filter()[:1]:
         joinrequest.team.members.add(joinrequest.requester)
         joinrequest.send_join_accept()

         if self.messages.get("team_join_accept"):
            messages.add_message(
               self.request,
               self.messages["team_join_accept"]["level"],
               self.messages["team_join_accept"]["text"]
            )
      else:
         messages.add_message(
            self.request,
            self.messages['already_has_team']['level'],
            self.messages['already_has_team']['text']
         )

      joinrequest.delete()

      return HttpResponseRedirect(self.get_success_url())
