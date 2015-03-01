from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils import timezone

from hackingweek.models import Team
from hackingweek.utils import begin_date


has_no_team = user_passes_test(lambda u: u.team_set.all().count() == 0 and timezone.now() <= begin_date(), login_url='/')

def has_no_team_required(view_func):
    decorated_view_func = login_required(has_no_team(view_func))
    return decorated_view_func

has_team = user_passes_test(lambda u: u.team_set.all().count() >= 1 or u.is_staff, login_url='/')

def has_team_required(view_func):
    decorated_view_func = login_required(has_team(view_func))
    return decorated_view_func
