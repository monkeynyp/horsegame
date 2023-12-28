from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import pandas as pd
import os
from django.conf import settings

# Create your views here.
def races(request):
     csv_path = os.path.join(settings.BASE_DIR, "racecard/data/current_race.csv")
     current_race = pd.read_csv(csv_path)
     template = loader.get_template("currentrace.html")
     return HttpResponse(template.render({"current_race":current_race},request))
