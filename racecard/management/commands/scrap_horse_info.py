import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from racecard.models import HorseInfo
import time

class Command(BaseCommand):
    help = 'Scrape horse information and insert into HorseInfo table'

    def handle(self, *args, **kwargs):
        url = "https://racing.hkjc.com/racing/info/mcs/Chinese/Horses/clas"
        response = requests.get(url)
        time.sleep(10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table with the ID 'tbHorseList'
        main_table = soup.find('table', {'id': 'tbHorseList'})
        if not main_table:
            self.stdout.write(self.style.ERROR('Main table not found'))
            return

        # Find all inner tables with the class 'table report_body_small'
        inner_tables = main_table.find_all('table', {'class': 'table report_body_small'})
        if len(inner_tables) < 2:
            self.stdout.write(self.style.ERROR('Second inner table not found'))
            return

        # Select the second inner table
        inner_table = inner_tables[1]

        rows = inner_table.find_all('tr')[1:]  # Skip the header row

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 4:
                continue  # Skip rows that don't have enough columns

            horse_name = cols[0].text.strip()
            horse_name_cn = cols[1].text.strip()
            band_no = cols[2].text.strip()
            rating = cols[3].text.strip()
            rate_change = cols[4].text.strip()
            if rate_change == '*':
                rate_change = 0

            # Handle missing ratings and rate changes
            rating = int(rating) if rating else 0
            rate_change = int(rate_change) if rate_change else 0

            HorseInfo.objects.update_or_create(
                band_no=band_no,
                defaults={
                    'horse_name': horse_name,
                    'horse_name_cn': horse_name_cn,
                    'rating': rating,
                    'rate_change': rate_change,
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully scraped and updated HorseInfo'))
