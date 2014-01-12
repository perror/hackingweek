from django.db import models
from django.contrib.auth.models import User

from django.forms import ModelForm


class Contest(models.Model):
    max_team_members = 5
    begin_date = ''
    end_date = ''

class Challenge(models.Model):
    name   = models.CharField(max_length=128)
    author = models.CharField(max_length=128)
    description = models.CharField(max_length=2048)
    password = models.CharField(max_length=128)

class Team(models.Model):
    max_members = 5
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(User,
                                     related_name='team_list',
                                     null=True, blank=True)

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name']

class UserProfile(models.Model):
    user = models.OneToOneField(User)

    real_name   = models.CharField(max_length=128)
    school      = models.CharField(max_length=128)
    study_level = models.CharField(max_length=8)

    team = models.ForeignKey(Team, null=True, blank=True)
