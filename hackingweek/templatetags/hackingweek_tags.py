from django import template

from django.contrib.auth.models import User
from hackingweek.models import UserProfile, Team


register = template.Library()

@register.simple_tag
def count_users():
    return User.objects.exclude(is_staff=True).count()

@register.simple_tag
def count_teams():
    return Team.objects.all().count()

