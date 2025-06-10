import os 
import pandas as pd
import geopandas as gpd
from mycoCarte import Utils
from numpy import NaN
import numpy as np
import itertools

def cleanOccurencesData(csv_occurences_path,cleaned_occurences_path, overwrite = False ):
    """
    Input : Takes in a csv path of occurences, reads and cleans it
    Output: path
    """

    print(f'#{__name__}.cleanOccurencesData')

    def process():
        # read csv
        df = pd.read_csv(csv_occurences_path, index_col= 0)
        print(df.shape[0])

        # keep only canada & quebec
        df = df[df.countryCode == 'CA']
        df = df[df.stateProvince == 'Québec']
        print(df.shape[0])

        # remove occurences with same latLong values (preserved specimens from older sources)
        df = df.drop_duplicates(subset=['decimalLatitude'], keep = 'last')
        df = df.drop_duplicates(subset=['decimalLongitude'],keep = 'last')
        print(df.shape[0])

        # remove before 2000
        df = df[df.year >= 2000]
        print(df.shape[0])

        # Remove points where coordinateUncertaintyInMeters is over 500
        df = df[df.coordinateUncertaintyInMeters <= 500]
        print(df.shape[0])

        

        df.to_csv(cleaned_occurences_path, index = False)
        print('Writting cleaned occurences to:')
        print(cleaned_occurences_path)

        return cleaned_occurences_path

    if os.path.isfile(cleaned_occurences_path):
        print(f'Cleaned occurences already on file')
        if overwrite:
            print('Overwritting')
            output = process()
        else:
            # Written, not overriding, just reading it back to create dict and df 
            output = cleaned_occurences_path
    else:
        output = process
    
    return output

def spatialJoin(cleaned_occurences_path, grid_path, sjoin_occurence_path, overwrite = False):
    print(f'#{__name__}.spatialJoin')
    
    def process():
        # load grid 
        grid = gpd.read_file(grid_path)

        #load occurences
        df = pd.read_csv(cleaned_occurences_path, index_col= 0)
        gdf = Utils.df_to_gdf(df, xy = ['decimalLongitude','decimalLatitude'])
        #spatial join
        joined_gdf = gpd.sjoin(gdf, grid, how ='inner', predicate= 'intersects')
        joined_gdf = joined_gdf.drop(['index_right'], axis = 1)

        df = Utils.gdf_to_df(joined_gdf)
        df.to_csv(sjoin_occurence_path, index  = False)
        return df 

    def read():
        df = pd.read_csv(sjoin_occurence_path)
        return df 
    
    if os.path.isfile(sjoin_occurence_path):
        if overwrite:
            print('Occurences already spatialy joined, ### overwritting ###')
            df = process()
        else:
            print('Occurences already spatialy joined, reading')
            df = read()
    else:
        print('Occurences not spatialy joined, processing')
        df = process()

    return df 

def biasFilter(occ_df, bias_df):
    print(f'#{__name__}.biasFilter')

    try:
        temp_df = occ_df.merge(bias_df, on = 'FID',how = 'left')
    except Exception as e:
        print('Failed to merge foretOuverte_df data')
        print(e)

    print('Occurences size before bias filter')
    print(occ_df.shape[0])
    temp_df = temp_df[temp_df.urbanArea != 1]

    #Keep only rows of original df from filtered temp_df
    common_idx = occ_df.index.intersection(temp_df.index)
    occ_df = occ_df.loc[common_idx]

    print('Occurences size after bias filter')
    print(occ_df.shape[0])
    return occ_df
    
def process_fungi_ecology_index(occurences_df):
    print(f'#{__name__}.process_fungi_ecology_index')

    #aggregate field values grouped by cell id 
    try:
        richness_df = occurences_df.groupby('FID')['species'].nunique().reset_index(name='fungi_richness')
        shannon_df = occurences_df.groupby('FID')['species'].agg(Utils.shannonIndex).reset_index(name='fungi_shannon')
    except Exception as e:
            print(e)

    result_df = richness_df.merge(shannon_df, on = 'FID',how = 'left')

    return result_df

def spatial_aggregate(occurences_df: pd.DataFrame):
    print(f'#{__name__}.spatial_aggregate')

    #Keeping only spatially relevant / aggregate-able rows 
    rows = ['kingdom','phylum','class','order','family','genus','species','eventDate','day','month','year','FID']
    rows = ['FID']

    reduced_df = occurences_df[rows]

    ecology_index_df = process_fungi_ecology_index(occurences_df)

    #Aggregate field values grouped by cell id based on dict 
    try:
        aggregated_df = reduced_df.groupby('FID').agg(lambda x : x.mode()[0] if not x.mode().empty else np.nan).reset_index()
        #Performed tree richness based on tree cover column, rename 
    except Exception as e:
        print(e)

    result_df = aggregated_df.merge(ecology_index_df, on = 'FID',how = 'left')

    print(f'Aggregated occurences df shape = {result_df.shape}')
    return result_df

def preprocessData(overwrite = False):
    print(f'#{__name__}.preprocessData')

    cleaned_occurences_path = cleanOccurencesData('data/raw/occurences/allOcurrences.csv',
                                                   'data/interim/occurences/filteredOcurrences.csv',
                                                     overwrite= overwrite)
    df = spatialJoin(cleaned_occurences_path,
                'data/interim/geodata/vector/geoUtils/0.5km_grid.shp',
                'data/interim/occurences/griddedOccurences.csv',
                overwrite= overwrite)
    
    print(f'Occurences df shape = {df.shape}')

    # Remove columns with Nans 
    df = df.dropna(axis = 1)

    return df
    

if __name__ == '__main__':
    preprocessData(overwrite = True)