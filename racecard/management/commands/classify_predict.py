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
        categoryList = ['band_no','jockey', 'trainer', 'gear', 'track', 'race_class', 'good']
        test_case=['band_no', 'jockey', 'trainer', 'gear','track', 'race_class','good','act_wt','draw','declar_horse_wt','distance','rating']
        race_hist = pd.DataFrame(data, columns=columns)
        print(race_hist.head()) 
        horse_jockey_avg_result = race_hist
        preprocessor = ColumnTransformer(
            transformers=[
                ('categorical', OneHotEncoder(handle_unknown='ignore', sparse_output=True), categoryList)
            ],
            remainder='passthrough'  # Include non-categorical features as is
        )
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            #('Classifier', LogisticRegression(C=5,max_iter=3000,solver='lbfgs'))
            #('Classifier', CategoricalNB()),
            #('regressor', MLPRegressor(hidden_layer_sizes=(150,), max_iter=500, alpha=0.0001,solver='adam',tol=0.0001,verbose=10, random_state=1))
            ('Classifier',RandomForestClassifier(n_estimators=1299, random_state=42))
            #('classifier', SVC(kernel='rbf', C=7, gamma='auto', probability=True)
            
            #('classifier', MLPClassifier(hidden_layer_sizes=(150,), max_iter=500, alpha=0.000005,
                        #solver='adam', verbose=10, random_state=1, tol=0.0001)),
        ])

        # Train a Random Forest classifier
        X = horse_jockey_avg_result[test_case]
        y = horse_jockey_avg_result['Result']
        pipeline.fit(X, y)
        no_of_race = input("Input Total Number of Race: ")
        try:
            for pred_i in range(1,int(no_of_race)+1):
                print(pred_i)

                race_predict_df = pd.DataFrame([],columns=['HorseName','HorseName_cn','Jockey','Trainer','Score'])
                race_data = pd.read_csv('current_race_'+str(pred_i)+'.csv')
                race_data['band_no']= race_data['HorseName']
                race_data['jockey'] = race_data['Jockey']
                race_data['trainer'] = race_data['Trainer']
                race_data['act_wt']= race_data['ActWeight']
                race_data['WeightRatio'] = (race_data['ActWeight'] / race_data['HorseW`eight']).astype(float)
                race_data['race_class'] = race_data['Class']

                # Make predictions on the new data
                new_predictions = pipeline.predict(race_data)

                # Print the predictions
                print(new_predictions)

                probabilities = pipeline.predict_proba(race_data)
            
                race_data['prob'] = probabilities[:, 1]
                # Print the probability of each horse belonging to class 1
                for i, horse_name in enumerate(race_data['HorseName']):
                    jockey = race_data['Jockey'][i]
                    trainer = race_data['Trainer'][i]
                    horse_name_cn = race_data['HorseName_cn'][i]
                    probability_class_1 = probabilities[i, 1]  # Assuming class 1 is the second column
                    race_predict_data = [horse_name,horse_name_cn,jockey,trainer,probability_class_1]
                    print(race_predict_data)
                    race_predict_df.loc[len(race_predict_df)] = race_predict_data

                    print(f'Probability of {horse_name} : {probability_class_1}')
                
                print("My Prediction")
                print(race_predict_df)
                
                race_predict_df.to_csv('../horsegame/racecard/data/predict_db_ran'+str(pred_i)+'.csv')
        except Exception as e:
                print(e)
  
