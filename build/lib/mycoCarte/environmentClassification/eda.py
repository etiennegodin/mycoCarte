import pandas as pd 
import numpy as np

from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

df = pd.read_csv('data/interim/geodata/vector/preprocessedData/preprocessedData.csv')

if np.isnan(df.values).any():
    print("NaNs found, applying SimpleImputer...")
    imputer = SimpleImputer(strategy='mean') # or 'median', 'most_frequent'
    pixel_features_imputed = imputer.fit_transform(df)
    df = pd.DataFrame(pixel_features_imputed)
else:
    print("No NaNs found in the valid pixel data.")

categorical_colums = ['ty_couv_et', 'dep_sur', 'etagement']

for col in categorical_colums:
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    col_encoded = encoder.fit_transform(df[[col]])
    col_encoded_df = pd.DataFrame(col_encoded, columns=encoder.get_feature_names_out([col]))
    df = pd.concat([df.drop(col, axis=1), col_encoded_df], axis=1)
    print("After OneHotEncoding (if applied):")
    
print(df.head())