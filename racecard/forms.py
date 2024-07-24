from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
class HorseChartForm(forms.Form):
    no_of_race = forms.IntegerField(label='No of Race')
    race_date = forms.DateField(label='Race Date')

class NumberForm(forms.Form):
     No1 = forms.IntegerField(min_value=1, max_value=49)
     No2 = forms.IntegerField(min_value=1, max_value=49)
     No3 = forms.IntegerField(min_value=1, max_value=49)
     No4 = forms.IntegerField(min_value=1, max_value=49)
     No5 = forms.IntegerField(min_value=1, max_value=49)
     No6 = forms.IntegerField(min_value=1, max_value=49)
     No7 = forms.IntegerField(min_value=1, max_value=49)


class LottoForm(forms.Form):
    OPTIONS = [
        (500, '500'),
        (1000, '1000'),
        (2000, '2000'),
    ]
    option = forms.ChoiceField(choices=OPTIONS, widget=forms.RadioSelect, initial=500)
    number1 = forms.IntegerField(min_value=1, max_value=49, error_messages={
        'min_value': _('Ensure this value is greater than or equal to %(limit_value)s.'),
        'max_value': _('Ensure this value is less than or equal to %(limit_value)s.'),
    })
    number2 = forms.IntegerField(min_value=1, max_value=49, error_messages={
        'min_value': _('Ensure this value is greater than or equal to %(limit_value)s.'),
        'max_value': _('Ensure this value is less than or equal to %(limit_value)s.'),
    })
    number3 = forms.IntegerField(min_value=1, max_value=49, error_messages={
        'min_value': _('Ensure this value is greater than or equal to %(limit_value)s.'),
        'max_value': _('Ensure this value is less than or equal to %(limit_value)s.'),
    })
    number4 = forms.IntegerField(min_value=1, max_value=49, error_messages={
        'min_value': _('Ensure this value is greater than or equal to %(limit_value)s.'),
        'max_value': _('Ensure this value is less than or equal to %(limit_value)s.'),
    })
    number5 = forms.IntegerField(min_value=1, max_value=49, error_messages={
        'min_value': _('Ensure this value is greater than or equal to %(limit_value)s.'),
        'max_value': _('Ensure this value is less than or equal to %(limit_value)s.'),
    })
    number6 = forms.IntegerField(min_value=1, max_value=49, error_messages={
        'min_value': _('Ensure this value is greater than or equal to %(limit_value)s.'),
        'max_value': _('Ensure this value is less than or equal to %(limit_value)s.'),
    })
    number7 = forms.IntegerField(min_value=1, max_value=49, error_messages={
        'min_value': _('Ensure this value is greater than or equal to %(limit_value)s.'),
        'max_value': _('Ensure this value is less than or equal to %(limit_value)s.'),
    })

    def clean(self):
        cleaned_data = super().clean()
        numbers = [
            cleaned_data.get('number1'),
            cleaned_data.get('number2'),
            cleaned_data.get('number3'),
            cleaned_data.get('number4'),
            cleaned_data.get('number5'),
            cleaned_data.get('number6'),
            cleaned_data.get('number7'),
        ]
        if any(n is None for n in numbers):
            raise forms.ValidationError(_("All number fields must be filled out."))
        if len(set(numbers)) != 7:
            raise forms.ValidationError(_("Numbers must be unique."))
        return cleaned_data