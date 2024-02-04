from django.shortcuts import render,redirect
import pandas as pd
import os
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import UserTips,UserScores,Article
from django.db.models import Max, F



## Horse Raching Features Create your views here.
def racecard(request):
     id = request.GET.get('id')
     if id is None:
          id = 1
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/current_race_"+str(id)+".csv")
     current_race = pd.read_csv(csv_path)

     #Retrive the most recent record
     latest_tips_by_user = (
        UserTips.objects.filter(race_no=id)
        .values('user')
        .annotate(latest_race_date=Max('race_date'))
        )
    # Organize the data by username and fetch all relevant records for each user
     complete_tips_by_user = []
     for user_tips in latest_tips_by_user:
        user_records = UserTips.objects.filter(
            user_id=user_tips['user'],
            race_date=user_tips['latest_race_date'],
            race_no=id
        )
        complete_tips_by_user.append({'user': user_records[0].user, 'records': user_records})

    # Get the user scores and calculate the percentage of hits
        user_scores = UserScores.objects.filter(user__in=latest_tips_by_user.values('user')).annotate(
        percentage=F('total_hits') / F('total_records') * 100
        )

        context = {
            'current_race': current_race,
            'race_id' : id,
            'complete_tips_by_user': complete_tips_by_user,
            'user_scores': user_scores # Add the user scores to the context
        }

     return render(request, 'currentrace.html', context)

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


## Article Section ###
def about(request):
    return render(request, 'home.html')

def recent_article(request):
    recent_article = Article.objects.latest('pub_date')
    return render(request, 'blog/recent_article.html', {'article': recent_article})


## Login and Administration Session
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



