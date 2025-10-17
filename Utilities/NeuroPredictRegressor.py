import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import sys
from sklearn import __version__ as sklearn_version
from distutils.version import LooseVersion

def simulate_race(win_probabilities, horses):
    # Simulate the race outcome
    winner = np.random.choice(horses, p=win_probabilities)
    return winner

if len(sys.argv) > 1:
    no_of_race = sys.argv[1]
else:
    no_of_race = input("Input Total Number of Race: ")
# Assume you have a DataFrame 'historical_data' containing the historical racing data
race_hist = pd.read_csv('curr_hist_df_m_3.csv')
# Feature Engineering
race_hist['RaceMonth'] = pd.to_numeric(race_hist['RaceMonth'])
# Calculate average running result for each horse-jockey pair
race_hist['Place'] = pd.to_numeric(race_hist['Place'], errors='coerce')
race_hist['Draw'] = pd.to_numeric(race_hist['Draw'], errors='coerce')
race_hist=race_hist.dropna(subset=['Place'])
race_hist=race_hist.dropna(subset=['Draw'])
race_hist = race_hist[race_hist['Place'] != 99]


race_hist['Class_pur']=race_hist['Class'].str.split("-").str.get(0).str.rstrip()
race_hist['Distance']=race_hist['Class'].str.split("-").str.get(1).str.rstrip().str[:-1]
race_hist['Distance'] = pd.to_numeric(race_hist['Distance'], errors='coerce')
race_hist=race_hist.dropna(subset=['Distance'])
race_hist['ActWeight'] = pd.to_numeric(race_hist['ActWeight'], errors='coerce')
race_hist['HorseWeight'] = pd.to_numeric(race_hist['HorseWeight'], errors='coerce')
race_hist['WeightRatio'] = (race_hist['ActWeight'] / race_hist['HorseWeight']).astype(float)
race_hist['Year']=race_hist['RaceDate'].str[:4]
horse_jockey_avg_result = race_hist.groupby(['HorseName', 'Jockey','Class_pur','Distance','Draw','Course','Venue','Going','RaceMonth','WeightRatio','RestDays','HasPreviousRace'])['Place'].mean().reset_index()
horse_jockey_avg_result.columns = ['HorseName', 'Jockey','Class','Distance','Draw','Course','Venue','Going','RaceMonth','WeightRatio','RestDays','HasPreviousRace','AvgResult']
print(horse_jockey_avg_result)

# Create OneHotEncoder compatibly with installed scikit-learn version
if LooseVersion(sklearn_version) >= LooseVersion("1.2"):
    ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=True)
else:
    # Old sklearn versions use `sparse` argument
    ohe = OneHotEncoder(handle_unknown='ignore', sparse=False)

preprocessor = ColumnTransformer(
    transformers=[
        ('categorical', ohe, ['HorseName','Jockey','Class','Course','Going','Venue'])
    ],
    remainder='passthrough'  # Include non-categorical features as is
)

pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('regressor', MLPRegressor(hidden_layer_sizes=(150,), max_iter=500, alpha=0.000003,
                     solver='adam',tol=0.0001,verbose=10, random_state=1))
]) #23

# Train a Random Forest classifier
X = horse_jockey_avg_result[['HorseName', 'Jockey','Class','Distance','Draw','Course','Venue','Going','RaceMonth','WeightRatio','RestDays']]
y = horse_jockey_avg_result['AvgResult']
pipeline.fit(X, y)

# New race data
for i in range(1,int(no_of_race)+1): 
    race_predict_df = pd.DataFrame([],columns=['HorseName','Score'])  
    new_race_data = pd.read_csv('../racecard/data/current_race_'+str(i)+'.csv')
    new_race_data['ActWeight'] = pd.to_numeric(new_race_data['ActWeight'], errors='coerce')
    new_race_data['HorseWeight'] = pd.to_numeric(new_race_data['HorseWeight'], errors='coerce')
    new_race_data['WeightRatio'] = (new_race_data['ActWeight'] / new_race_data['HorseWeight']).astype(float)
    new_race_data['Last10Races'] = new_race_data['Freq']
    
    new_race_data['RaceMonth'] = 10
    new_race_data['Year'] = 2025
# Encode new race data
    #encoded_new_race_data = encoder.transform(new_race_data[['HorseName','Jockey','Class','Distance']])
    #encoded_new_race_data_df = pd.DataFrame(encoded_new_race_data, columns=encoder.get_feature_names_out(['HorseName', 'Jockey']))
    #X_new_race = pd.concat([new_race_data[['Distance']], encoded_new_race_data_df], axis=1)


# Predict running result for each horse
    new_race_data['PredictedResult'] = pipeline.predict(new_race_data)
    predictions = pipeline.predict(new_race_data)

# Define a function to transform predictions to probabilities
    def softmax(x):
        inverted_x = -x  # Invert the predictions
        e_x = np.exp(inverted_x - np.max(inverted_x))
        return e_x / e_x.sum(axis=0)

    # Transform predictions to probabilities
    win_probabilities = softmax(predictions)

# Rank the horses based on predicted running result
    new_race_data['Rank'] = new_race_data['PredictedResult'].rank(method='min')

   # print(new_race_data[['HorseName','Rank']])

# Get the top 3 horses
    top_3_horses = new_race_data.sort_values(by='Rank').head(3)['HorseName'].tolist()

    print("Predicted Top 3 Horses:", top_3_horses)

   # Calculate score
    top_3_horses_df = new_race_data.sort_values(by='Rank').head(3)
   

    #Create DataFrame
   
    num_simulations = 10000
    horses = new_race_data['HorseName'].values
    results = {horse: 0 for horse in horses}

    # Run simulations
    for _ in range(num_simulations):
        winner = simulate_race(win_probabilities, horses)
        results[winner] += 1

    # Calculate winning probabilities
    winning_probabilities = {horse: count / num_simulations for horse, count in results.items()}
    print(win_probabilities)
    race_prob = pd.DataFrame(win_probabilities, columns=['Values'])
     # Display results
    print("Winning probabilities after simulation:")
    for horse, probability in winning_probabilities.items():
        print(f"{horse}: {probability:.2%}")   

       # Calculate score
    #top_3_horses_df = new_race_data.sort_values(by='Rank').head(3)
    top_3_horses_df['Score'] = race_prob.sort_values(by='Values', ascending=False).head(3)['Values'].values
    print(top_3_horses_df)

    race_predict_df = pd.DataFrame(top_3_horses_df[['HorseName','HorseName_cn','Jockey','Trainer','Score']])

    print(race_predict_df)
    race_predict_df.to_csv('../racecard/data/predict_race_neu2'+str(i)+'.csv')
    #race_prob.to_csv('../horsegame/racecard/data/predict_race_neu2_weight'+str(i)+'.csv')