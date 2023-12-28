from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import pandas as pd

# Create your views here.
def races(request):
     current_race = pd.read_csv("horsegame/data/current_race.csv")
     template = loader.get_template("currentrace.html")
     return HttpResponse(template.render({"current_race":current_race},request))
