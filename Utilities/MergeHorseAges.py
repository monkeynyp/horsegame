# /Users/louisngai/HorsePredictLocal/merge_horse_data.py

import pandas as pd

# Read in the CSV files

curr_hist_df = pd.read_csv('curr_hist_df_m_3.csv')
horse_ages = pd.read_csv('horse_ages202509.csv')

for i in range(1, 12):
    # Read in the current race CSV file
    curr_race_df = pd.read_csv(f'../racecard/data/current_race_{i}.csv')
    
    # Merge the dataframes on HorseName
    merged_df = pd.merge(curr_race_df, horse_ages, on='HorseName', how='left')
    
    # Save the merged dataframe to a new CSV file
    merged_df.to_csv(f'../racecard/data/new_current_race_{i}.csv', index=False)

# Merge the dataframes on HorseName
merged_df = pd.merge(curr_hist_df, horse_ages, on='HorseName', how='left')

# Function to adjust age based on RaceDate
def adjust_age(row):
    race_year = int(row['RaceDate'][:4])
    age_2025 = row['Age']
    adjusted_age = age_2025 - (2025 - race_year)
    return adjusted_age

# Apply the function to adjust ages
merged_df['AdjustedAge'] = merged_df.apply(adjust_age, axis=1)

# Save the merged dataframe to a new CSV file
merged_df.to_csv('../racecard/data/curr_hist_df_m_5.csv', index=True)