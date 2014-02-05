import account.views

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView

from hackingweek.decorators import has_team_required
from hackingweek.forms import SettingsForm, SignupForm
from hackingweek.models import Challenge, Team, UserProfile

class SignupView(account.views.SignupView):
   form_class = SignupForm

   def after_signup(self, form):
      self.create_profile(form)
      super(SignupView, self).after_signup(form)

   def create_profile(self, form):
      profile = self.created_user.get_profile()
      
      profile.real_name   = form.cleaned_data['real_name']
      profile.school      = form.cleaned_data['school']
      profile.study_level = form.cleaned_data['study_level']
      
      profile.save()


class SettingsView(account.views.SettingsView):
   form_class = SettingsForm

   def get_initial(self):
      initial = super(SettingsView, self).get_initial()
      profile = self.request.user.get_profile()

      initial['real_name']   = profile.real_name
      initial['school']      = profile.school
      initial['study_level'] = profile.study_level

      return initial

   def update_settings(self, form):
      super(SettingsView, self).update_settings(form)
      
      profile = self.request.user.get_profile()
      
      profile.real_name   = form.cleaned_data['real_name']
      profile.school      = form.cleaned_data['school']
      profile.study_level = form.cleaned_data['study_level']
      
      profile.save()


class ChallengeListView(ListView):
   model = Challenge

   def get_context_data(self, **kwargs):
      context = super(ChallengeListView, self).get_context_data(**kwargs)
      return context


class TeamListView(ListView):
   model = Team

   def get_context_data(self, **kwargs):
      context = super(TeamListView, self).get_context_data(**kwargs)
      return context


class ContestantListView(ListView):
   model = UserProfile

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



from hackingweek import settings
from hackingweek.models import TeamJoinRequest

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

      # Checking but shouldn't be possible anyway...
      if (self.object.members.all().count() >= settings.TEAM_MAX_MEMBERS):
         return HttpResponseRedirect(self.get_success_url())

      # Sending a request to join to each team member
      for member in self.object.members.all():
         joinrequest = TeamJoinRequest.create(team=self.object,
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
      "wrong_team": {
         "level": messages.ERROR,
         "text": _("User request cannot be completed ! This key does not match this team.")
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
      joinrequest = TeamJoinRequest.objects.get(key=self.kwargs['key'])
      team = Team.objects.get(pk=self.kwargs['pk'])

      # FIXME: This should be checked in the get_object and NOT here!!!
      # Check if the Request is for the right team
      if not team == joinrequest.team:
         if self.messages.get("wrong_team"):
            messages.add_message(
               self.request,
               self.messages['wrong_team']['level'],
               self.messages['wrong_team']['text']
               )
         return HttpResponseRedirect(self.get_success_url())

      joinrequest.team.members.add(joinrequest.requester)
      joinrequest.send_join_accept()
      joinrequest.delete()

      if self.messages.get("team_join_accept"):
         messages.add_message(
            self.request,
            self.messages["team_join_accept"]["level"],
            self.messages["team_join_accept"]["text"]
            )

      return HttpResponseRedirect(self.get_success_url())
