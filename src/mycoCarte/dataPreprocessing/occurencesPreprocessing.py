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
        'captive_cultivated',       
        'latitude',
        'longitude',
        'positional_accuracy',
        'taxon_id',
        'taxon_class_name','taxon_order_name','taxon_family_name','taxon_genus_name','taxon_species_name'
          ]

    df = pd.read_csv(path, usecols=cols)
    print(f'Reading {df.shape[0]} occurences')

    #Rename taxon cols:
    cols_rename = { 'taxon_class_name' : 'taxon_class',
                   'taxon_order_name' : 'taxon_order',
                   'taxon_family_name' : 'taxon_family',
                   'taxon_genus_name' : 'taxon_genus',
                   'taxon_species_name' : 'taxon_species',
    }

    df.rename(columns = cols_rename, inplace= True)

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

    # Check of many Nans pr column

    na_counts = df.isnull().sum()
    print('Nans count:')
    print(na_counts)

    return df 
def test():
    print('test')

if __name__ == '__main__':
    path = 'data/raw/occurences/iNaturalist_all_Basidiomycetes.csv'

    df = cleanOccurences(path)
    print(df)

print(datetime.datetime.now())
