from datetime import datetime

from django.conf import settings
from django.utils import timezone

def begin_date():
    return timezone.make_aware(datetime.strptime(settings.CONTEST_BEGIN_DATE,
                                                 '%Y-%m-%d %H:%M'),
                               timezone.get_current_timezone())

def end_date():
    return timezone.make_aware(datetime.strptime(settings.CONTEST_END_DATE,
                                                 '%Y-%m-%d %H:%M'),
                               timezone.get_current_timezone())
