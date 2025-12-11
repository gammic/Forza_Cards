import pandas as pd
import numpy as np

original_db = pd.read_csv('db.csv', na_values="-")
db = original_db[
    ["Name", "Manufacturer", "Year", "Model", "Type", "Rarity.1", "Country", "PI", "PI.1", "Speed", "Handling",
     "Acceleration", "Launch", "Braking", "Offroad", "Average Stat"]]
db.rename(columns={"Name": "name", "Manufacturer": "man", "Year": "year", "Model": "model", "Type": "type",
                   "Rarity.1": "rarity",
                   "Country": "country", "PI": "class", "PI.1": "PI", "Speed": "speed", "Handling": "handling",
                   "Acceleration": "acceleration", "Launch": "launch", "Braking": "braking", "Offroad": "offroad",
                   "Average Stat": "avg"}, inplace=True)
print(db.isna().sum())
db = db.dropna()
print(db.columns)
print(db.info())
db.to_csv('db_cleaned.csv', index=False)
