from mycoCarte import Utils, geoUtils
from mycoCarte.dataPreprocessing.foretOuverte import unpackGpkg, encoder, gridAggregate

def combineAllSubsets(dir_path : str):
    import pandas as pd 
    import os 

    print(f'#{__name__}.combineAllSubsets')
    subsets_list = os.listdir(dir_path)
    df = pd.DataFrame()

    for i, subset in enumerate(subsets_list):
        print(f'Combining {subset} ({i+1}/{len(subsets_list)})')
        df_temp = pd.read_csv(dir_path + subset, low_memory= False)
        df = pd.concat([df,df_temp])
    
    print('#Combined all subsets#')

    return df


def preprocessData():


    grid = geoUtils.readGrid()
    regions_list = Utils.get_regionCodeList()

    preprocessed_dfs = []
    for region in regions_list:

        gdf, perimeter_gdf = unpackGpkg.main(region)
        encoded_gdf = encoder.encode(gdf, region, verbose = True)
        aggregated_gdf = gridAggregate.aggregate(encoded_gdf, perimeter_gdf, grid, region)

