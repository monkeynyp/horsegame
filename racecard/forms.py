from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import RaceComment, StockInfo

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
     #No7 = forms.IntegerField(min_value=1, max_value=49)

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
        race_date = forms.DateField(label='Race Date')

class StockInfoForm(forms.ModelForm):
    class Meta:
        model = StockInfo
        fields = ['title', 'stock_code', 'content']