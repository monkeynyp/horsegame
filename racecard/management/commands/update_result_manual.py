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
        race_no = input("race_no")
        race_date = options['race_date']
        horse1=input("HorseNo1:")
        dividend1=input("Dividend1:")
        horse2=input("HorseN02:")
        dividend2=input("Dividend2:")
        horse3=input("HorseNo3:")
        dividend3=input("Dividend3:")

        
        # Update UserTips records
        UserTips.objects.filter(
            horse_no=horse1,
            race_date=race_date,
            race_no=race_no,  
        ).update(hit=1, dividend=dividend1)

        UserTips.objects.filter(
            horse_no=horse2,
            race_date=race_date,
            race_no=race_no,  
        ).update(hit=1, dividend=dividend2)

        UserTips.objects.filter(
            horse_no=horse3,
            race_date=race_date,
            race_no=race_no,  
        ).update(hit=1, dividend=dividend3)



        # Loop through the user tips data and update the user scores

