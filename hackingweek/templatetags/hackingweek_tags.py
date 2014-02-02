from django import template
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from hackingweek.models import UserProfile, Team

from django.template.base import Variable, VariableDoesNotExist

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
