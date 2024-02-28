from django.core.management.base import BaseCommand
from racecard.models import UserTips,User  # Replace 'YourModel' with the actual model name
from datetime import datetime
import pandas as pd
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Update data from CSV files to SQLite database'

# Specify the relative path to the CSV file

    def add_arguments(self, parser):
        # Add command line arguments
        parser.add_argument('num_races', type=int, help='Number of races')
        parser.add_argument('race_date', type=str, help='Race date in YYYY-MM-DD format')

    def handle(self, *args, **options):
        # Access command line arguments
        num_races = options['num_races']
        race_date = datetime.strptime(options['race_date'], '%Y-%m-%d').date()

        #alg_methods = ['LogRegress','NaiveBayes','SVC','RanForest','NeuroNet','ForestReg','NeuroReg','GradientB']
        alg_methods = ['ForestReg','NeuroReg','GradientB']
        class_flag=0
        for alg in alg_methods:
            user_id = User.objects.get(username=alg)
            for counter in range(1,num_races+1):
                if alg =="LogRegress":
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_log"+str(counter)+".csv")
                elif alg == 'NaiveBayes':
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_nav"+str(counter)+".csv")
                elif alg == 'SVC':
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_svc"+str(counter)+".csv")
                elif alg == 'RanForest':
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_ran"+str(counter)+".csv")
                elif alg == 'NeuroNet':
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_neu"+str(counter)+".csv")
                elif alg == 'ForestReg':
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_ran2"+str(counter)+".csv")
                elif alg == 'NeuroReg':
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_neu2"+str(counter)+".csv")
                elif alg == 'GradientB':
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_gra"+str(counter)+".csv")
                
                df = pd.read_csv(csv_path)
                if class_flag == 1:
                    df.sort_values(by='Score',ascending=False, inplace=True)
                print(df)
                
                result_df = df.head(3)

                for i,row in result_df.iterrows():
                    # Your logic to update the database with race_date and race_no
                    UserTips.objects.update_or_create(
                        user = user_id,
                        race_date = race_date,
                        race_no = counter,
                        horse_no = row[ 'Unnamed: 0']+1,
                        horse_name = row['HorseName'],
                        hit = 0
                        )
                print(result_df)
        self.stdout.write(self.style.SUCCESS('Data updated successfully.'))