# /Users/louisngai/horsegame/update_race_hist.py

import pandas as pd
from racecard.models import Race_hist, HorseInfo
import os
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Update race history from database'

    def handle(self, *args, **kwargs):
        csv_path = os.path.join(settings.BASE_DIR, "racecard/data/curr_hist_df_m_3.csv")
        # Step 1: Read all the records from curr_hist_df_m_3.csv into a dataset e.g race_hist
        race_hist = pd.read_csv(csv_path)

        # Step 2: Read all the records from the table race_hist into a dataset, e.g race_hist_db

        # Fetch all Race_hist records and related Horse_info records
        race_hist_records = Race_hist.objects.select_related('band_no').all()

        # Create a list of dictionaries with race_hist data and horse_name from horse_info
        race_hist_data = []
        for record in race_hist_records:
            race_hist_data.append({
                'id': record.id,
                'date': record.date,
                'band_no': record.band_no.band_no,
                'gear': record.gear,
                'rating': record.rating,
                'horse_name': record.band_no.horse_name
            })

        # Convert the list of dictionaries to a DataFrame
        race_hist_db = pd.DataFrame(race_hist_data)

        print(race_hist_db.head)
        # Step 3: Match 2 datasets by matching the race_hist.RaceDate = race_hist_db.date and race_hist.HorseName=race_hist_db.band_no

        # Convert RaceDate and date columns to datetime format
        race_hist['RaceDate'] = pd.to_datetime(race_hist['RaceDate'], format='%Y-%m-%d')
        race_hist_db['date'] = pd.to_datetime(race_hist_db['date'], format='%Y-%m-%d')
        # Create the new columns race_hist['Gear'] and race_hist['Rating']
        # Ensure the 'HorseName' and 'horse_name' columns are stripped of leading/trailing spaces and are in the same case
        race_hist['HorseName'] = race_hist['HorseName'].str.strip()
        race_hist_db['horse_name'] = race_hist_db['horse_name'].str.strip()

        merged_df = pd.merge(race_hist, race_hist_db, left_on=['RaceDate', 'HorseName'], right_on=['date', 'horse_name'], how='left')
        
        merged_df.to_csv('/Users/louisngai/horsegame/merged_df.csv', index=False)   

        # Close the database connection 
        # No need to close the database connection when using Django ORM