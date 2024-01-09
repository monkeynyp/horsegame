from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import pandas as pd
import os
from django.conf import settings
from django.utils.translation import gettext as _

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
     template = loader.get_template("currentrace.html")
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

def contact(request):
     text = _("Louis is very good!")
     return render(request, 'contact.html', {'text': text})