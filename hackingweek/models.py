from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models

class Contest(models.Model):
    max_team_members = 5
    start_date = models.DateTimeField("Starting time")
    end_date   = models.DateTimeField("Ending time")


class Challenge(models.Model):
    category = models.CharField(max_length=128)
    name     = models.CharField(max_length=128)
    author   = models.CharField(max_length=128)
    summary  = models.CharField(max_length=2048)
    key      = models.CharField(max_length=128)


class Team(models.Model):
    max_members = 5
    name = models.CharField(max_length=128, unique=True)
    members = models.ManyToManyField(User, null=True, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    real_name   = models.CharField(max_length=128)
    school      = models.CharField(max_length=128)
    study_level = models.CharField(max_length=8)
