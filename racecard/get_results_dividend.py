import requests
from bs4 import BeautifulSoup

url = "https://racing.hkjc.com/racing/information/English/Racing/LocalResults.aspx?RaceDate=2024/03/20&Racecourse=HV&RaceNo=2"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
#print(soup)

table = soup.find("table", {"class": "table_bd f_tac f_fs13 f_fl"})
print(table)
rows = table.find_all("tr")



dividend_data = {}
extract_data = False

for row in rows:
    columns = row.find_all("td")
    if len(columns) == 3:
        if columns[0].text.strip() == "PLACE":
            extract_data = True
        elif extract_data:
            horse_no = columns[0].text.strip()
            dividend = columns[1].text.strip()
            print(f"Horse No: {horse_no}, Dividend: {dividend}")


print(dividend_data)