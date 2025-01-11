from selenium import webdriver
from selenium.webdriver.common.by import By
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

#from selenium import webdriver

# Create a new instance of the Firefox driver
#driver = webdriver.Firefox()
driver = webdriver.Chrome()

# Get input for race_date, venue, and number of races
race_date = input("Enter the race date (YYYY-MM-DD): ")
venue = input("Enter the venue: ")
num_races = int(input("Enter the number of races: "))

# Loop through each race
for race_no in range(1, num_races + 1):
    # Create the URL
    url = f'https://bet.hkjc.com/en/racing/wp/{race_date}/{venue}/{race_no}'
    
    # Go to the webpage
    driver.get(url)
    #driver.implicitly_wait(10) # seconds

    # Wait until the elements are present
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"div[id^='odds_WIN_{race_no}_']")))

    # Find the elements with the specific ids for No, Win, and Place
    no_elements = driver.find_elements(By.CSS_SELECTOR, f"td[id^='runnerNo_{race_no}_']")
    win_elements = driver.find_elements(By.CSS_SELECTOR, f"div[id^='odds_WIN_{race_no}_']")
    place_elements = driver.find_elements(By.CSS_SELECTOR, f"div[id^='odds_PLA_{race_no}_']")

    # Extract the text or value from the elements and write to CSV
    with open(f'../horsegame/racecard/data/race_odds_{race_no}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['horse_no', 'win', 'place'])
        for no, win, place in zip(no_elements, win_elements, place_elements):
            writer.writerow([no.text, win.text, place.text])

# Close the browser
driver.quit()