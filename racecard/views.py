from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import pandas as pd
import os
from django.conf import settings

# Create your views here.
def racecard(request):
     id = request.GET.get('id')
     if id is None:
          id = 1
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/current_race_"+str(id)+".csv")
     current_race = pd.read_csv(csv_path)
     template = loader.get_template("currentrace.html")
     return HttpResponse(template.render({"current_race":current_race},request))

def about(request):
     template = loader.get_template("about.html")
     return HttpResponse(template.render())

def contact(request):
     template = loader.get_template("contact.html")
     return HttpResponse(template.render())