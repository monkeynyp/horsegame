import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import CategoricalNB
#from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np
import traceback
import joblib
import sqlite3

no_of_race = input("Input Total Number of Race: ")
mode = input("Do you want to run a new training? (Y/N): ")
if mode.lower() == 'y':
    # Assume you have a DataFrame 'historical_data' containing the historical racing data
    # Connect to the database
    conn = sqlite3.connect('/Users/louisngai/horsegame/db.sqlite3')
    query = "SELECT * FROM race_hist WHERE date <= '2024-06-31'"
    race_hist = pd.read_sql_query(query, conn)
    conn.close()
    # Feature Engineering
    # Calculate average running result for each horse-jockey pair
    race_hist['Place'] = pd.to_numeric(race_hist['Place'], errors='coerce')
    race_hist['Draw'] = pd.to_numeric(race_hist['Draw'], errors='coerce')
    race_hist=race_hist.dropna(subset=['Place'])
    race_hist=race_hist.dropna(subset=['Draw'])
    race_hist['Result']=pd.cut(race_hist['Place'], bins=[0,3,15],labels=['1','0'],include_lowest=True)
    #race_hist = race_hist.dropna(subset=['RaceNo'])
    race_hist['Class_pur']=race_hist['Class'].str.split("-").str.get(0).str.rstrip()
    #race_hist['Class_no']=race_hist['Class_pur'].str.extract(r'(\d+)')
    #race_hist=race_hist.dropna(subset=['Class_no'])
    race_hist['Distance']=race_hist['Class'].str.split("-").str.get(1).str.rstrip().str[:-1]
    race_hist['Distance'] = pd.to_numeric(race_hist['Distance'], errors='coerce')
    race_hist['ActWeight'] = pd.to_numeric(race_hist['ActWeight'], errors='coerce')
    race_hist['HorseWeight'] = pd.to_numeric(race_hist['HorseWeight'], errors='coerce')
    race_hist['WeightRatio'] = (race_hist['ActWeight'] / race_hist['HorseWeight']).astype(float)
    race_hist['Year']=race_hist['RaceDate'].str[:4]
    print(race_hist['Year'])
    race_hist=race_hist.dropna(subset=['Distance'])


    test_case=[
    ['HorseName', 'Jockey','Class_pur','Distance','ActWeight','HorseWeight','Venue','Draw'],
    ['HorseName', 'Jockey','Class_pur','Distance','ActWeight','HorseWeight','Venue','Draw','Going'],
    ['HorseName', 'Jockey','Class_pur','Distance','ActWeight','HorseWeight','Venue','Draw','Going','Course'],
        ['HorseName', 'Jockey','Draw','Venue','Course','Distance'],
        #['HorseName', 'Jockey','Draw','Venue','Course'],  #Optimized for Logistic Regression 210 races 0.41333
        #['HorseName', 'Jockey', 'Class_pur', 'ActWeight', 'HorseWeight', 'Venue', 'Draw'] #Optimized for NeroNetClassifier 200 racies 0.40158
        #['HorseName', 'Jockey', 'Class_pur', 'ActWeight', 'Venue', 'Draw','Distance','Going']
        ['HorseName', 'Jockey', 'Class_pur', 'Distance', 'Venue', 'Draw', 'Course','Going','RaceMonth','WeightRatio','Trainer','RestDays'], #350, 413, 0.3933
        ['HorseName', 'Jockey', 'Class_pur', 'Distance','Draw', 'Venue','Course','Going','RaceMonth','WeightRatio','Trainer','RestDays'], 
    #['HorseName', 'Jockey','Class_pur','Distance','ActWeight','HorseWeight','Draw'],
    #['HorseName', 'Jockey', 'Class_pur', 'Distance','Venue','ActWeight', 'Draw', 'Course','Going','RaceMonth','WeightRatio','RestDays'], #Optimized for SVC
    ]

    #Unnamed: 0,RaceDate,Venue,Class,Going,Course,Place,HorseName,Jockey,Trainer,ActWeight,HorseWeight,Draw,FinishTime,WinOdd,RaceNo,Dividend
    

    for i in range(len(test_case)-1,len(test_case)):
    #for i in range(20):
        horse_jockey_avg_result = race_hist
        print(horse_jockey_avg_result)
        categoryList = ["HorseName"]
        #categoryList = []
        if 'Jockey' in test_case[i]:
            categoryList.append("Jockey")
        if 'Class_pur' in test_case[i]:
            categoryList.append("Class_pur")
        # Check if Venue exists in the test_case and add it to new_case if it does
        if 'Venue' in test_case[i]:
            categoryList.append('Venue')
        if 'Going' in test_case[i]:
            categoryList.append('Going')
        if 'Course' in test_case[i]:
            categoryList.append('Course')
        if 'Trainer' in test_case[i]:
            categoryList.append('Trainer')
        #if 'ActWeight' in test_case[i]:
            #categoryList.append('ActWeight')
        #if 'Distance' in test_case[i]:
            #categoryList.append('Distance')
    
        preprocessor = ColumnTransformer(
            transformers=[
                ('categorical', OneHotEncoder(handle_unknown='ignore', sparse_output=True), categoryList)
            ],
            remainder='passthrough'  # Include non-categorical features as is
        )

        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            #('Classifier', LogisticRegression(C=5,max_iter=3000,solver='lbfgs'))
            #('Classifier', CategoricalNB()),
            #('regressor', MLPRegressor(hidden_layer_sizes=(150,), max_iter=500, alpha=0.0001,solver='adam',tol=0.0001,verbose=10, random_state=1))
            ('Classifier',RandomForestClassifier(n_estimators=1299, random_state=42))
            #('classifier', SVC(kernel='rbf', C=7, gamma='auto', probability=True)
            
            #('classifier', MLPClassifier(hidden_layer_sizes=(150,), max_iter=500, alpha=0.000005,
                        #solver='adam', verbose=10, random_state=1, tol=0.0001)),
        ])

        # Train a Random Forest classifier
        X = horse_jockey_avg_result[test_case[i]]
        y = horse_jockey_avg_result['Result']
        pipeline.fit(X, y)


    # Save the trained pipeline to a file
        model_filename = 'trained_random_forest_pipeline.pkl'
        joblib.dump(pipeline, model_filename)
        print(f"Model saved to {model_filename}")

    # # Estimate feature importance
    # importances = pipeline.named_steps['Classifier'].feature_importances_
    # feature_names = X.columns
    # feature_importances = sorted(zip(importances, feature_names), reverse=True)

    # print("Feature importances:")
    # for importance, name in feature_importances:
    #     print(f"{name}: {importance}")
else:
    model_filename = 'trained_random_forest_pipeline.pkl'
    pipeline = joblib.load(model_filename)
    print(f"Model loaded from {model_filename}")
# Predict the new data
    # Predict the new data
    # Data for testing the model, using the recent completed race record.
accuracy = []
test_hist = pd.read_csv('Evaluation/test_curr_hist_df_m.csv')
test_hist['Place'] = pd.to_numeric(test_hist['Place'], errors='coerce')
test_hist['Draw'] = pd.to_numeric(test_hist['Draw'], errors='coerce')
test_hist=test_hist.dropna(subset=['Place'])
test_hist=test_hist.dropna(subset=['Draw'])
test_hist['Class_pur']=test_hist['Class'].str.split("-").str.get(0).str.rstrip()
#test_hist['Class_no']= test_hist['Class_pur'].str.extract(r'(\d+)')
#test_hist=test_hist.dropna(subset=['Class_no'])
test_hist['Distance']=test_hist['Class'].str.split("-").str.get(1).str.rstrip().str[:-1]
test_hist['Result']=pd.cut(test_hist['Place'], bins=[0,3,15],labels=['1','0'],include_lowest=True)
test_hist['Place_shift']=test_hist['Place'].shift()
test_hist['Change'] = np.where(test_hist['Place']<test_hist['Place_shift'],1,0)
test_hist['ActWeight'] = pd.to_numeric(test_hist['ActWeight'], errors='coerce')
test_hist['HorseWeight'] = pd.to_numeric(test_hist['HorseWeight'], errors='coerce')
test_hist['WeightRatio'] = (test_hist['ActWeight'] / test_hist['HorseWeight']).astype(float)
test_hist['seq_no'] = test_hist['Change'].cumsum()+1
test_hist.drop(columns=['Place'], inplace=True)
test_hist['Year'] = test_hist['RaceDate'].str[:4]

race_datas = test_hist[['seq_no','HorseName','Jockey','Draw','Class_pur','ActWeight','HorseWeight','Distance','Venue','Going','Course','Trainer','RaceMonth','Year','WeightRatio','RestDays','Last10Races']]
print("#####Race Data###")

print(race_datas)


score_counter = 0
try:
    for pred_i in range(1,int(no_of_race)+1):
        print(pred_i)

        race_predict_df = pd.DataFrame([],columns=['HorseName'])
        race_data = race_datas[race_datas['seq_no'] == pred_i]

        # Make predictions on the new data
        race_data['Result'] = pipeline.predict(race_data)

        # Print the predictions
        print(race_data)

        new_predictions = pipeline.predict(race_data)

        probabilities = pipeline.predict_proba(race_data)
    
        race_data['prob'] = probabilities[:, 1]
        # Print the probability of each horse belonging to class 1
        #for j, horse_name in enumerate(race_data['HorseName']):
            #   probability_class_1 = probabilities[j, 1]  # Assuming class 1 is the second column
            #   print(f'Probability of {horse_name} : {probability_class_1}')

    
    # Rank the horses based on 'prob' in descending order
        race_data.loc[:, 'rank'] = race_data['prob'].rank(ascending=False, method='dense')
        print(race_data[["HorseName","Jockey","Result","prob","rank"]])

    
        # Print the probability of each horse belonging to class 1

        print(race_data[["HorseName","rank"]])

        place_counter = 0
        for raceitem in race_data["rank"]:
            if raceitem <= 3:
                score_counter=score_counter+1
            place_counter = place_counter+1
            if place_counter == 3:
                break

    print("Score_Counter: ", score_counter)
    print("No of Race: ", no_of_race)

    accuracy_value= score_counter/(3*int(no_of_race))
    print("Accuracy: ", accuracy_value)
    #accuracy.append((test_case[i],accuracy_value))

            
except Exception as e:
    print(e)
    traceback.print_exc()
print(accuracy)

   

