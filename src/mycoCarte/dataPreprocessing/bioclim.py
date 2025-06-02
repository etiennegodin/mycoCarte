import pandas as pd
import geopandas as gpd
import os 

output_path = 'data/interim/geodata/vector/bioclim/preprocessedBioclim.csv'
raw_bioclim = '/home/egodin/Documents/projects/mycoCarte/data/raw/sampledBioclim/0.5km_bioclim.shp'

def preprocessData(overwrite = False):
    print(f'#{__name__}.preprocessData')
    run = False

    if os.path.isfile(output_path):
        if overwrite:
            run = True
    else:
        run = True

    if run:
    # Remove cold related bioclims, remove months and keep only quarter bioclims to remove multicollinearity
    # See jupyter notebook

        col_remove = ['bioclim_06',
                'bioclim_07',
                'bioclim_11',
                'bioclim_13',
                'bioclim_14',
                'bioclim_19']
        

        gdf = gpd.read_file(raw_bioclim)
        gdf.drop(col_remove, axis = 1, inplace= True)

        df = gdf.drop('geometry', axis = 1)
        
        print(df.head())
        df.to_csv(output_path)

    else:
        df = pd.read_csv(output_path)
        
    return df


if __name__ == '__main__':
    preprocessData()
