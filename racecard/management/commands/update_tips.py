from django.core.management.base import BaseCommand
from racecard.models import UserTips,User, UserScores # Replace 'YourModel' with the actual model name
from datetime import datetime
import pandas as pd
import os,math
from django.conf import settings
from django.db.models import Sum, F

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
        
        #alg_methods = ['LogRegress','NaiveBayes','SVC','RanForest','NeuroNet','ForestReg','NeuroReg','GradientB','TimeMonkey']
        #alg_methods = ['LogRegress','RanForest','ForestReg','NeuroReg']
        alg_methods = ['LogRegress','NeuroReg','NeuroNet']
        #alg_methods = ['LogRegress','RanForest']
        #alg_methods = ['RanForest']
        jockey_score = 0
        trainer_score = 0
        class_flag=0
        for alg in alg_methods:
            user_id = User.objects.get(username=alg)
            for counter in range(1,num_races+1):
                if alg =="LogRegress":
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_neu5"+str(counter)+".csv")
                elif alg == 'NaiveBayes':
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_neu5"+str(counter)+".csv")
                elif alg == 'SVC':
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_svc"+str(counter)+".csv")
                elif alg == 'RanForest':
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_ran"+str(counter)+".csv")
                elif alg == 'NeuroNet':
                    class_flag=1
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_neu3"+str(counter)+".csv")
                elif alg == 'ForestReg':
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_ran2"+str(counter)+".csv")
                elif alg == 'NeuroReg':
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_neu2"+str(counter)+".csv")

                elif alg == 'GradientB':
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_gra"+str(counter)+".csv")
                elif alg == 'TimeMonkey':
                    csv_path = os.path.join(settings.BASE_DIR, "racecard/data/predict_race_tim"+str(counter)+".csv")
                
                df = pd.read_csv(csv_path)
                if class_flag == 1:
                    df.sort_values(by='Score',ascending=False, inplace=True)
                print(df)
                
                result_df = df.head(3)
                print("Top3: ",result_df)
                existing_records = UserTips.objects.filter(user=user_id, race_date=race_date, race_no=counter)
                if existing_records.exists():
                    existing_records.delete()
                rank = 0
                j = 0
                for i,row in result_df.iterrows():
                
                    print(f"Processing row {j}: {row}")
                    if j == 0:
                        jockey_score = 12
                        trainer_score = 12
                        win_flag = True
                    elif j == 1:
                        jockey_score = 6
                        trainer_score = 6
                        win_flag = False
                    elif j == 2:
                        jockey_score = 4
                        trainer_score = 4
                        win_flag = False
                    else:
                        jockey_score = 0
                        trainer_score = 0
                        win_flag = False
                    j += 1
                    # Your logic to update the database with race_date and race_no
                    UserTips.objects.update_or_create(
                        user = user_id,
                        race_date = race_date,
                        race_no = counter,
                        horse_no = row[ 'Unnamed: 0']+1,
                        rank = j,
                        jockey_score = jockey_score,
                        trainer_score = trainer_score,
                        horse_name = row['HorseName'],
                        horse_name_cn = row['HorseName_cn'],
                        jockey = row['Jockey'],
                        trainer = row['Trainer'],
                        hit = 0,
                        win_flag = win_flag,
                        ratio=round(row['Score'] * 100 / 10) * 10  # Multiply by 100, then round up to the nearest 10
                        )


        self.stdout.write(self.style.SUCCESS('Data updated successfully.'))

       

        # Get the hit_weight for each user from UserScores
        user_scores = UserScores.objects.filter(user=F('user__pk')).values('user').annotate(
            hit_weight=Sum('hit_weight')
        )

        # Initialize a dictionary to store the top 3 horses for each race
        top_horses_by_race = {}

        # Iterate over race numbers 1 to 10
        for race_no in range(1, 11):
            # Get the UserTips records for the specified race_no
            user_tips = UserTips.objects.filter(race_no=race_no)

            # Calculate the total hit_weight for each horse in this race
            horse_hit_weight = user_tips.values('horse_name').annotate(
                total_hit_weight=Sum('user__score__hit_weight')
            ).order_by('-total_hit_weight')[:3]

            # Store the top 3 horses for this race in the dictionary
            top_horses_by_race[race_no] = horse_hit_weight

        # Print the top 3 horses for each race
        for race_no, horses in top_horses_by_race.items():
            print(f"Race {race_no}:")
            for rank, horse in enumerate(horses, start=1):
                print(f"  Rank {rank}: {horse['horse_name']} - {horse['total_hit_weight']}")