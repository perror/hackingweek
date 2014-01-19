import account.views

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from hackingweek.forms import SettingsForm, SignupForm
from hackingweek.models import UserProfile, Team


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


class TeamListView(ListView):
   model = Team

   def get_context_data(self, **kwargs):
      context = super(TeamListView, self).get_context_data(**kwargs)
      return context


class UserListView(ListView):
   model = UserProfile

   def get_context_data(self, **kwargs):
      context = super(UserListView, self).get_context_data(**kwargs)
      return context


class TeamCreate(CreateView):
   model = Team
   fields = ['name']

   def form_valid(self, form):
      self.object = form.save(commit=False)
      self.object.save()

      # Adding the creator to team members
      self.object.members.add(self.request.user)

      return HttpResponseRedirect(self.get_success_url())

   def get_success_url(self):
      return reverse('teams_list')
