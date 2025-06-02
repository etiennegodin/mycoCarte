import os
import pandas as pd
from mycoCarte import Utils, geoUtils
from mycoCarte.dataPreprocessing.foretOuverte import unpackGpkg, encoder, gridAggregate

preprocessed_path = 'data/interim/geodata/vector/foretOuvertePreprocessed/foretOuvertePreprocessed.csv'
region_subset_dir = 'data/interim/geodata/vector/sampled_grid/csv/'

def combineAllSubsets(dir_path : str):

    print(f'#{__name__}.combineAllSubsets')
    subsets_list = os.listdir(dir_path)
    df = pd.DataFrame()

    for i, subset in enumerate(subsets_list):
        print(f'Combining {subset} ({i+1}/{len(subsets_list)})')
        df_temp = pd.read_csv(dir_path + subset, low_memory= False)
        df = pd.concat([df,df_temp])
    
    print('#Combined all subsets#')

    return df

def subset_processing(overwrite = False):
    print(f'#{__name__}.subset_processing')

    grid = geoUtils.readGrid()
    regions_list = Utils.get_regionCodeList()
    preprocessed_dfs = []

    for region in regions_list:
        region_subset_path = region_subset_dir + f'{region}_grid.csv'
        run = False 

        if os.path.isfile(region_subset_path):
            if overwrite:
                run = True
        else:
            run = True
        
        if run:
            gdf, perimeter_gdf = unpackGpkg.main(region)
            encoded_gdf = encoder.encode(gdf, region, verbose = True)
            output_csv = gridAggregate.aggregate(encoded_gdf, perimeter_gdf, grid, region, region_subset_path)
            preprocessed_dfs.append(output_csv)
        else:
            preprocessed_dfs.append(region_subset_path)


    if len(preprocessed_dfs) == len(regions_list):
        combined_df = combineAllSubsets('data/interim/geodata/vector/sampled_grid/csv/')
        combined_df.to_csv('data/interim/geodata/vector/foretOuvertePreprocessed/foretOuvertePreprocessed.csv')
    return combined_df

def preprocessData(overwrite = False):
    print(f'#{__name__}.preprocessData')
    run = False

    if os.path.isfile(preprocessed_path):
        if overwrite:
            run = True
    else:
        run = True

    if run: 
        combined_df = subset_processing(overwrite = overwrite)
    else:
        combined_df = pd.read_csv(preprocessed_path)

    return combined_df

    