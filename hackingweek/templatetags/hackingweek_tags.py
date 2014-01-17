from django import template
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from hackingweek.models import UserProfile, Team


register = template.Library()

@register.simple_tag
def user_count():
    return User.objects.exclude(is_staff=True).count()

@register.simple_tag
def team_count():
    return Team.objects.all().count()

@register.simple_tag
def active(request, pattern):
    import re
    if re.search(reverse(pattern), request.path):
        return ' class="active"'
    else:
        return ''
