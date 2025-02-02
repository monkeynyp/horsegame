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
from django.db.models import Count
from racecard.models import Race_hist

no_of_race = input("Input Total Number of Race: ")
mode = input("Do you want to run a new training? (Y/N): ")
if mode.lower() == 'y':
    # Assume you have a DataFrame 'historical_data' containing the historical racing data
    # Connect to the database
    race_hist = (
        Race_hist.objects
        .filter(date__lte='2024-06-31')
        .values()
    )
    race_hist = pd.DataFrame(list(race_hist))
    # Feature Engineering
    # Calculate average running result for each horse-jockey pair
    print(race_hist)
   

