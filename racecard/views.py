from django.shortcuts import render,redirect
from django.template import loader
import pandas as pd
import os
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required



# Create your views here.
def racecard(request):
     id = request.GET.get('id')
     if id is None:
          id = 1
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/current_race_"+str(id)+".csv")
     pred_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_place"+str(id)+".csv")
     win_pred_path =os.path.join(settings.BASE_DIR, "racecard/data/predict_race_win"+str(id)+".csv")
     current_race = pd.read_csv(csv_path)
     prediction = pd.read_csv(pred_path)
     prediction = prediction.sort_values("Score", ascending = False)
     win_pred = pd.read_csv(win_pred_path)
     win_pred = win_pred.sort_values("Score", ascending = False)

     # create the context dictionary
     context = {
          'current_race': current_race,
          'prediction': prediction,
          'win_pred': win_pred
     }
     #return HttpResponse(template.render(context,request))
     return render(request, 'currentrace.html', context)

def about(request):
    return render(request, 'home.html')

@login_required
def contact(request):
     return render(request, 'contact.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('contact')  # replace with the actual URL
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('contact')  # replace with the actual URL
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')  # replace with the actual URL

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('contact')  # replace with the actual URL
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration_form.html', {'form': form})

