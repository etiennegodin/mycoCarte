import pandas as pd 
import datetime
from numpy import NaN



def filter(df, key,value):
    df = df[df[key] == value]
    print(f'Filtering {key} by {value}, new df size = {df.shape[0]}')
    return df


def drop_duplicates(df, subset):
    """
    subset : list 
    """
    df = df.drop_duplicates(subset=subset, keep = 'last')
    print(f'Removing duplicates for {subset}, new df size = {df.shape[0]}')

    return df 
def cleanOccurences(path):
    # Removing un-used columns
    cols = ['id',
        'observed_on',
        'quality_grade',
        'url',
        'latitude',
        'longitude',
        'coordinates_obscured',
        'scientific_name',
        'taxon_id'
        ]

    df = pd.read_csv(path, usecols=cols)
    print(df)
    print(f'Reading {df.shape[0]} occurences')

    # Data Type restructure 

    #Observed On string to datetime 
    df['observed_on'] = pd.to_datetime(df['observed_on'])

    # Observation quality integer encoding
    df.loc[df['quality_grade'] == 'needs_id', 'quality_grade'] = 0
    df.loc[df['quality_grade'] == 'research', 'quality_grade'] = 1


    convert_dict = {'quality_grade': int}
    df = df.astype(convert_dict)

    print(df.dtypes)


    # Dropping duplicates
    df = drop_duplicates(df, ['id'])
    df = drop_duplicates(df, ['latitude'])
    df = drop_duplicates(df, ['longitude'])

    return df 

if __name__ == '__main__':
    path = 'data/raw/occurences/iNaturalist_all_Basidiomycetes.csv'

    df = cleanOccurences(path)