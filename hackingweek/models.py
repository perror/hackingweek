from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(User,
                                     related_name='team_list',
                                     null=True, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    
    real_name   = models.CharField(max_length=128)
    school      = models.CharField(max_length=128)
    study_level = models.CharField(max_length=8)

    team = models.ForeignKey(Team, null=True, blank=True)
