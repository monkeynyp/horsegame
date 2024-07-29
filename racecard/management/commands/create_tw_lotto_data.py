from django.core.management.base import BaseCommand
import pandas as pd
from datetime import datetime
from racecard.models import TW_lotto_hist

class Command(BaseCommand):
    help = 'Import data from Lotto_649.csv into W_lotto_hist model'

    def handle(self, *args, **options):
        file_path = 'racecard/data/Lotto_649.csv'
        data = pd.read_csv(file_path)

        for index, row in data.iterrows():
            draw = row['期數']
            date = datetime.strptime(row['日期'], '%Y-%m-%d').date()
            no1 = row['中獎號碼 1']
            no2 = row['2']
            no3 = row['3']
            no4 = row['4']
            no5 = row['5']
            no6 = row['6']
            extra_number = row['特別號碼']

            TW_lotto_hist.objects.create(
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
