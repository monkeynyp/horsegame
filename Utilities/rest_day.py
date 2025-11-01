import pandas as pd
from datetime import datetime
import numpy as np

# Read the CSV file
df = pd.read_csv('../racecard/data/curr_hist_df_m_2.csv')

# Convert the RaceDate column to datetime, handling multiple formats (coerce invalid)
df['RaceDate'] = pd.to_datetime(df['RaceDate'], infer_datetime_format=True, errors='coerce')
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

# Calculate the number of times each horse participated in the last 60 days (excluding current race)
# Use a robust per-group approach to avoid rolling() monotonic/NaT issues.
def _count_last_60(group):
    # work on a copy to avoid modifying original order
    dates = group['RaceDate']
    # sort dates and keep corresponding index order
    sorted_idx = dates.sort_values().index
    sorted_dates = dates.loc[sorted_idx].values.astype('datetime64[ns]')
    n = len(sorted_dates)
    counts = np.zeros(n, dtype=int)
    for i in range(n):
        d = sorted_dates[i]
        if pd.isna(d):
            counts[i] = 0
            continue
        start = d - np.timedelta64(60, 'D')
        # count dates in [start, d] then subtract 1 to exclude current race
        cnt = int(((sorted_dates >= start) & (sorted_dates <= d)).sum()) - 1
        counts[i] = max(0, cnt)
    # return Series indexed by the original index positions
    return pd.Series(counts, index=sorted_idx)

# Apply per-group and align back to original DataFrame index
last10_series = df.groupby('HorseName', sort=False).apply(_count_last_60)
# groupby.apply produced a Series with a MultiIndex (HorseName, original_index) — drop the first level
last10_series = last10_series.reset_index(level=0, drop=True)
df['Last10Races'] = last10_series.reindex(df.index).fillna(0).astype(int)

# Sort the dataframe by the original order of the records in curr_hist_df_m_2.csv

df = df.sort_values(by=['RaceDate', 'RaceNo', 'Place'])


# Replace NA values in the 'Place' column with 99
df['Place'] = df['Place'].fillna(99)

df.to_csv('../racecard/data/curr_hist_df_m_3.csv', index=False)

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



