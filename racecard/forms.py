from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import RaceComment

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
class HorseChartForm(forms.Form):
    no_of_race = forms.IntegerField(label='No of Race')
    race_date = forms.DateField(label='Race Date')

class NumberForm(forms.Form):
    number = forms.IntegerField(label='Number')

class LottoForm(forms.Form):
    option = forms.ChoiceField(choices=[(10, 'Last 10 draws'), (20, 'Last 20 draws'), (30, 'Last 30 draws')])
    number1 = forms.IntegerField()
    number2 = forms.IntegerField()
    number3 = forms.IntegerField()
    number4 = forms.IntegerField()
    number5 = forms.IntegerField()
    number6 = forms.IntegerField()
    number7 = forms.IntegerField()

class LottoTrioForm(forms.Form):
    number1 = forms.IntegerField()
    number2 = forms.IntegerField()
    number3 = forms.IntegerField()

class RaceCommentForm(forms.ModelForm):
    class Meta:
        model = RaceComment
        fields = ['comment']