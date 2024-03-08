from django.shortcuts import render,redirect
import pandas as pd
import os
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import UserTips,UserScores,Article
from django.db.models import Max, F, Count, Sum, ExpressionWrapper, FloatField, IntegerField
from django.utils import timezone
from .forms import CustomUserCreationForm
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from django.utils import translation

## Horse Raching Features Create your views here.
def racecard(request):
     id = request.GET.get('id')
     if id is None:
          id = 1
     current_datetime = timezone.now()
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/current_race_"+str(id)+".csv")
     current_race = pd.read_csv(csv_path)
     curr_race_date=current_race['Racedate'].iloc[0].replace('/','-')
     total_race = current_race['Total'].iloc[0]
     
     horse_tips_qty = UserTips.objects.filter(race_date=curr_race_date, race_no=id).values('horse_name').annotate(num_tips=Count('id'), )

    ## For Tips Sorting based on Overall Performance ##
     last_tips_by_user = (
        UserScores.objects.all()  
            .values('user', 'user__groups__name')
            .annotate(
                hit_ratio=ExpressionWrapper(F('total_hits')*100/F('total_records'), output_field=FloatField())
        )
        .order_by('-hit_ratio')  # Sort in descending order of hit ratio
    )

    ## For Tips Sorting based on Current Peformance. If the Current Performance is zero, Last Performace will be used for sorting ##
     
     curr_tips_by_user = (
        UserTips.objects.filter(race_date=curr_race_date)  # Current Tips Only
            .values('user', 'user__groups__name')
            .annotate(
            hit_pst=Sum('hit') * 100.0 / Count('hit'),
            total_dividend=Sum('dividend') - Count('hit') * 10,
        )
        .order_by('-hit_pst')  # Sort in descending order of hit ratio
    )   

    # Calculate the total sum of 'Hit' in 'curr_tips_by_user' with handling for None values
     sum_pst = 0
     for tip in curr_tips_by_user:
         sum_pst = sum_pst+tip['hit_pst']
    
     if sum_pst == 0.0:
         sort_query = last_tips_by_user
     else:
         sort_query = curr_tips_by_user
         print("## Sort_query ##", sort_query)

     

    # Organize the data by username and fetch all relevant records for each user
     last_perf_by_user = (
        UserTips.objects.filter(race_date=curr_race_date)
        .select_related('user')
        .values('user__username')
        .annotate(
                  hit_pst = Sum('hit')*100.0/Count('hit'),
                  total_dividend = Sum('dividend')-Count('hit')*10
    ))
    # Get the user scores and calculate the percentage of hits
     user_scores = UserScores.objects.annotate(
        percentage= F('total_hits') * 100.0 / F('total_records'),
            profit_percentage=ExpressionWrapper((F('total_dividend') - F('total_records') * 10) * 100.0 / (F('total_records') * 10), output_field=FloatField())
            ).order_by('-percentage')
    
     complete_tips_by_user = []
     for user_tips in sort_query:
        user_records = UserTips.objects.filter(
            user_id=user_tips['user'],
            race_date=curr_race_date,
            race_no=id
        )
      
        if user_records:
            complete_tips_by_user.append({'user': user_records[0].user, 'groups_name': user_tips['user__groups__name'], 'records': user_records})

        selected_language = translation.get_language()  # Default to Chinese if language is not provided
        recent_articles = Article.objects.filter(language=selected_language).order_by('-pub_date')[:5]
  
        context = {
            'current_race': current_race,
            'total_race': total_race,
            'current_datetime':current_datetime,
            'race_id' : id,
            'complete_tips_by_user': complete_tips_by_user,
            'user_scores': user_scores, # Add the user scores to the context
            'recent_articles': recent_articles,
            'last_perf_by_user' : last_perf_by_user,
            'horse_tips_qty' : horse_tips_qty
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

        if not UserScores.objects.filter(user=user_id).exists():
            # If not, create a new UserScores record with default values
            UserScores.objects.create(user=user_id, total_records=0, total_hits=0, total_dividend=0)
       
        # Check if records exist for the same user_id, race_date, and race_no
        existing_records = UserTips.objects.filter(user=user_id, race_date=race_date, race_no=race_no)
        if existing_records.exists():
            existing_records.delete()
        
        for horse_select in selected_horses:
            split_values = horse_select.split(".")
            horse_no=split_values[0]
            horse_name=split_values[1]
            UserTips.objects.create(user=user_id, race_date=race_date, race_no=race_no, horse_no=horse_no,horse_name=horse_name, hit=0)
        # Redirect to a success page or wherever needed
        
    return redirect('../racecard/?id='+race_no)


## Article Section ###
@login_required
def newsletter(request):
    id = request.GET.get('id')
    if id is None:
          id = 1
    id=int(id)
    selected_language = translation.get_language()  # Default to Chinese if language is not provided
    recent_articles = Article.objects.filter(language=selected_language).order_by('-pub_date')[:1]
        # Fetch articles from 3 to 13
    email_list_group = Group.objects.get(name='MailList')
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

        for recipient in recipients:
            context = {
                'subject': subject,
                'message': article.content,
            }
            message = render_to_string('blog/newsletter_email.html', context)
            send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient], html_message=message)
        
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

    selected_language = translation.get_language()  # Default to Chinese if language is not provided
    recent_articles = Article.objects.filter(language=selected_language).order_by('-pub_date')[id-1:id]
    other_articles = Article.objects.filter(language=selected_language).order_by('-pub_date')[id:id+10]
    print("## Selected Language:", selected_language)
    #recent_articles = Article.objects.order_by('-pub_date')[id-1:id]
        # Fetch articles from 3 to 13
    #other_articles = Article.objects.order_by('-pub_date')[id:id+10]
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

