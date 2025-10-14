# Import the required libraries
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Get the HTML content of the web page

df = pd.DataFrame([], columns=["HorseName","Age"])
for age in range(2,10):
    url = "https://racing.hkjc.com/racing/information/english/Horse/ListByAge.aspx?OrderType="+str(age)
    print(url)
    response = requests.get(url)

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
        td = tr.find("li", class_ ="table_eng_text")
    # Get the text content of the td element using .text and strip any whitespace using .strip()
        horse_name = td.text.strip()
    # Store the horse name in a list
        horse_ages=[horse_name,age]
        print(horse_ages)
        df.loc[len(df)] = horse_ages

# Remove duplicate records with the same horse_name
df.drop_duplicates(subset=["HorseName"], inplace=True)

# Print the DataFrame
print(df)
df.to_csv("horse_ages202509.csv")
