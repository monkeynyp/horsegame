import pandas as pd
from django.core.management.base import BaseCommand

#from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np

from racecard.models import Race_hist

class Command(BaseCommand):
    help = 'Get the Horse Racing Historydata from the database'
    def get_race_hist_data(self):
        race_result = Race_hist.objects.all().order_by('date', 'index', 'place')
        return race_result

    def handle(self, *args, **options):
       race_result = self.get_race_hist_data()
       data = []
       for race in race_result:
            data.append([
            race.date,
            race.index,
            race.place,
            race.band_no,
            race.jockey,
            race.trainer,
            race.act_wt,
            race.draw,
            race.win_odds,
            race.declar_horse_wt,
            race.gear,
            race.track,
            race.race_class,
            race.distance,
            race.good,
            race.rating,
          
            ])
        
       columns = [
         'date', 'index', 'place', 'band_no', 'jockey', 'trainer', 'act_wt', 'draw', 'win_odds', 'declar_horse_wt',
         'gear', 'track', 'race_class', 'distance', 'good', 'rating'
        ]
       race_hist = pd.DataFrame(data, columns=columns)
       print(race_hist.head())

       preprocessor = ColumnTransformer(
            transformers=[
                ('categorical', OneHotEncoder(handle_unknown='ignore', sparse_output=True), categoryList)
            ],
            remainder='passthrough'  # Include non-categorical features as is
        )

        
