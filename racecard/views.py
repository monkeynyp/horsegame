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
     win_pred_path =os.path.join(settings.BASE_DIR, "racecard/data/predict_race_place_log"+str(id)+".csv")
     current_race = pd.read_csv(csv_path)
     prediction = pd.read_csv(pred_path)
     prediction = prediction.sort_values("Score", ascending = False)
     log_pred = pd.read_csv(win_pred_path)
     log_pred = log_pred.sort_values("Score", ascending = False)

     # create the context dictionary
     context = {
          'current_race': current_race,
          'prediction': prediction,
          'log_pred': log_pred,
          'race_id' : id
     }
     #return HttpResponse(template.render(context,request))
     return render(request, 'currentrace.html', context)

def lottory(request):
    last_marksixpath = os.path.join(settings.BASE_DIR, "racecard/data/marksix_hist_curr.csv")
    pred_marksixpath = os.path.join(settings.BASE_DIR, "racecard/data/mksixprediction.csv")
    last_marksix = pd.read_csv(last_marksixpath,nrows=10)
    pred_marksix = pd.read_csv(pred_marksixpath)

    context = {
        'last_marksix': last_marksix,
        'pred_marksix': pred_marksix
    }
    return render(request, 'lottory.html', context)


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

from .models import UserTips

def submit_tips(request):
    if request.method == 'POST':
        selected_horses = request.POST.getlist('selected_horses')

        # Assuming you have a user identifier, replace 'user_id' with the actual field name
        user_id = "joeytang"  # Replace with the actual user ID
        race_date="2024-01-24"
        race_no = 1
        for horse_name in selected_horses:
            UserTips.objects.create(username=user_id, race_date=race_date, race_no=race_no, horse_name=horse_name, hit=0)

        # Redirect to a success page or wherever needed
        return redirect('404.html')

    # Handle GET requests or other logic for rendering the form initially
    # ...


