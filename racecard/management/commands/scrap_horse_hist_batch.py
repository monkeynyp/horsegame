import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from racecard.models import HorseInfo, Race_hist
from datetime import datetime

class Command(BaseCommand):
    help = 'Scrape race history information and insert into RaceHist table'
    # Query to read data from the horse_info table 
    
    def handle(self, *args, **kwargs):
        horse_info_list = HorseInfo.objects.exclude(horse_name_cn__isnull=True).exclude(horse_name_cn__exact='')
        for horse_info in horse_info_list:
            band_no = horse_info.band_no
            print("band_no:",band_no)
            url = "https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseNo="+band_no
            print("URL:",url)
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table with the specified attributes
            table = soup.find('table', {'class': 'bigborder', 'style': 'width:970px;'})
            if not table:
                self.stdout.write(self.style.ERROR('Table not found'))
                continue

            rows = table.find_all('tr')[1:]  # Skipping the header row

            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 18:
                    continue  # Skip rows that don't have enough columns

                if cols[0].text.strip().isdigit():   
                    index = int(cols[0].text.strip())
                else:
                    continue # Skip the oversea records
                if cols[1].text.strip().isdigit():
                    place = int(cols[1].text.strip())
                else:
                    continue
                   
                date_str = cols[2].text.strip()
                try:
                    date = datetime.strptime(date_str, '%d/%m/%Y').date()
                except ValueError:
                    date = datetime.strptime(date_str, '%d/%m/%y').date()
                
                track = cols[3].text.strip()
                distance = int(cols[4].text.strip())
                good = cols[5].text.strip()
                race_class = cols[6].text.strip()
                if cols[7].text.strip().isdigit():
                    draw = int(cols[7].text.strip())
                else:
                    continue
                rating_text = cols[8].text.strip()
                rating = int(rating_text) if rating_text != '--' else 0
                trainer = cols[9].text.strip()
                jockey = cols[10].text.strip()
                lbw = cols[11].text.strip()
                if cols[12].text.strip().isdigit():
                     win_odds = float(cols[12].text.strip())
                else:
                     win_odds = 999
                if cols[13].text.strip().isdigit():
                    act_wt = int(cols[13].text.strip())
                else:
                    act_wt = 999
                running_pos = cols[14].text.strip()
                finish_time = cols[15].text.strip()
                if cols[16].text.strip().isdigit():
                    declar_horse_wt = int(cols[16].text.strip())
                else:
                    declar_horse_wt = 999
                gear = cols[17].text.strip()
                horse_name = "A AMERIC TE SPECSO"  # Example horse name
                band_id = HorseInfo.objects.get(band_no=band_no)  # Example band_no

                Race_hist.objects.update_or_create(
                    index=index,
                    place=place,
                    date=date,
                    track=track,
                    distance=distance,
                    good=good,
                    race_class=race_class,
                    draw=draw,
                    rating=rating,
                    trainer=trainer,
                    jockey=jockey,
                    lbw=lbw,
                    win_odds=win_odds,
                    act_wt=act_wt,
                    running_pos=running_pos,
                    finish_time=finish_time,
                    declar_horse_wt=declar_horse_wt,
                    gear=gear,
                    #horse_name=horse_name,
                    band_no=band_id
                )

        self.stdout.write(self.style.SUCCESS('Successfully scraped and updated RaceHist'))
