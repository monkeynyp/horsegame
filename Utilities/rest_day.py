import pandas as pd
from datetime import datetime

# Read the CSV file
df = pd.read_csv('../racecard/data/curr_hist_df_m_2.csv')

# Convert the RaceDate column to datetime, handling multiple formats
df['RaceDate'] = pd.to_datetime(df['RaceDate'], format='mixed', dayfirst=False)
# Convert the Place column to integer
try:
    df['Place'] = df['Place'].astype(int)
except ValueError:
    df['Place'] = pd.to_numeric(df['Place'], errors='coerce')

# Sort the dataframe by HorseName and RaceDate
df = df.sort_values(by=['HorseName', 'RaceDate'])

# Calculate the rest days
df['RestDays'] = df.groupby('HorseName')['RaceDate'].diff().dt.days
df['HasPreviousRace'] = df['RestDays'].notna().astype(int)
df['RestDays'] = df['RestDays'].fillna(300)

# Calculate the number of times each horse participated in the last 10 racing days
df['Last10Races'] = df.groupby('HorseName').apply(lambda x: x.rolling(window='60D', on='RaceDate', min_periods=1)['RaceDate'].count()).reset_index(level=0, drop=True)-1

# Sort the dataframe by the original order of the records in curr_hist_df_m_2.csv

df = df.sort_values(by=['RaceDate', 'RaceNo', 'Place'])


# Replace NA values in the 'Place' column with 99
df['Place'] = df['Place'].fillna(99)

df.to_csv('../racecard/curr_hist_df_m_3.csv', index=False)

# Select the required columns for display
# Get the latest race date for each horse
latest_race_date_df = df.groupby('HorseName')['RaceDate'].max().reset_index()
latest_race_date_df.columns = ['HorseName', 'LastRaceDate']

# Calculate the frequency of the horse running the race in the last 60 days from today
today = datetime.now()
df['DaysSinceRace'] = (today - df['RaceDate']).dt.days

# Calculate the frequency correctly
frequency_df = df[df['DaysSinceRace'] <= 60].groupby('HorseName').size().reset_index(name='Frequency')

# Ensure all horses are included in the frequency dataframe
all_horses = df[['HorseName']].drop_duplicates()
frequency_df = all_horses.merge(frequency_df, on='HorseName', how='left').fillna(0)

# Merge the frequency of races in the last 60 days with the latest race date dataframe
latest_race_date_df = latest_race_date_df.merge(frequency_df, on='HorseName', how='left')

# Fill NaN values in Frequency with 0
latest_race_date_df['Frequency'] = latest_race_date_df['Frequency'].astype(int)

# Drop the DaysSinceRace column as it is no longer needed
df = df.drop(columns=['DaysSinceRace'])

# Save the result to a new CSV file
latest_race_date_df.to_csv('../racecard/data/horse_last_racedate.csv', index=False)



