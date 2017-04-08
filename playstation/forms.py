from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.forms.models import inlineformset_factory

from registration.forms import RegistrationFormUniqueEmail

from .models import Profile


class PlayStationIdForm(forms.ModelForm):
    """
    form to capture the PSN ID/Username.
    PSN ID's are alphanumeric PLUS hyphens (-) and underscores (_) and must start with a letter.
    """

    class Meta:
        model = User
        fields = ['psn_id']

    starts_with_letter = RegexValidator(regex='^[A-Za-z]', code='first_letter',
                                    message='PSN IDs must start with a letter.')
    form_attributes = {
        'class': 'form-control',
        'placeholder': 'PSN Username'
    }
    err_msg = {
        'invalid': 'PSN IDs may only consist of letters, numbers, hyphens (-) and underscores (_).'
    }
    psn_id = forms.SlugField(min_length=3, max_length=16, required=True,
                             widget=forms.TextInput(attrs=form_attributes),
                             validators=[starts_with_letter], error_messages=err_msg)
    

class GameSearchForm(forms.Form):
    """
    Search the PlayStation Game database for games.  Filter based on criteria.
    """
    # release_date = forms.DateField(widget=forms.DateInput(), required=False)
    maturity_rating = forms.CharField(max_length=5)
    platform = forms.CharField(max_length=4)
    title = forms.CharField(max_length=99)
    platinum = forms.BooleanField()

# RegistrationFormSet = inlineformset_factory(parent_model=User, form=PlayStationIdForm)
