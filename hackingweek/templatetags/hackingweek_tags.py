import datetime

from django import template
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.base import Variable, VariableDoesNotExist
from django.utils.translation import ugettext_lazy as _

from hackingweek.settings import CONTEST_START_DATE

from hackingweek.models import Challenge, Team, UserProfile, Validation


register = template.Library()

@register.simple_tag
def user_count():
    return User.objects.filter(is_active=True).exclude(is_staff=True).count()

@register.simple_tag
def team_count():
    return Team.objects.all().count()

@register.simple_tag
def challenge_count(request):
    start = \
        datetime.datetime.strptime(CONTEST_START_DATE, "%Y-%m-%d %H:%M")

    if (datetime.datetime.now() <= start):
        return 0
    else:
        challenge_count = Challenge.objects.all().count()

        if request.user.is_anonymous():
            return challenge_count
        else:
            try:
                user_team  = request.user.team_set.filter()[:1].get()
            except Team.DoesNotExist:
                return challenge_count

        validation_count = Validation.objects.filter(team=user_team).count()
        return challenge_count - validation_count

@register.simple_tag
def challenge_button_color(challenge_status, pk, has_team):
    count, is_done, is_breakthrough = challenge_status[pk]

    if (has_team):
        if (is_done):
            return "success"
        else:
            return "danger"
    else:
        return "info"

@register.simple_tag
def challenge_score(challenge_status, active_teams, pk):
    count, is_done, is_breakthrough = challenge_status[pk]

    if (count == 0):
        return active_teams * (active_teams + 1)
    elif (is_done):
        if (is_breakthrough):
            return active_teams * (active_teams - count + 2)
        else:
            return active_teams * (active_teams - count + 1)
    else:
        return active_teams * (active_teams - count)

@register.simple_tag
def challenge_button_text(challenge_status, pk, has_team):
    count, is_done, is_breakthrough = challenge_status[pk]

    if (has_team):
        if (is_done):
            return _("Done")
        else:
            return _("To Do")
    else:
        return _("View")

@register.simple_tag
def active(request, pattern):
    import re
    if re.search(reverse(pattern), request):
        return ' class="active"'
    else:
        return ''

@register.filter
def sort_lower(value, arg):
    try:
        return sorted(value,
                      key=Variable(arg).resolve,
                      cmp=lambda x,y: cmp(x.lower(), y.lower()))
    except (TypeError, VariableDoesNotExist):
        return ''

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def repeat(number):
    return range(number)
