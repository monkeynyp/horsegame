from django.shortcuts import render,redirect
import pandas as pd
import os,json,math,random,time
import requests
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import  UserTips,UserScores,Article,Marksix_hist,Marksix_user_rec,TW_lotto_hist,LottoTrioSearch
from django.db.models import Max, F, Count, Sum, ExpressionWrapper, FloatField, IntegerField,Q
from django.utils import timezone
from .forms import CustomUserCreationForm,NumberForm,LottoForm,LottoTrioForm
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from django.template.loader import render_to_string
from django.utils import translation
from django.http import JsonResponse,HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from .get_results import get_results
from django.contrib import messages
from datetime import datetime, date
from sklearn.neighbors import KNeighborsRegressor


## Horse Raching Features Create your views here.
def racecard(request):
     id = request.GET.get('id')
     if id is None:
          id = 1
     current_datetime = timezone.now()
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/current_race_"+str(id)+".csv")
     current_race = pd.read_csv(csv_path)
     odds_path = os.path.join(settings.BASE_DIR, "racecard/data/race_odds_"+str(id)+".csv")
     current_odds = pd.read_csv(odds_path)
     creation_time = os.path.getctime(odds_path)
     odds_time = time.strftime('%H:%M:%S', time.localtime(creation_time))
     current_race["Win"] = current_odds["win"]
     current_race["Place"] = current_odds["place"]
     curr_race_date=current_race['Racedate'].iloc[0].replace('/','-')
     dt_obj = datetime.strptime(curr_race_date, "%Y-%m-%d")
     timestamp = int(dt_obj.timestamp())+int(id)
     race_time = current_race['RaceTime'].iloc[0]
     print("Race_timne:", race_time)
     random.seed(timestamp)
     # Generate random integers between 1 and 64
     num_rows = len(current_race)

     random_numbers_list = [random.randint(1, 64) for _ in range(num_rows)]
     # Add the 'Rand' column to the DataFrame
     current_race['Ichi'] = random_numbers_list

     total_race = current_race['Total'].iloc[0]

     print("Total race:",total_race)
     horse_tips_qty = (
        UserTips.objects
        .filter(race_date=curr_race_date, race_no=id)
        .values('horse_name', 'user__groups__name')
        .annotate(num_tips=Count('id'))
    )
     
     tips_qty_by_type = (
        UserTips.objects
        .filter(race_date=curr_race_date, race_no=id)
        .values('user__groups__name')
        .annotate(num_users=Count('user', distinct=True))
    )


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
         #print("## Sort_query ##", sort_query)

     request.session['curr_tips_by_user'] = list(curr_tips_by_user)
     request.session['curr_race_date'] = curr_race_date
     request.session['total_race']= int(total_race)

    # Organize the data by username and fetch all relevant records for each user
     last_perf_by_user = (
        UserTips.objects.filter(race_date=curr_race_date)
        .select_related('user')
        .values('user__username')
        .annotate(
                  hit_pst = Sum('hit')*100.0/Count('hit'),
                  total_dividend = Sum('dividend')-Count('hit')*10
    ))
     request.session['last_perf_by_user'] = list(last_perf_by_user)
    # Get the user scores and calculate the percentage of hits
     user_scores = UserScores.objects.annotate(
        percentage= F('total_hits') * 100.0 / F('total_records'),
        confidence = F('hit_weight')* 100.0,
            profit_percentage=ExpressionWrapper((F('total_dividend') - F('total_records') * 10) * 100.0 / (F('total_records') * 10), output_field=FloatField())
            ).order_by('-percentage')
    
     #request.session['user_scores'] = list(user_scores)

     complete_tips_by_user = []
     for user_tips in sort_query:
        user_records = UserTips.objects.filter(
            user_id=user_tips['user'],
            race_date=curr_race_date,
            race_no=id
        ).order_by('race_no')
      
        if user_records:
            complete_tips_by_user.append({'user': user_records[0].user, 'groups_name': user_tips['user__groups__name'], 'records': user_records})

        selected_language = translation.get_language()  # Default to Chinese if language is not provided
        recent_articles = Article.objects.filter(language=selected_language).order_by('-pub_date')[:5]


        context = {
            'current_race': current_race,
            'odds_time': odds_time,
            'total_race': total_race,
            'race_time': race_time,
            'current_datetime':current_datetime,
            'race_id' : id,
            'complete_tips_by_user': complete_tips_by_user,
            'user_scores': user_scores, # Add the user scores to the context
            'recent_articles': recent_articles,
            'last_perf_by_user' : last_perf_by_user,
            'horse_tips_qty' : horse_tips_qty,
            'tips_qty_by_type': tips_qty_by_type
        }
       
     return render(request, 'currentrace.html', context)

def submit_tips(request):
    if request.method == 'POST':
        selected_horses = request.POST.get('selection_sequence')
        selected_horses = selected_horses.split(',') 
        # Process the horse name and jockey
        for horse_jockey in selected_horses:
            horse_name, jockey_name,trainer_name,horse_name_cn = horse_jockey.split('|')
        # Now you can work with horse_name and jockey_name separately
        print(f"Horse: {horse_name}, Jockey: {jockey_name}, trainer: {trainer_name}")
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
        rank =0
        for horse_select in selected_horses:
            
            split_values = horse_select.split(".")
            horse_no=split_values[0]
            horse_name=split_values[1].split("|")[0]
            jockey = split_values[2].split("|")[0]
            trainer = split_values[3].split("|")[0]
            horse_name_cn = split_values[4]
            print("HorseCN:",horse_name_cn)
            rank=rank+1
            if rank == 1:
                jockey_score = 12
                trainer_score = 12
            elif rank == 2:
                jockey_score = 6
                trainer_score = 6
            elif rank == 3:
                jockey_score = 4
                trainer_score = 4
            
            UserTips.objects.create(user=user_id, race_date=race_date, race_no=race_no,rank=rank,jockey_score=jockey_score,trainer_score=trainer_score, horse_no=horse_no,horse_name=horse_name,horse_name_cn=horse_name_cn, jockey=jockey,trainer=trainer,hit=0)
        # Redirect to a success page or wherever needed
        
    return redirect('../racecard/?id='+race_no)

def view_by_member(request):
    curr_tips_by_user = request.session.get('curr_tips_by_user',[])
    curr_race_date = request.session.get('curr_race_date')
    last_perf_by_user = request.session.get('last_perf_by_user',[])
    user_scores = request.session.get('user_scores',[])

    print(curr_tips_by_user)
    print(curr_race_date)

    complete_tips_by_user = []
    for user_tips in curr_tips_by_user:
        user_records = UserTips.objects.filter(
            user_id=user_tips['user'],
            race_date=curr_race_date,
        )
    
        if user_records:
            records_by_race_no = {}
            for record in user_records:
                race_no = record.race_no
                if race_no not in records_by_race_no:
                    records_by_race_no[race_no] = []
                records_by_race_no[race_no].append(record)
            
            complete_tips_by_user.append({
                'user': user_records[0].user, 
                'groups_name': user_tips['user__groups__name'], 
                'records_by_race_no': records_by_race_no
            })
    user_scores = UserScores.objects.annotate(
        percentage= F('total_hits') * 100.0 / F('total_records'),
            profit_percentage=ExpressionWrapper((F('total_dividend') - F('total_records') * 10) * 100.0 / (F('total_records') * 10), output_field=FloatField())
            ).order_by('-percentage')
    print("Last Pref:", user_scores)
    context = {
            'complete_tips_by_user': complete_tips_by_user,
            'last_perf_by_user' : last_perf_by_user,
            'user_scores': user_scores
    }
    return render(request, 'view_by_member.html', context)

def jockey_king(request):
    #if request.session.get('button_clicked')!=True:
        # Change the button's behavior after the first click
     #   return redirect('click_ads')  # Redirect to external URL
    
    #print('test123',request.session.get('button_clicked'))
    # Step 1: Get the most recent race_date
    recent_race_date = UserTips.objects.aggregate(Max('race_date'))['race_date__max']

    # Step 2: Filter UserTips by the most recent race_date
    recent_tips = UserTips.objects.filter(race_date=recent_race_date)

    # Step 3: Group by 'user' and 'jockey', then accumulate (sum) the jockey_scores
    jockey_scores = recent_tips.values('user__username', 'jockey') \
        .annotate(total_jockey_score=Sum('jockey_score')) \
        .order_by('user__username', '-total_jockey_score')  # Order by user first, then score descending
        # Get the user scores and calculate the percentage of hits
    user_scores = UserScores.objects.annotate(
        percentage= F('total_hits') * 100.0 / F('total_records'),
        confidence = F('hit_weight')* 100.0,
            profit_percentage=ExpressionWrapper((F('total_dividend') - F('total_records') * 10) * 100.0 / (F('total_records') * 10), output_field=FloatField())
            ).order_by('-percentage')
    # Step 4: Find the top jockey per user
    top_jockeys_per_user = {}
    #print("original:",jockey_scores)
    for jockey_score in jockey_scores:
        username = jockey_score['user__username']
        if username not in top_jockeys_per_user:
            # Add the first (top) jockey for each user
            top_jockeys_per_user[username] = jockey_score
    print(top_jockeys_per_user)
    # Step 5: Pass the dictionary of top jockeys per user to the template
    context = {
        'race_date':recent_race_date,
        'top_jockeys': top_jockeys_per_user,
        'user_scores': user_scores

    }
    return render(request, 'jockey_king.html', context)

def trainer_king(request):
    #if request.session.get('button_clicked')!=True:
        # Change the button's behavior after the first click
     #   return redirect('click_ads')  # Redirect to external URL
    
    #print('test123',request.session.get('button_clicked'))
    # Step 1: Get the most recent race_date
    recent_race_date = UserTips.objects.aggregate(Max('race_date'))['race_date__max']

    # Step 2: Filter UserTips by the most recent race_date
    recent_tips = UserTips.objects.filter(race_date=recent_race_date)

    # Step 3: Group by 'user' and 'trainer', then accumulate (sum) the trainer_scores
    trainer_scores = recent_tips.values('user__username', 'trainer') \
        .annotate(total_trainer_score=Sum('trainer_score')) \
        .order_by('user__username', '-total_trainer_score')  # Order by user first, then score descending
        # Get the user scores and calculate the percentage of hits
    user_scores = UserScores.objects.annotate(
        percentage= F('total_hits') * 100.0 / F('total_records'),
        confidence = F('hit_weight')* 100.0,
            profit_percentage=ExpressionWrapper((F('total_dividend') - F('total_records') * 10) * 100.0 / (F('total_records') * 10), output_field=FloatField())
            ).order_by('-percentage')
    # Step 4: Find the top jockey per user
    top_trainers_per_user = {}
    print("original:",trainer_scores)
    for trainer_score in trainer_scores:
        username = trainer_score['user__username']
        if username not in top_trainers_per_user:
            # Add the first (top) jockey for each user
            top_trainers_per_user[username] = trainer_score

    # Step 5: Pass the dictionary of top jockeys per user to the template
    context = {
        'race_date':recent_race_date,
        'top_trainers': top_trainers_per_user,
        'user_scores': user_scores

    }
    return render(request, 'trainer_king.html', context)
    
def match_chart(request):
     id = request.GET.get('id')
     print("ID1:##",id)
     if id is None:
          id = 1
     total_race = request.session.get("total_race")
     print("ID:##",id)
     context = {
            'race_id' : id,
            'total_race':total_race
        }
     return render(request, 'match_chart.html', context)

@login_required
def racecard_vip(request):
     id = request.GET.get('id')
     if id is None:
          id = 1
     current_datetime = timezone.now()
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/current_race_"+str(id)+".csv")
     #prob_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_neu2_weight"+str(id)+".csv")
     prob_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_ran"+str(id)+".csv")
     odds_path = os.path.join(settings.BASE_DIR, "racecard/data/race_odds_"+str(id)+".csv")
     current_race = pd.read_csv(csv_path)
     current_prob = pd.read_csv(prob_path)
     current_odds = pd.read_csv(odds_path)
     current_race["Prob"] = current_prob['Score']*100
     current_race["Win"] = current_odds["win"]
     current_race["Place"] = current_odds["place"]
     current_race["Expected"] = current_race["Prob"] * current_race["Place"]-(100-current_race["Prob"])

    

     print(current_race)
    
    # Get Current Race Data
     #curr_race_data = current_race[current_race['race_no'] == int(id)]
     curr_race_date=current_race['Racedate'].iloc[0].replace('/','-')
     total_race = current_race['Total'].iloc[0]     
     print(total_race)
    
     curr_tips_by_user = (
       UserTips.objects.filter(race_date=curr_race_date, user__username__in=['RanForest', 'WePower'])  # Current Tips Only
          .values('user', 'user__groups__name')
          .annotate(
          hit_pst=Sum('hit') * 100.0 / Count('hit'),
          total_dividend=Sum('dividend') - Count('hit') * 10,
       )
       .order_by('-hit_pst')  # Sort in descending order of hit ratio
    )  
         # Organize the data by username and fetch all relevant records for each user
     last_perf_by_user = (
        UserTips.objects.filter(race_date=curr_race_date)
        .select_related('user')
        .values('user__username')
        .annotate(
                  hit_pst = Sum('hit')*100.0/Count('hit'),
                  total_dividend = Sum('dividend')-Count('hit')*10,
                  total_weighted_dividend=Sum(F('dividend') * F('ratio')/10)-Sum(F('ratio'))  # New annotation for Sum of dividend * ratio

    ))
     
     curr_perf_by_user = (
        UserTips.objects.filter(race_date=curr_race_date,race_no=id)
        .select_related('user')
        .values('user__username')
        .annotate(
                  hit_pst = Sum('hit')*100.0/Count('hit'),
                  curr_invest = Sum(F('ratio')),
                  curr_return = Sum(F('dividend')* F('ratio')/10),           
                  curr_profit=Sum(F('dividend')* F('ratio')/10)-Sum(F('ratio'))  # New annotation for Sum of dividend * ratio

    ))
     complete_tips_by_user = []
     for user_tips in curr_tips_by_user:
        user_records = UserTips.objects.filter(
            user_id=user_tips['user'],
            race_date=curr_race_date,
            race_no=id
        ).order_by('race_no')
      
        if user_records:
            complete_tips_by_user.append({'user': user_records[0].user, 'groups_name': user_tips['user__groups__name'], 'records': user_records})
     



    # Create or update the records in the UserTips model
     act = request.GET.get('act')
     if act == 'update':
            # Get the top 3 records based on the 'Expected' value
        top_3_records = current_race.nlargest(3, 'Expected')
        # Normalize the 'Expected' values to sum up to 100
        total_expected = top_3_records['Expected'].sum()
        top_3_records['Ratio'] = (top_3_records['Expected'] / total_expected) * 100
        # Round the ratio to the nearest 0 or 5
        top_3_records['Ratio'] = top_3_records['Ratio'].apply(lambda x: round(x / 5) * 5)
        UserTips.objects.filter(
            user=User.objects.get(username='WePower'),
            race_date=curr_race_date,
            race_no=id,
            ).delete()
        print(top_3_records['Ratio'])
        
        rank = 0
        for index, row in top_3_records.iterrows():
            rank = rank + 1

            UserTips.objects.update_or_create(
                user=User.objects.get(username='WePower'),
                race_date=curr_race_date,
                race_no=id,
                horse_no=row['HorseNo'],
                defaults={
                    'rank': rank,
                    'jockey_score': 12 if rank == 1 else 6 if rank == 2 else 4,
                    'trainer_score': 12 if rank == 1 else 6 if rank == 2 else 4,
                    'horse_name': row['HorseName'],
                    'horse_name_cn': row['HorseName_cn'],
                    'jockey': row['Jockey'],
                    'trainer': row['Trainer'],
                    'hit': 0,
                    'ratio': row['Ratio'],
                    
                }
            )
    
     #print(complete_tips_by_user)
     context = {
            'current_race': current_race,
            'total_race': total_race,
            'current_datetime':current_datetime,
            'race_id' : id,
            'complete_tips_by_user': complete_tips_by_user,
            'last_perf_by_user' : last_perf_by_user,
            'curr_perf_by_user': curr_perf_by_user,
        }

     return render(request, 'currentrace_vip.html', context)
    



## Article Section ###

def is_specific_user(user):
    # Check if the user is the specific user you want to allow access
    return user.username == 'louisngai'

@login_required
@user_passes_test(is_specific_user)
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

@login_required
@user_passes_test(is_specific_user)
def data_update_console(request):
    id = request.GET.get('id')
    if id is None:
          id = 1
    context = { 
                'race_id' : id,
    }
    return render(request, 'data_update_console.html', context)

def update_race_result(request):
    id = request.GET.get('id')
    if id is None:
        id = 1
    output = get_results(id)  # Call the function get_results
    messages.success(request, 'Update Success!')
    return redirect('../data_update_console')  # replace with the actual URL
    
def privacy(request):
    return render(request, 'privacy.html')

def disclaimer(request):
    return render(request, 'disclaimer.html')

def responsible(request):
    return render(request, 'responsible.html')

def help(request):
    return render(request, 'help.html')

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

def like_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    if 'liked_articles' not in request.session:
        request.session['liked_articles'] = []

    liked_articles = set(request.session['liked_articles'])

    if article_id not in liked_articles:
        article.likes += 1
        article.save()
        liked_articles.add(article_id)
        request.session['liked_articles'] = list(liked_articles)

    return JsonResponse({'likes': article.likes})


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

def lottory_predict(request):
    listNo='No1'
    id = request.GET.get('id')
    listNo = 'No'+id
    current_datetime = timezone.now()
    largest_draw = Marksix_hist.objects.aggregate(largest_draw=models.Max('Draw'))['largest_draw']
    form = NumberForm() 
    # Now 'largest_draw' contains the largest value from the 'Draw' column
    # (e.g., '24/071')

    # Next, remove the '/' character and convert it to an integer
    draw_without_slash = largest_draw.replace('/', '')
    seed_no = int(draw_without_slash)+1
    draw_string = str(seed_no)
    print("SeedNo:", seed_no)
    # Insert the '/' character at the appropriate position
    next_draw = f"{draw_string[:2]}/{draw_string[2:]}"

     # Retrieve the data from the Marksix_hist model, sorted by Date in descending order
    data = Marksix_hist.objects.order_by('-Date').values_list(listNo, flat=True)

    # Convert the queryset to a list
    data_list = list(data)
    data_list.reverse()
    print(data_list)
    # Prepare the features (X) and target (y) for KNN
    X = [[x] for x in data_list[:-1]]  # Features: all numbers except the last one
    y = data_list[1:]  # Target: the next number for each feature

    # Create and fit the KNN model
    knn_model = KNeighborsRegressor(n_neighbors=3)
    knn_model.fit(X, y)

    # Predict the next number
    next_number = math.ceil(knn_model.predict([[data_list[-1]]])[0])
    print("Next_number:",next_number)

    # Prepare data for the chart
    labels = list(range(1, 21))  # Numbers 1 to 20 for the recent numbers
    labels = list(range(int(draw_string[2:]) - 10, int(draw_string[2:])))
    labels.append('下期預測')  # Label for the next number
    predicted_numbers = knn_model.predict([[x] for x in range(1, 22)])
    print("predicted Number",predicted_numbers)
    records = Marksix_user_rec.objects.filter(Draw=next_draw)
    # Pass the results to the template
    context = {
        'records':records,
        'next_draw': next_draw,
        'current_datetime': current_datetime,
        'recent_numbers': data_list[-10:],
        'next_number': next_number,
        'labels': json.dumps(labels),
        'predicted_numbers': json.dumps(predicted_numbers.tolist()),
        'form':form,
    }

    return render(request, 'lottory.html', context)

def ichi_lotto(request):
    current_datetime = timezone.now()
    # Assuming you have a model field named 'Draw'
    largest_draw = Marksix_hist.objects.aggregate(largest_draw=models.Max('Draw'))['largest_draw']

    # Now 'largest_draw' contains the largest value from the 'Draw' column
    # (e.g., '24/071')

    # Next, remove the '/' character and convert it to an integer
    draw_without_slash = largest_draw.replace('/', '')
    seed_no = int(draw_without_slash)+1
    draw_string = str(seed_no)
    print("SeedNo:", seed_no)
    # Insert the '/' character at the appropriate position
    next_draw = f"{draw_string[:2]}/{draw_string[2:]}"
    print("NextDraw:", next_draw)
    request.session['next_draw']= next_draw
    form = NumberForm()  # Initialize the form here
    user_input = 0
    if request.method == 'POST':
        user_input = request.POST.get('number')  # Get the value from the form

    seed_no=seed_no+int(user_input)
    print("Final_seedNo", seed_no)
    random.seed(seed_no)
    random_numbers_list = [random.randint(1, 64) for _ in range(49)]
   
    # Initialize an empty dictionary to store the indices
    ichi = {}

     # Iterate through the random numbers and populate the dictionary
    for index, number in enumerate(random_numbers_list):
        ichi_counter = 0
        if number in [1,2,34,11,13,7,50,27,9,14,58,45]:
            if number not in ichi:
                ichi[number] = [index+1]
            else:
                ichi[number].append(index+1)
        ichi_counter = ichi_counter+1        
                # Retrieve all records with Draw='24/071'
    records = Marksix_user_rec.objects.filter(Draw=next_draw)
    return render(request, 'ichi_lotto.html', {'ichi': ichi, 'form':form,'records':records,'current_datetime':current_datetime,'next_draw':next_draw})

def update_lotto_tips(request):
    if request.method == 'POST':
        form = NumberForm(request.POST)
        if form.is_valid():
            draw_no = request.POST.get('DrawNo')
            # Sort the numbers in ascending order
            sorted_numbers = sorted([
                form.cleaned_data['No1'],
                form.cleaned_data['No2'],
                form.cleaned_data['No3'],
                form.cleaned_data['No4'],
                form.cleaned_data['No5'],
                form.cleaned_data['No6'],
                form.cleaned_data['No7'],
            ])
            # Update or create the instance
            user_rec, created = Marksix_user_rec.objects.update_or_create(
                user=request.user,
                seq=1,  # Set the appropriate sequence value
                Draw=draw_no,  # Set the appropriate draw value
                defaults={
                    'Date': date.today(),
                    'No1': sorted_numbers[0],
                    'No2': sorted_numbers[1],
                    'No3': sorted_numbers[2],
                    'No4': sorted_numbers[3],
                    'No5': sorted_numbers[4],
                    'No6': sorted_numbers[5],
                    'No7': sorted_numbers[6],
                }
            )
            # Save the instance to the database
            user_rec.save()
    return redirect('../ichi_lotto/')

def lotto_next_stat(request):
    listNo='No1'
    id = request.GET.get('id')
    if id:
        listNo = 'No'+id
    else:
        id=1
    current_datetime = timezone.now()
    largest_draw = Marksix_hist.objects.aggregate(largest_draw=models.Max('Draw'))['largest_draw']
    form = NumberForm() 
    # Now 'largest_draw' contains the largest value from the 'Draw' column
    # (e.g., '24/071')

    # Next, remove the '/' character and convert it to an integer
    draw_without_slash = largest_draw.replace('/', '')
    seed_no = int(draw_without_slash)+1
    draw_string = str(seed_no)

    # Insert the '/' character at the appropriate position
    next_draw = f"{draw_string[:2]}/{draw_string[2:]}"

     # Retrieve the data from the Marksix_hist model, sorted by Date in descending order
    data = Marksix_hist.objects.order_by('-Date').values_list(listNo, flat=True)

    # Convert the queryset to a list
    data_list = list(data)
    data_list.reverse()
    print(data_list)
    # Prepare the features (X) and target (y) for KNN

    past_pattern=data_list[-3:]
    #past_pattern = [17,21,8]
    print("Past_pattern:", past_pattern)


    occurrences, next_numbers = find_occurrences_and_next_numbers(data_list, past_pattern,id)

    print("Next_number",next_numbers)
    # Prepare data for the chart

    number_counts = {}  # Dictionary to store the frequency of each number

    # Count the occurrences of each number
    for num in next_numbers:
        number_counts[num] = number_counts.get(num, 0) + 1

    # Create a list of (number, frequency) tuples
    number_pairs = [(num, count) for num, count in number_counts.items()]

    records = Marksix_user_rec.objects.filter(Draw=next_draw)
    # Pass the results to the template
    context = {
        'past_pattern':past_pattern,
        'next_draw': next_draw,
        'current_datetime': current_datetime,
        'number_pairs':number_pairs,
    }

    return render(request, 'lotto_next_stat.html', context)

def find_occurrences_and_next_numbers(history, target_sequence,id):
    occurrences = []
    next_numbers = []
    id=int(id)
    print("In Function:",target_sequence)
    if id <= 2:
        shift_pattern = [-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12]
    elif id == 5 or id == 6:
        shift_pattern = [-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3]
    elif id == 7:
        shift_pattern = [-20,-19,-18,-17,-16,-15,-14,-13,-12,11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    else:
        shift_pattern = [-7,-6,-5,-4,-3,-2,-1,0,1,2,3,4,5,6,7,8]
    for shift in shift_pattern:
        target=[num + shift for num in target_sequence]
        print("In Function1:",target)

        for i in range(len(history) - len(target) + 1):
            if history[i:i + len(target)] == target: #Find the seq mactch
                occurrences.append(i)
                print("i:",i)
                if i < (len(history)-len(target)):
                    if history[i+len(target)]-shift>0 and history[i+len(target)]-shift<49:
                        next_numbers.append(history[i + len(target)]-shift)
    return occurrences, next_numbers   

def lotto_must_win(request, id):

    largest_draw = Marksix_hist.objects.aggregate(largest_draw=models.Max('Draw'))['largest_draw']

    # Next, remove the '/' character and convert it to an integer
    draw_without_slash = largest_draw.replace('/', '')
    seed_no = int(draw_without_slash)+1
    random.seed(seed_no)
    file_path = os.path.join(settings.BASE_DIR, "racecard/data/lotto_must_win117.csv")
    data = pd.read_csv(file_path)

    # Random Number for Ichi
    # Generate random integers between 1 and 64
    num_rows = len(data)
    random_numbers_list = [random.randint(1, 64) for _ in range(num_rows)]
     # Add the 'Rand' column to the DataFrame
    data['Ichi'] = random_numbers_list

    # Calculate the start and end indices based on the page ID
    page_size = 30
    start_index = (id - 1) * page_size
    end_index = start_index + page_size

    if start_index >= len(data):
        raise Http404("Page does not exist")

    page_data = data.iloc[start_index:end_index]

    context = {
        'page_data': page_data.to_dict(orient='records'),
        'page_id': id,
        'prev_page': id - 1 if id > 1 else None,
        'next_page': id + 1 if end_index < len(data) else None,
    }

    return render(request, 'lotto_must_win.html', context)

def lotto_test(request):
     user_language = 'tw'  # or
     translation.activate(user_language)

     request.session[settings.LANGUAGE_COOKIE_NAME] = user_language
     results = None
     total_records = 0
     if request.method == 'POST':
        form = LottoForm(request.POST)
        if form.is_valid():
            option_value = int(form.cleaned_data['option'])
            numbers = [
                form.cleaned_data['number1'],
                form.cleaned_data['number2'],
                form.cleaned_data['number3'],
                form.cleaned_data['number4'],
                form.cleaned_data['number5'],
                form.cleaned_data['number6'],
                form.cleaned_data['number7'],
            ]
            # Fetch records based on the option_value
            records = Marksix_hist.objects.all().order_by('-Date')[:option_value]
            
            results = []
            for record in records:
                match_count = len(set(numbers[:7]) & {record.No1, record.No2, record.No3, record.No4, record.No5, record.No6})
                if match_count >= 3:
                    score = match_count
                    if record.No7 in numbers:
                        score += 0.5
                    results.append({
                        'Draw': record.Draw,
                        'Date': record.Date,
                        'No1': record.No1,
                        'No2': record.No2,
                        'No3': record.No3,
                        'No4': record.No4,
                        'No5': record.No5,
                        'No6': record.No6,
                        'No7': record.No7,
                        'score': score,
                    })
            total_records = len(results)
     else:
        form = LottoForm()
    
    
  
    
     return render(request, 'lotto_test.html', {'form': form, 'results': results, 'total_records': total_records})

def lotto_trio(request):
     user_language = 'tw'  # or
     translation.activate(user_language)

     request.session[settings.LANGUAGE_COOKIE_NAME] = user_language

     record = None
     hist_records = None
     record1 = None 
     record2 = None 
     record1_freq = None
     record2_freq = None
     record1_cold = None
     record2_cold = None
     
    
     diff = 0
     largest_draw = Marksix_hist.objects.aggregate(models.Max('Draw'))['Draw__max']
     print("largest Draw:",largest_draw)
     draw_without_slash = largest_draw.replace('/', '')
     seed_no = int(draw_without_slash)+1
     draw_string = str(seed_no)

     # Insert the '/' character at the appropriate position
     next_draw = f"{draw_string[:2]}/{draw_string[2:]}"

     if request.method == 'POST':
        form = LottoTrioForm(request.POST)
        if form.is_valid():
            number_list = [
                form.cleaned_data['number1'],
                form.cleaned_data['number2'],
                form.cleaned_data['number3'],
            ]
            # Fetch records based on the option_value
            print("numbers:",number_list)
            condition = (
                Q(No1=number_list[0]) | Q(No2=number_list[0]) | Q(No3=number_list[0]) | Q(No4=number_list[0]) | Q(No5=number_list[0]) | Q(No6=number_list[0]) | Q(No7=number_list[0])
            ) & (
                Q(No1=number_list[1]) | Q(No2=number_list[1]) | Q(No3=number_list[1]) | Q(No4=number_list[1]) | Q(No5=number_list[1]) | Q(No6=number_list[1]) | Q(No7=number_list[1])
            ) & (
                Q(No1=number_list[2]) | Q(No2=number_list[2]) | Q(No3=number_list[2]) | Q(No4=number_list[2]) | Q(No5=number_list[2]) | Q(No6=number_list[2]) | Q(No7=number_list[2])
            )

            record = Marksix_hist.objects.filter(condition).distinct().last()
            freq = Marksix_hist.objects.filter(condition).count()
            print("Freq:",freq)
            if record:
                diff = calculate_days_difference(record.Date)

                lotto_trio_search, created = LottoTrioSearch.objects.update_or_create(
                            Draw=largest_draw,
                            No1=number_list[0],
                            No2=number_list[1],
                            No3=number_list[2],
                            Freq = freq,
                            defaults={
                                'Search_date': datetime.now().date(),
                                'Diff_days': diff
                            }
                        )
            hist_records = LottoTrioSearch.objects.filter(Draw=largest_draw).order_by('-Diff_days')

            # Loop through the records to find the first two distinct ones 
            for i, hist_record in enumerate(hist_records): 
                if record1 is None: 
                    record1 = hist_record 
                elif record2 is None: 
                    if set([record1.No1, record1.No2, record1.No3]).isdisjoint([hist_record.No1, hist_record.No2, hist_record.No3]): 
                        record2 =hist_record
                        break
            hist_records_freq = LottoTrioSearch.objects.filter(Draw=largest_draw).order_by('-Freq')
            # Loop through the records to find the first two distinct ones 
            for i, hist_record_freq in enumerate(hist_records_freq): 
                if record1_freq is None: 
                    record1_freq = hist_record_freq 
                elif record2_freq is None: 
                    if set([record1_freq.No1, record1_freq.No2, record1_freq.No3]).isdisjoint([hist_record_freq.No1, hist_record_freq.No2, hist_record_freq.No3]): 
                        record2_freq =hist_record_freq
                        break
            
            hist_records_cold = LottoTrioSearch.objects.filter(Draw=largest_draw).order_by('Freq')
            # Loop through the records to find the first two distinct ones 
            for i, hist_record_cold in enumerate(hist_records_cold): 
                if record1_cold is None: 
                    record1_cold = hist_record_cold 
                elif record2_cold is None: 
                    if set([record1_cold.No1, record1_cold.No2, record1_cold.No3]).isdisjoint([hist_record_cold.No1, hist_record_cold.No2, hist_record_cold.No3]): 
                        record2_cold =hist_record_cold
                        break
     
     else:
        form = LottoTrioForm()
        hist_records = LottoTrioSearch.objects.filter(Draw=largest_draw).order_by('-Diff_days')
     # Loop through the records to find the first two distinct ones 
        for i, hist_record in enumerate(hist_records): 
                if record1 is None: 
                    record1 = hist_record 
                elif record2 is None: 
                    if set([record1.No1, record1.No2, record1.No3]).isdisjoint([hist_record.No1, hist_record.No2, hist_record.No3]): 
                        record2 =hist_record
                        break
        hist_records_freq = LottoTrioSearch.objects.filter(Draw=largest_draw).order_by('-Freq')
            # Loop through the records to find the first two distinct ones 
        for i, hist_record_freq in enumerate(hist_records_freq): 
            if record1_freq is None: 
                record1_freq = hist_record_freq 
            elif record2_freq is None: 
                if set([record1_freq.No1, record1_freq.No2, record1_freq.No3]).isdisjoint([hist_record_freq.No1, hist_record_freq.No2, hist_record_freq.No3]): 
                    record2_freq =hist_record_freq
                    break
        hist_records_cold = LottoTrioSearch.objects.filter(Draw=largest_draw).order_by('Freq')
        # Loop through the records to find the first two distinct ones 
        for i, hist_record_cold in enumerate(hist_records_cold): 
            if record1_cold is None: 
                record1_cold = hist_record_cold 
            elif record2_cold is None: 
                if set([record1_cold.No1, record1_cold.No2, record1_cold.No3]).isdisjoint([hist_record_cold.No1, hist_record_cold.No2, hist_record_cold.No3]): 
                    record2_cold =hist_record_cold
                    break
     return render(request, 'lotto_trio.html', {'form': form, 'next_draw':next_draw,'diff':diff, 'result':record, 'hist':hist_records, 'record1':record1, 'record2':record2, 'record1_freq':record1_freq, 'record2_freq':record2_freq, 'record1_cold':record1_cold, 'record2_cold':record2_cold})

def lotto_longterm(request):     
     form = NumberForm() 
     return render(request, 'lotto_longterm.html',{'form':form})

def calculate_days_difference(record_date):
    # Convert record_date to a datetime object if it's not already
    if isinstance(record_date, str):
        record_date = datetime.strptime(record_date, '%Y-%m-%d').date()

    # Get the current date
    current_date = datetime.now().date()

    # Calculate the difference in days
    days_difference = (current_date - record_date).days

    return days_difference

