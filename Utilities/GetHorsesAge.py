# Import the required libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
from pathlib import Path

# Get the HTML content of the web page

df = pd.DataFrame([], columns=["HorseName","Age"])
for age in range(2,10):
    url = "https://racing.hkjc.com/racing/information/english/Horse/ListByAge.aspx?OrderType="+str(age)
    print(url)
    # polite headers and basic error handling
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        continue

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table element using soup.find()
    div = soup.find(id="innerContent")

    # Find the second table element within the div element using soup.find_all()
    #table = div.find_all("table")[1]
    table = div.find_all("table")[3] 
    # Find all the tr elements within the table element using soup.find_all()
    trs = table.find_all("tr")

    # Loop through the tr elements and find the first td element within each tr element using soup.find()

    for tr in trs:
        td = tr.find("li", class_="table_eng_text")
        if td is None:
            continue
        horse_name = td.get_text(strip=True)
        horse_ages = [horse_name, age]
        print(horse_ages)
        df.loc[len(df)] = horse_ages

# Remove duplicate records with the same horse_name
df.drop_duplicates(subset=["HorseName"], inplace=True)

# Print the DataFrame
print(df)
# Ensure output directory exists (make path absolute relative to this script)
base_dir = Path(__file__).resolve().parent.parent  # project root (Utilities/..)
output_dir = base_dir / "racecard" / "data"
os.makedirs(output_dir, exist_ok=True)
out_path = output_dir / "horse_ages202509.csv"
df.to_csv(out_path.as_posix(), index=False)  # Set index=False to avoid creating additional index column
#df.to_csv("../racecard/data/horse_ages202509.csv")
