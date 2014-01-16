from django import template

from django.contrib.auth.models import User
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
    if re.search(pattern, request.path):
        return ' class="active"'
    else:
        return ''
