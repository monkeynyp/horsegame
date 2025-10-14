import pandas as pd
import subprocess

pre_hist_df = pd.read_csv("curr_hist_df_m_2.csv")
update_hist_df = pd.read_csv("race_hist_update.csv")

curr_hist_df = pd.concat([pre_hist_df, update_hist_df], ignore_index=True)

curr_hist_df.to_csv("curr_hist_df_m_2.csv", index=False)  # Set index=False to avoid creating additional index columns
# Call the rest_day.py script
#subprocess.run(["python", "/Users/louisngai/HorsePredictLocal/Utilities/rest_day.py"])
