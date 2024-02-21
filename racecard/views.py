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
from django.utils import timezone
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group


## Horse Raching Features Create your views here.
def racecard(request):
     id = request.GET.get('id')
     if id is None:
          id = 1
     current_datetime = timezone.now()
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/current_race_"+str(id)+".csv")
     current_race = pd.read_csv(csv_path)
     curr_race_date=current_race['Racedate'].iloc[0].replace('/','-')
     #Retrive the most recent record of user tips
     latest_tips_by_user = (
        UserTips.objects.filter(race_no=id, race_date=curr_race_date)
        .values('user')
        .annotate(latest_race_date=Max('race_date'))
    )
     print(latest_tips_by_user)
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
        
        user_scores = UserScores.objects.annotate(
                    percentage= F('total_hits') * 100.0 / F('total_records'),
                    profit =  F('total_dividend') - F('total_records')*10
        ).order_by('-percentage')

        #user_scores = UserScores.objects.filter(user__in=latest_tips_by_user.values('user')).annotate(
        #    percentage= F('total_hits') * 100.0 / F('total_records')  
        #).order_by('-percentage')
        recent_articles = Article.objects.order_by('-pub_date')[:2]
        context = {
            'current_race': current_race,
            'current_datetime':current_datetime,
            'race_id' : id,
            'complete_tips_by_user': complete_tips_by_user,
            'user_scores': user_scores, # Add the user scores to the context
            'recent_articles': recent_articles,
        }
       
     return render(request, 'currentrace.html', context)

def submit_tips(request):
    if request.method == 'POST':
        selected_horses = request.POST.getlist('selected_horses')
        print(selected_horses)
        # Assuming you have a user identifier, replace 'user_id' with the actual field name
        user_id = request.user  # Replace with the actual user ID
        race_date=request.POST['race_date'].replace('/','-')
        race_no = request.POST['race_no']
        for horse_select in selected_horses:
            split_values = horse_select.split(".")
            horse_no=split_values[0]
            horse_name=split_values[1]
            UserTips.objects.create(user=user_id, race_date=race_date, race_no=race_no, horse_no=horse_no,horse_name=horse_name, hit=0)
        # Redirect to a success page or wherever needed
    return redirect('../racecard/?id='+race_no)


## Article Section ###
def newsletter(request):
    id = request.GET.get('id')
    if id is None:
          id = 1
    id=int(id)
    recent_articles = Article.objects.order_by('-pub_date')[id-1:id]
        # Fetch articles from 3 to 13
    email_list_group = Group.objects.get(name='MailList Memeber')
    print(email_list_group)
    emails = User.objects.filter(groups=email_list_group).values_list('email', flat=True)
    print(emails)
    context = {
        'recent_articles': recent_articles,
        'emails': emails
    }
    return render(request, 'blog/newsletter.html', context)
def privacy(request):
    return render(request, 'privacy.html')

def disclaimer(request):
    return render(request, 'disclaimer.html')

def send_article_email(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        article = Article.objects.get(pk=article_id)
        recipients = request.POST.getlist('recipients')
        subject = article.title
        message = article.content
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipients)
        return redirect('newsletter')
        # Redirect or show a success message
    else:
        # Handle GET request
        pass

def recent_article(request):
    id = request.GET.get('id')
    if id is None:
          id = 1
    id=int(id)
    recent_articles = Article.objects.order_by('-pub_date')[id-1:id]
        # Fetch articles from 3 to 13
    other_articles = Article.objects.order_by('-pub_date')[id:id+10]
    context = {
        'recent_articles': recent_articles,
        'other_articles': other_articles,
    }

    return render(request, 'blog/articles.html', context)


## Login and Administration Session
#@login_required
def contact(request):
     return render(request, 'contact.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('racecard')  # replace with the actual URL
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/registration_form.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('racecard')  # replace with the actual URL
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
    

def user_logout(request):
    logout(request)
    return redirect('login')  # replace with the actual URL

#login_required
def member(request):
     return render(request, 'member.html')

