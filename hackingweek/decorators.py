from datetime import datetime

from django.contrib.auth.decorators import user_passes_test, login_required

from hackingweek.models import Team
from hackingweek.settings import CONTEST_BEGIN_DATE

has_no_team = user_passes_test(lambda u: u.team_set.all().count() == 0 and datetime.now() <= CONTEST_BEGIN_DATE)

def has_no_team_required(view_func):
    decorated_view_func = login_required(has_no_team(view_func))
    return decorated_view_func

has_team = user_passes_test(lambda u: u.team_set.all().count() >= 1 or u.is_staff)

def has_team_required(view_func):
    decorated_view_func = login_required(has_team(view_func))
    return decorated_view_func
