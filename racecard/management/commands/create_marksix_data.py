from django.core.management.base import BaseCommand
import pandas as pd
from datetime import datetime
from racecard.models import Marksix_hist

class Command(BaseCommand):
    help = 'Import data from Mark_Six.csv into Marksix_hist model'

    def handle(self, *args, **options):
        file_path = 'racecard/data/Mark_Six.csv'
        data = pd.read_csv(file_path)

        for index, row in data.iterrows():
            draw = row['Draw']
            date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
            no1 = row['Winning Number 1']
            no2 = row['2']
            no3 = row['3']
            no4 = row['4']
            no5 = row['5']
            no6 = row['6']
            extra_number = row['Extra Number']

            Marksix_hist.objects.create(
                Draw=draw,
                Date=date,
                No1=no1,
                No2=no2,
                No3=no3,
                No4=no4,
                No5=no5,
                No6=no6,
                No7=extra_number
            )

        self.stdout.write(self.style.SUCCESS('Data imported successfully.'))
