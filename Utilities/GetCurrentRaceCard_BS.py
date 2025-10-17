import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import date
import sys

today = str(date.today())

if len(sys.argv) > 2:
    race_date = sys.argv[1]
    race_no = sys.argv[2]
else:
    race_date = input("Current Race Date (YYYY/MM/DD): ")
    race_no = input("Total Races: ")

race_no = int(race_no)
horse_last_race = pd.read_csv('horse_last_racedate.csv')
cur_raceColumn = ['Racedate','HorseNo','HorseName','HorseName_cn','Jockey','Jockey_cn','ActWeight','HorseWeight','Draw','Trainer','Total','Class','Distance','Venue','Course','Going','RaceTime','RestDays','Freq','Gear','HorseScore']

for rn in range(1, race_no + 1):
    curr_race_df = pd.DataFrame([], columns=cur_raceColumn)
    url = f'https://racing.hkjc.com/racing/information/English/racing/RaceCard.aspx?RaceDate={race_date}&RaceNo={rn}'
    url_chi = f'https://racing.hkjc.com/racing/information/Chinese/racing/RaceCard.aspx?RaceDate={race_date}&RaceNo={rn}'
    print(url)

    # Get English and Chinese pages
    resp = requests.get(url)
    resp_chi = requests.get(url_chi)
    soup = BeautifulSoup(resp.content, 'html.parser')
    soup_chi = BeautifulSoup(resp_chi.content, 'html.parser')

    # Extract race condition info (Class, Distance, Venue, Course, Going, RaceTime)
    race_info_div = soup.find('div', class_='margin_top10')
    race_info_text = race_info_div.find('div', class_='f_fs13').get_text(separator="\n") if race_info_div else ""
    lines = race_info_text.split("\n")
    race_class = race_distance = race_venue = race_course = race_going = race_time = ""
    for line in lines:
        # Capture "Class N" or "Group One/Two/Three" (also "Group 1", etc.)
        class_match = re.search(r'(Class\s*\d+|Group\s+(?:One|Two|Three|Four|Five|\d+))', line, re.IGNORECASE)
        race_class = class_match.group(0).strip() if class_match else ""
        if "Turf" in line or "All Weather" in line:
            # Extract course in format "TURF - \"C+3\" Course"
            course_match = re.search(r'(Turf|All Weather)[^,]*,\s*"[^"]+"\s*Course', line, re.IGNORECASE)
            if course_match:
                race_course = course_match.group(0).strip()
            else:
                # Fallback: try to extract course manually
                parts = line.split(",")
                if len(parts) > 1 and "Course" in parts[1]:
                    race_course = f'"TURF - ""{parts[1].replace("Course", "").strip()}"" Course"'
            race_distance = re.search(r'(\d+)M', line)
            race_distance = race_distance.group(1) if race_distance else ""

            # Extract race time in HH:MM format (e.g., "18:40") from the race info div HTML
            if race_info_div:
                race_info_html = race_info_div.decode_contents()
                time_match = re.search(r'(\d{2}:\d{2})', race_info_html)
                race_time = time_match.group(1) if time_match else ""
        if "Good" in line or "Firm" in line or "Yielding" in line or "Wet" in line or "Soft" in line:
            race_going = line.split(",")[-1].strip()
        else:
            race_going = "Good"
        if "Happy Valley" in line:
            race_venue = "Happy Valley:"
        elif "Sha Tin" in line:
            race_venue = "Sha Tin"

    # Extract horse details from the starter table
    starter_table = soup.find('table', {'class': 'starter'})
    if starter_table:
        starter_rows = starter_table.find('tbody').find_all('tr', class_='f_tac f_fs13')
        for i, row in enumerate(starter_rows, 1):
            cells = row.find_all('td')
            if len(cells) < 24:
                continue
            horse_no = cells[0].get_text(strip=True)
            horseName = cells[3].find('a').get_text(strip=True) if cells[3].find('a') else cells[3].get_text(strip=True)
            # Chinese name extraction (from Chinese page)
            horseName_cn = ""
            starter_table_chi = soup_chi.find('table', {'class': 'starter'})
            if starter_table_chi:
                starter_rows_chi = starter_table_chi.find('tbody').find_all('tr', class_='f_tac f_fs13')
                if len(starter_rows_chi) >= i:
                    horseName_cn = starter_rows_chi[i-1].find_all('td')[3].get_text(strip=True)
            jockey = cells[6].find('a').get_text(strip=True) if cells[6].find('a') else cells[6].get_text(strip=True)
            jockey = re.sub(r"\(-\d+\)", "", jockey).strip()
            # Chinese jockey name
            jockey_cn = ""
            if starter_table_chi:
                if len(starter_rows_chi) >= i:
                    jockey_cn = starter_rows_chi[i-1].find_all('td')[6].get_text(strip=True)
            actWeight = cells[5].get_text(strip=True)
            draw = cells[8].get_text(strip=True)
            trainer = cells[9].find('a').get_text(strip=True) if cells[9].find('a') else cells[9].get_text(strip=True)
            horse_weight = cells[13].get_text(strip=True)
            # Gear: extract from the <td> with Gear info (usually last column)
            gear = cells[-1].get_text(strip=True)
            # If gear is empty, try to extract from a <div class="Gear"> nearby
            if not gear:
                gear_div = soup.find('div', class_='Gear')
                if gear_div:
                    gear = gear_div.get_text(strip=True)
            horse_score = cells[11].get_text(strip=True)
            # Last run and frequency
            try:
                last_race_date_str = horse_last_race.loc[horse_last_race['HorseName'] == horseName, 'LastRaceDate'].values[0]
                last_race_date = pd.to_datetime(last_race_date_str)
                race_date_dt = pd.to_datetime(race_date)
                last_race_day = (race_date_dt - last_race_date).days
                frequency = horse_last_race.loc[horse_last_race['HorseName'] == horseName, 'Frequency'].values[0]
            except (IndexError, KeyError):
                last_race_day = 300
                frequency = 0

            raceData = [
                race_date, horse_no, horseName, horseName_cn, jockey, jockey_cn, actWeight, horse_weight, draw, trainer,
                race_no, race_class, race_distance, race_venue, race_course, race_going, race_time,
                last_race_day, frequency, gear, horse_score
            ]
            curr_race_df.loc[len(curr_race_df)] = raceData

    #curr_race_df.to_csv(f'current_race_{rn}.csv', index=True)
    curr_race_df.to_csv(f'../racecard/data/current_race_{rn}.csv', index=True)