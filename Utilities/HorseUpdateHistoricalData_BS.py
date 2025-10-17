import requests
from bs4 import BeautifulSoup
import pandas as pd
import sys

raceColumn = ['RaceDate', 'RaceNo', 'Venue', 'Class', 'Going', 'Course', 'Place', 'HorseName', 'Jockey', 'Trainer', 'ActWeight',
              'HorseWeight', 'Draw', 'FinishTime', 'WinOdd', 'Dividend', 'RaceMonth']
race_df = pd.DataFrame([], columns=raceColumn)

# Accept command-line arguments if provided
if len(sys.argv) > 2:
    raceDates = sys.argv[1].split(',')
    num_races = int(sys.argv[2])
else:
    raceDates = input("Enter race dates separated by commas (e.g., 2025/01/08,2025/01/15): ").split(',')
    num_races = int(input("Enter the number of races: "))

for race_date in raceDates:
    race_month = race_date.split('/')[1]
    print(race_date)
    for cj in range(1, num_races + 1):
        url = f'https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate={race_date}&RaceNo={cj}'
        print(url)

        # Fetch the page content
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
       
        try:
            # Extract race details from the first table in .race_tab
            race_tab = soup.find('div', class_='race_tab')
            race_table = race_tab.find('table')
            tbody = race_table.find('tbody')
            trs = tbody.find_all('tr')

            # Find raceClass ("Class 5 - ...")
            raceClass = ""
            raceGoing = ""
            raceCourse = ""
            for tr in trs:
                tds = tr.find_all('td')
                if tds:
                    # Class (e.g. "Class 5 - 1800M - (40-0)")
                    if "Class" in tds[0].text:
                        raceClass = tds[0].text.strip()  # "Class 5"
                    # Going (e.g. "GOOD TO FIRM")
                    if "Going" in tds[1].text:
                        raceGoing = tds[2].text.strip()
                    # Course (e.g. "TURF - \"C+3\" Course")
                    if "Course" in tds[1].text:
                        raceCourse = tds[2].text.strip()

            # Fallback for Venue (use previous method)
            span = soup.find('span', class_='f_fl f_fs13')
            if span:
                text = span.get_text(strip=True)
                parts = text.split()
                raceVenue = parts[-2] + " " + parts[-1] if len(parts) >= 2 else ""
                raceVenue = raceVenue + ":"
            print(raceClass, raceGoing, raceCourse, raceVenue)
            # Extract horse details
            raceCard = soup.select('#innerContent > div:nth-child(2) > div:nth-child(5) > table > tbody > tr')
           
            for i, row in enumerate(raceCard, start=1):
                cells = row.find_all('td')
                if len(cells) < 12:
                    continue

                winOdd = cells[11].text.strip()
                if winOdd == "---":
                    continue

                horsePlace = cells[0].text.strip()
                horseName = cells[2].find('a').text.strip()
                jockey = cells[3].find('a').text.strip()
                trainer = cells[4].text.strip()
                actWeight = cells[5].text.strip()
                horseWeight = cells[6].text.strip()
                draw = cells[7].text.strip()
                finishTime = cells[10].text.strip()

                # Extract dividend based on position
                if i == 1:
                    dividend = soup.select_one('#innerContent > div:nth-child(2) > div:nth-child(6) > table > tbody > tr:nth-child(2) > td:nth-child(3)').text.strip()
                elif i == 2:
                    dividend = soup.select_one('#innerContent > div:nth-child(2) > div:nth-child(6) > table > tbody > tr:nth-child(3) > td:nth-child(2)').text.strip()
                elif i == 3:
                    dividend = soup.select_one('#innerContent > div:nth-child(2) > div:nth-child(6) > table > tbody > tr:nth-child(4) > td:nth-child(2)').text.strip()
                else:
                    dividend = 0

                raceData = [race_date, cj, raceVenue, raceClass, raceGoing, raceCourse, horsePlace, horseName, jockey, trainer, actWeight,
                            horseWeight, draw, finishTime, winOdd, dividend, race_month]
                race_df.loc[len(race_df)] = raceData

            # Extract dividend values from the dividend_tab
            dividend_dict = {}
            dividend_tab = soup.find('div', class_='dividend_tab')
            if dividend_tab:
                dividend_table = dividend_tab.find('table')
                dividend_rows = dividend_table.find('tbody').find_all('tr')
                # Track the current pool for PLACE rows
                current_pool = None
                for row in dividend_rows:
                    tds = row.find_all('td')
                    if len(tds) == 3:
                        pool = tds[0].get_text(strip=True)
                        comb = tds[1].get_text(strip=True)
                        value = tds[2].get_text(strip=True)
                        if pool == "WIN":
                            dividend_dict[f"WIN_{comb}"] = value
                        elif pool == "PLACE":
                            dividend_dict[f"PLACE_{comb}"] = value
                            current_pool = "PLACE"
                    elif len(tds) == 2 and current_pool == "PLACE":
                        # For subsequent PLACE rows, pool cell is omitted
                        comb = tds[0].get_text(strip=True)
                        value = tds[1].get_text(strip=True)
                        dividend_dict[f"PLACE_{comb}"] = value

            # Find the performance table for horse results
            performance_div = soup.find('div', class_='performance')
            perf_table = performance_div.find('table')
            perf_tbody = perf_table.find('tbody')
            perf_rows = perf_tbody.find_all('tr')

            for row in perf_rows:
                cells = row.find_all('td')
                if len(cells) < 12:
                    continue

                horsePlace = cells[0].get_text(strip=True)
                horseNo = cells[1].get_text(strip=True)
                horseName = cells[2].find('a').get_text(strip=True) if cells[2].find('a') else cells[2].get_text(strip=True)
                jockey = cells[3].find('a').get_text(strip=True) if cells[3].find('a') else cells[3].get_text(strip=True)
                trainer = cells[4].find('a').get_text(strip=True) if cells[4].find('a') else cells[4].get_text(strip=True)
                actWeight = cells[5].get_text(strip=True)
                horseWeight = cells[6].get_text(strip=True)
                draw = cells[7].get_text(strip=True)
                finishTime = cells[10].get_text(strip=True)
                winOdd = cells[11].get_text(strip=True)

                # Set dividend value for 1st, 2nd, 3rd place horses using PLACE pool
                if horsePlace in ["1", "2", "3"]:
                    dividend = dividend_dict.get(f"PLACE_{horsePlace}", "0")
                else:
                    dividend = "0"

                raceData = [race_date, cj, raceVenue, raceClass, raceGoing, raceCourse, horsePlace, horseName, jockey, trainer, actWeight,
                            horseWeight, draw, finishTime, winOdd, dividend, race_month]
                race_df.loc[len(race_df)] = raceData

        except AttributeError:
            print("Element not found, skipping this race.")
            continue

print(race_df)

#race_df.to_csv('race_hist_update.csv', index=False)
race_df.to_csv('race_hist_update.csv', index=True)