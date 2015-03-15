import urllib
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from hackingweek import settings


class Category(models.Model):
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name_plural = "categories"

    def __unicode__(self):
        return self.name


class Challenge(models.Model):
    category = models.ForeignKey(Category)
    name     = models.CharField(max_length=128)
    author   = models.CharField(max_length=128)
    body     = models.CharField(max_length=4096)
    # TODO: Keys should be stored hashed in case somebody manage to dump the db
    key      = models.CharField(max_length=512)

    def __unicode__(self):
        return self.name


class UserProfile(models.Model):
    """Decorate the regular User model with extra information about the user"""
    user = models.OneToOneField(User)

    status       = models.CharField(max_length=32)
    organisation = models.CharField(max_length=128)


class Team(models.Model):
    name = models.CharField(max_length=128, unique=True)
    members = models.ManyToManyField(User, null=True, blank=True)

    # The 'is_active' field denotes if the team has validated at least
    # one challenge in order to know if it has to be considered as
    # active in the contest.
    is_active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Validation(models.Model):
    date = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, related_name='validation_user')
    team = models.ForeignKey(Team, related_name='validation_team')
    challenge = models.ForeignKey(Challenge, related_name='validation_challenge')


# class Score(models.Model):
#     score      = models.IntegerField(default=0)
#     team       = models.ForeignKey(Team)
#     challenges = models.ManyToManyField(Challenge,
#                                         related_name='score_challenges',
#                                         null=True, blank=True)
#     breakthroughs = models.ManyToManyField(Challenge,
#                                            related_name='score_breakthroughs',
#                                            null=True, blank=True)


# TODO: Remove empty team when the last user destroy his account
class TeamJoinRequest(models.Model):
    team      = models.ForeignKey(Team)
    requester = models.ForeignKey(User, related_name='teamjoinrequest_requester')
    responder = models.ForeignKey(User, related_name='teamjoinrequest_responder')

    created = models.DateTimeField(default=timezone.now)
    key     = models.CharField(max_length=64, unique=True)

    @classmethod
    def create(cls, request=None, **kwargs):
        # Check if a similar request already exists before proceeding
        try:
            _object = cls.objects.get(requester=kwargs['requester'],
                                      responder=kwargs['responder'],
                                      team=kwargs['team'])
            # If the request has expired keep going
            #if _object.key_expired():
            #    raise cls.DoesNotExist
            # If not, return None
            joinrequest = None
        except cls.DoesNotExist:
            from uuid import uuid1
            kwargs['key'] = uuid1().hex
            joinrequest = cls(**kwargs)
            joinrequest.save()

        return joinrequest

    def send_join_request(self):
        protocol = getattr(settings, "DEFAULT_HTTP_PROTOCOL", "http")
        current_site = Site.objects.get_current()
        accept_url = "{0}://{1}{2}".format(
            protocol,
            current_site.domain,
            reverse('team_join_accept',
                    kwargs = {'pk': self.team.pk, 'key': self.key,}
                    )
            )

        ctx = {
            "team" : self.team,
            "username" : self.requester.username,
            "current_site": current_site,
            "accept_url"  : accept_url,
            }

        subject = render_to_string("email/team_join_request_subject.txt", ctx)
        message = render_to_string("email/team_join_request_message.txt", ctx)
        send_mail(subject.rstrip(),
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.responder.email])

    def send_join_accept(self):
        ctx = {
            "team" : self.team.name,
            "responder" : self.responder.username,
            "requester" : self.requester.username,
            "site": Site.objects.get_current().name,
            }

        subject = render_to_string("email/team_join_accept_subject.txt", ctx)
        message = render_to_string("email/team_join_accept_message.txt", ctx)

        for member in self.team.members.all():
            send_mail(subject.rstrip(),
                      message,
                      settings.DEFAULT_FROM_EMAIL,
                      [member.email])

    def key_expired(self):
        expiration_date = self.created + \
            timedelta(days=settings.TEAM_JOIN_REQUEST_EXPIRE_DAYS)

        if expiration_date <= timezone.now():
            self.delete()

        return expiration_date <= timezone.now()
