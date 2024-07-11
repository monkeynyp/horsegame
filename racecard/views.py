from django.shortcuts import render,redirect
import pandas as pd
import os,json,math,random
import requests
from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import FootballMatch, FootballTeam, UserTips,UserScores,Article,UserTips_my,Marksix_hist,Marksix_user_rec
from django.db.models import Max, F, Count, Sum, ExpressionWrapper, FloatField, IntegerField
from django.utils import timezone
from .forms import CustomUserCreationForm,NumberForm
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
     
     curr_race_date=current_race['Racedate'].iloc[0].replace('/','-')
     dt_obj = datetime.strptime(curr_race_date, "%Y-%m-%d")
     timestamp = int(dt_obj.timestamp())+int(id)
     random.seed(timestamp)
     # Generate random integers between 1 and 64
     num_rows = len(current_race)

     random_numbers_list = [random.randint(1, 64) for _ in range(num_rows)]
     # Add the 'Rand' column to the DataFrame
     current_race['Ichi'] = random_numbers_list

     total_race = current_race['Total'].iloc[0]
     
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
         print("## Sort_query ##", sort_query)

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
            'total_race': total_race,
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


def racecard_my(request):
     id = request.GET.get('id')
     if id is None:
          id = 1
     current_datetime = timezone.now()
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/my_curr_race.csv")
     current_race = pd.read_csv(csv_path)
    
    # Get Current Race Data
     curr_race_data = current_race[current_race['race_no'] == int(id)]
     current_race['race_date'] = current_race['race_date'].astype(str)
 
     first_row = current_race.iloc[0]
     race_date = first_row["race_date"]
     curr_race_date = datetime.datetime.strptime(race_date, "%Y%m%d").strftime("%Y-%m-%d")
     #total_race = current_race['Total'].iloc[0]
     
    #  horse_tips_qty = (
    #     UserTips.objects
    #     .filter(race_date=curr_race_date, race_no=id)
    #     .values('horse_name', 'user__groups__name')
    #     .annotate(num_tips=Count('id'))
    # )
     
    #  tips_qty_by_type = (
    #     UserTips.objects
    #     .filter(race_date=curr_race_date, race_no=id)
    #     .values('user__groups__name')
    #     .annotate(num_users=Count('user', distinct=True))
    # )
    #  print("Horse Tips Qtr: ", tips_qty_by_type)

    ## For Tips Sorting based on Overall Performance ##
    #  last_tips_by_user = (
    #     UserScores.objects.all()  
    #         .values('user', 'user__groups__name')
    #         .annotate(
    #             hit_ratio=ExpressionWrapper(F('total_hits')*100/F('total_records'), output_field=FloatField())
    #     )
    #     .order_by('-hit_ratio')  # Sort in descending order of hit ratio
    # )

    # ## For Tips Sorting based on Current Peformance. If the Current Performance is zero, Last Performace will be used for sorting ##
     
     curr_tips_by_user = (
         UserTips_my.objects.filter(race_date=curr_race_date)  # Current Tips Only
            .values('user', 'user__groups__name')
            .annotate(
             hit_pst=Sum('hit') * 100.0 / Count('hit'),
             total_dividend=Sum('dividend') - Count('hit') * 10,
         )
         .order_by('-hit_pst')  # Sort in descending order of hit ratio
     )   
  
    # Calculate the total sum of 'Hit' in 'curr_tips_by_user' with handling for None values
    # sum_pst = 0
    #  for tip in curr_tips_by_user:
    #       sum_pst = sum_pst+tip['hit_pst']
    
    #  if sum_pst == 0.0:
    #       sort_query = last_tips_by_user
    #   else:      
     sort_query = curr_tips_by_user


    #  request.session['curr_tips_by_user'] = list(curr_tips_by_user)
    #  request.session['curr_race_date'] = curr_race_date
    #  request.session['total_race']= int(total_race)


    # # Organize the data by username and fetch all relevant records for each user
    #  last_perf_by_user = (
    #     UserTips.objects.filter(race_date=curr_race_date)
    #     .select_related('user')
    #     .values('user__username')
    #     .annotate(
    #               hit_pst = Sum('hit')*100.0/Count('hit'),
    #               total_dividend = Sum('dividend')-Count('hit')*10
    # ))
    #  request.session['last_perf_by_user'] = list(last_perf_by_user)
    # # Get the user scores and calculate the percentage of hits
    #  user_scores = UserScores.objects.annotate(
    #     percentage= F('total_hits') * 100.0 / F('total_records'),
    #     confidence = F('hit_weight')* 100.0,
    #         profit_percentage=ExpressionWrapper((F('total_dividend') - F('total_records') * 10) * 100.0 / (F('total_records') * 10), output_field=FloatField())
    #         ).order_by('-percentage')
    
    #  #request.session['user_scores'] = list(user_scores)

     complete_tips_by_user = []
     for user_tips in sort_query:
         print("user_tips",user_tips)
         user_records = UserTips_my.objects.filter(
             user_id=user_tips['user'],
             race_date=curr_race_date,
             race_no=id
         ).order_by('race_no')
         print("user_records:", user_records)
      
         if user_records:
             complete_tips_by_user.append({'user': user_records[0].user, 'groups_name': user_tips['user__groups__name'], 'records': user_records})

    #     selected_language = translation.get_language()  # Default to Chinese if language is not provided
    #     recent_articles = Article.objects.filter(language=selected_language).order_by('-pub_date')[:5]
     print("Complete Tips",complete_tips_by_user)
    
     context = {
            'current_race': curr_race_data,
            'complete_tips_by_user': complete_tips_by_user
        }
       
     return render(request, 'currentrace_my.html', context)
    

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


def facebook_feed(request):
    access_token = 'EAAP8Mp3FsJsBO0i0h3KM36my69KFmblxKJsSOtnrKX15qF2GMp4En3S8TNCOuC8PhroobVRo2gkD99w8JmNEArXidvvNmFuF23rBPnH2zFUOtYiZAAVYptnI25D4Ll97WNFIeYIugDtAVI7TwOMQhzko91VY4qf83m7HnKlgciSC0g0GZANpE34b30MfkCYR2Wh1DhpTHZA0RZBZBhTIm2huSeezMPHXDM5IoxDhrLfallYI4ploISZB90r1KF7AZDZD'
    api_url = f'https://graph.facebook.com/v12.0/250396646015/feed?access_token={access_token}'

    response = requests.get(api_url)
    data = response.json()
    print ("Facebook Data",data)

    feed_data = data.get('data', [])

    return render(request, 'facebookfeed.html', {'feed_data': feed_data})

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
    data = Marksix_hist.objects.order_by('-Date').values_list(listNo, flat=True)[:500]

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
    labels.append('下期預測')  # Label for the next number
    predicted_numbers = knn_model.predict([[x] for x in range(1, 22)])
    print("predicted Number",predicted_numbers)
    records = Marksix_user_rec.objects.filter(Draw=next_draw)
    # Pass the results to the template
    context = {
        'records':records,
        'next_draw': next_draw,
        'current_datetime': current_datetime,
        'recent_numbers': data_list[-20:],
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


  
def football_match(request):
    id = request.GET.get('id')
    if  id is None:
        today_matches = FootballMatch.objects.filter(match_date__date__gte=date.today())
    else:
    # Get football matches for today
        today_matches = FootballMatch.objects.filter(id=id)
    
    if not today_matches:
        id = 1
        # Handle the case when no matches are found
        today_matches = FootballMatch.objects.filter(id=1)
    
    for match in today_matches:
        # Fetch team information based on team names
        team_a_info = FootballTeam.objects.get(team_name=match.team_a)
        print("Team_A:",team_a_info)
        team_b_info = FootballTeam.objects.get(team_name=match.team_b)
        print("Team_B:",team_b_info)

        # Combine match and team data
        combined_data = {
            'match': match,
            'team_a_info': team_a_info,
            'team_b_info': team_b_info,
        }
    
    # Render the template with the combined data
    return render(request, 'footballmatch.html', {'combined_data': combined_data, 'id':id})