from django import template
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from hackingweek.models import Challenge, Team, UserProfile, Validation

from django.template.base import Variable, VariableDoesNotExist

register = template.Library()

@register.simple_tag
def user_count():
    return User.objects.filter(is_active=True).exclude(is_staff=True).count()

@register.simple_tag
def team_count():
    return Team.objects.all().count()

@register.simple_tag
def challenge_count():
    return Challenge.objects.all().count()

@register.simple_tag
def challenge_button_color(challenge_status, pk):
    count, is_done, is_breakthrough = challenge_status[pk]

    if (is_done):
        if (is_breakthrough):
            return "warning"
        else:
            return "success"
    else:
        return "danger"

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
def challenge_button_text(challenge_status, pk):
    count, is_done, is_breakthrough = challenge_status[pk]

    if (is_done):
        if (is_breakthrough):
            return _("Breakthrough")
        else:
            return _("Done")
    elif (count > 0):
        return _("To Do")
    else:
        return _("Breakthrough")

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
def repeat(number):
    return range(number)
