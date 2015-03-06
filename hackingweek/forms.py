from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

import account.forms

from hackingweek.models import Challenge, Team


# List of possible status
STATUS_CHOICES = (
    ('Lyceen', 'Lyceen'),
    ('Bac+1', 'Bac+1'),
    ('Bac+2', 'Bac+2'),
    ('Bac+3', 'Bac+3'),
    ('Bac+4', 'Bac+4'),
    ('Bac+5', 'Bac+5'),
    ('Doctorant', 'Doctorant'),
    ('Professionnel',  'Professionnel'),
    )


class ChallengeForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Challenge


class ChallengeValidationForm(forms.Form):
    key = forms.CharField(max_length=128)


class SignupForm(account.forms.SignupForm):
    bio          = forms.CharField(label=_("Bio"), max_length=256,
                                   required=False, widget=forms.Textarea)
    status       = forms.ChoiceField(label=_("Status"), choices=STATUS_CHOICES)
    organisation = forms.CharField(label=_("Organisation"), max_length=128)


class SettingsForm(account.forms.SettingsForm):
    bio          = forms.CharField(label=_("Bio"), max_length=256,
                                   required=False, widget=forms.Textarea)
    status       = forms.ChoiceField(label=_("Status"), choices=STATUS_CHOICES)
    organisation = forms.CharField(label=_("Organisation"), max_length=128)
