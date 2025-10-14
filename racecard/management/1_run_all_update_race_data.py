import subprocess

# Get all required inputs once
last_race_date = input("Last Race Date (YYYY/MM/DD): ")
last_no_of_race = input("Last Num of Races: ")
current_race_date = input("Current Race Date (YYYY/MM/DD): ")
current_no_of_race= input("Current Num of Races: ")


# 1. Update historical data
subprocess.run([
    "python3", "Utilities/HorseUpdateHistoricalData_BS.py",
    last_race_date, last_no_of_race
])

# 2. Concatenate historical files
subprocess.run([
    "python3", "Utilities/concat_hist_file.py"
])

# 3. Calculate rest days
subprocess.run([
    "python3", "Utilities/rest_day.py"
])

# 4. Get current race card
subprocess.run([
    "python3", "Utilities/GetCurrentRaceCard_BS.py",
    current_race_date, current_no_of_race
])

# 5. Merge horse ages
subprocess.run([
    "python3", "Utilities/MergeHorseAges.py"
])

# 6. Get win/loss data
subprocess.run([
    "python3", "Utilities/GetWinLostData.py",
    current_no_of_race, current_race_date
])

