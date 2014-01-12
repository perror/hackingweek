from django import forms
from django.forms.extras.widgets import SelectDateWidget

from django.utils.translation import ugettext_lazy as _

import account.forms


# List of status.
LEVEL_CHOICES = (
    ('bac+0', 'Terminale'),
    ('bac+1', 'Bac+1'),
    ('bac+2', 'Bac+2'),
    ('bac+3', 'Bac+3'),
    ('bac+4', 'Bac+4'),
    ('bac+5', 'Bac+5')
    )

class SignupForm(account.forms.SignupForm):
    real_name   = forms.CharField(label=_("Real Name"), max_length=128)
    school      = forms.CharField(label=_("School"), max_length=128)
    study_level = forms.ChoiceField(label=_("Study Level"), choices=LEVEL_CHOICES)

class SettingsForm(account.forms.SettingsForm):
    real_name   = forms.CharField(label=_("Real Name"), max_length=128)
    school      = forms.CharField(label=_("School"), max_length=128)
    study_level = forms.ChoiceField(label=_("Study Level"), choices=LEVEL_CHOICES)

class TeamForm(forms.Form):
    name = forms.CharField(max_length=128)
