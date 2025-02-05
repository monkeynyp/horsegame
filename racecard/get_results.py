import requests
from bs4 import BeautifulSoup
from datetime import date
from .models import UserTips
from datetime import datetime

def get_results(race_no):
    race_date = date.today()
    #race_date=datetime.strptime("2025-02-05","%Y-%m-%d") 
    #print(race_date)
    formatted_date = race_date.strftime('%Y/%m/%d')
    print(formatted_date)
    response = requests.get('https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate='+str(formatted_date)+'&RaceNo='+str(race_no))
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"class": "table_bd f_tac f_fs13 f_fl"})
    rows = table.find_all("tr")
    
    print("race_no",race_no)

    for index, row in enumerate(rows):
        columns = row.find_all("td", class_="f_fs14")
        if index >= 3 and index <= 5:
            horse_no = columns[0].text.strip()
            dividend = columns[1].text.strip()
            print(f"Horse No: {horse_no}, Dividend: {dividend}")

            UserTips.objects.filter(
                horse_no=horse_no,
                race_date=race_date,
                race_no=race_no,  
              ).update(hit=1, dividend=dividend)

