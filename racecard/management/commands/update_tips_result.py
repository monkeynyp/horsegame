from django.core.management.base import BaseCommand
from racecard.models import UserTips,UserScores  # Replace 'YourModel' with the actual model name
from datetime import datetime
import pandas as pd
import os
from django.conf import settings
from django.db.models import Count, Sum

class Command(BaseCommand):
    help = 'Update data from CSV files to SQLite database'

    def add_arguments(self, parser):
        # Add command line arguments
   #     parser.add_argument('num_races', type=int, help='Number of races')
        parser.add_argument('race_date', type=str, help='Race date in YYYY/MM/DD format')
    
    def handle(self, *args, **options):
        # Access command line arguments
    #    num_races = options['num_races']
        #race_date = datetime.strptime(options['race_date'], '%Y-%m-%d').date()
        race_date = options['race_date']
        csv_path = os.path.join(settings.BASE_DIR, "racecard/data/race_hist_update.csv")
        csv_data = pd.read_csv(csv_path)
        print(csv_data)
        # Filter the CSV data for places 1, 2, or 3
        filtered_data = csv_data[(csv_data['Place'] == 1) | (csv_data['Place'] == 2) | (csv_data['Place'] == 3)]
     
        filtered_data = filtered_data[(filtered_data["RaceDate"]==race_date)]
        print(filtered_data[["RaceDate","RaceNo","HorseName","RaceNo","Place"]])
        # Iterate through the filtered data and update UserTips records
        for index, row in filtered_data.iterrows():
            race_date = datetime.strptime(row['RaceDate'], '%Y/%m/%d').date()
            race_no = row['RaceNo']
            horse_name = row['HorseName']
            
            # Update UserTips records
            UserTips.objects.filter(
                horse_name=horse_name,
                race_date=race_date,
                race_no=race_no,  
            ).update(hit=1)


# Get the UserTips data grouped by user, with the total records and total hits
user_tips_data = UserTips.objects.values('user').annotate(
    total_records=Count('id'),
    total_hits=Sum('hit')
)

# Loop through the user tips data and update the user scores
for user_tip in user_tips_data:
# Get or create the user score for the user
    user_score, created = UserScores.objects.get_or_create(user_id=user_tip['user'])
    # Update the user score with the total records and total hits
    user_score.total_records = user_tip['total_records']
    user_score.total_hits = user_tip['total_hits']
    # Save the user score
    user_score.save()
