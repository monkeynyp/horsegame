from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
class HorseChartForm(forms.Form):
    no_of_race = forms.IntegerField(label='No of Race')
    race_date = forms.DateField(label='Race Date')