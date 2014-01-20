import account.views

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
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


class ContestantListView(ListView):
   model = UserProfile

   def get_context_data(self, **kwargs):
      context = super(ContestantListView, self).get_context_data(**kwargs)
      return context


class TeamCreateView(CreateView):
   model = Team
   success_url = reverse_lazy('team_list')
   fields = ['name']

   def form_valid(self, form):
      self.object = form.save(commit=False)
      self.object.save()

      # Adding the creator to team members
      self.object.members.add(self.request.user)

      return HttpResponseRedirect(self.get_success_url())


class TeamQuitView(DeleteView):
   model = Team
   success_url = reverse_lazy('team_list')

   def delete(self, request, pk):
      team = Team.objects.filter(pk=pk)[0]
      team.members.remove(self.request.user)

      if (team.members.count() == 0):
         team.delete()

      return HttpResponseRedirect(reverse_lazy('team_list'))
