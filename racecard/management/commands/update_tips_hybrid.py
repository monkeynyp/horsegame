from django.core.management.base import BaseCommand
from racecard.models import UserTips,User, UserScores  # Replace 'YourModel' with the actual model name
from datetime import datetime
import pandas as pd
import os
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
       
        user_id = User.objects.get(username="WePower")
        # Get the hit_weight for each user from UserScores
        user_scores = UserScores.objects.filter(user=F('user__pk')).values('user').annotate(
            hit_weight=Sum('hit_weight')
        )

        print(user_scores)
        # Initialize a dictionary to store the top 3 horses for each race
        top_horses_by_race = {}

        # Iterate over race numbers 1 to 10
        for race_no in range(1, num_races+1):
            # Get the UserTips records for the specified race_no
            user_tips = UserTips.objects.filter(race_no=race_no,race_date=race_date)

            # Calculate the total hit_weight for each horse in this race
            horse_hit_weight = user_tips.values('horse_no','horse_name').annotate(
                total_hit_weight=Sum('user__score__hit_weight'),
            ).order_by('-total_hit_weight')[:3]

            # Store the top 3 horses for this race in the dictionary
            top_horses_by_race[race_no] = horse_hit_weight

        print(top_horses_by_race)
        # Print the top 3 horses for each race
        for race_no, horses in top_horses_by_race.items():
            print(f"Race {race_no}:")
            for rank, horse in enumerate(horses, start=1):
                print(f"  Rank {rank}: {horse['horse_name']} - {horse['total_hit_weight']}")
                    # Your logic to update the database with race_date and race_no
                UserTips.objects.update_or_create(
                    user = user_id,
                    race_date = race_date,
                    race_no = race_no,
                    horse_no = horse['horse_no'],
                    horse_name = horse['horse_name'],
                    hit = 0
                    )
    
        self.stdout.write(self.style.SUCCESS('Data updated successfully.'))