from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import models
from django.template.loader import render_to_string

from account.utils import random_token

import urllib

from hackingweek import settings

class Challenge(models.Model):
    category = models.CharField(max_length=128)
    name     = models.CharField(max_length=128)
    author   = models.CharField(max_length=128)
    summary  = models.CharField(max_length=2048)
    key      = models.CharField(max_length=128)


class Team(models.Model):
    # FIXME: should be removed, but see in templates/team-list.html
    max_members = settings.TEAM_MAX_MEMBERS
    name = models.CharField(max_length=128, unique=True)
    members = models.ManyToManyField(User, null=True, blank=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User)

    real_name   = models.CharField(max_length=128)
    school      = models.CharField(max_length=128)
    study_level = models.CharField(max_length=8)


from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from hackingweek.managers import TeamJoinRequestManager

class TeamJoinRequest(models.Model):
    team      = models.ForeignKey(Team)
    requester = models.ForeignKey(User, related_name='teamjoinrequest_requester')
    responder = models.ForeignKey(User, related_name='teamjoinrequest_responder')

    created = models.DateTimeField(default=timezone.now())
    sent = models.DateTimeField(null=True)
    key = models.CharField(max_length=64, unique=True)

    objects = TeamJoinRequestManager()

    @classmethod
    def create(cls, request=None, **kwargs):
        # Check if a similar request already exists before proceeding
        try:
            cls.objects.get(requester=kwargs['requester'],
                            responder=kwargs['responder'],
                            team=kwargs['team'])
            joinrequest = None
        except cls.DoesNotExist:
            kwargs['key'] = random_token()
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
        expiration_date = self.sent + \
            datetime.timedelta(days=settings.TEAM_JOIN_REQUEST_EXPIRE_DAYS)

        return expiration_date <= timezone.now()

    key_expired.boolean = True
