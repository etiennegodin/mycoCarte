import geopandas as gpd

def mergeAllDataset(grid: gpd.GeoDataFrame, gdfs :list, output_path: str = None, write =True):
    print(f'#{__name__}.mergeAllDataset')

    shp_output_path = output_path + 'preprocessedData.shp'
    csv_output_path = output_path + 'preprocessedData.csv'

    final_gdf = grid

    for i, gdf in enumerate(gdfs):
        # Removing geometry columns in data to merge 
        if 'geometry' in gdf.columns:
            try:
                gdf.drop(['geometry'], axis = 1, inplace = True)
            except Exception as e:
                print('Failed to remove geometry column')

        # Removing block id from clusterng in columns in data to merge 
        if 'block_id' in gdf.columns:
            try:
                gdf.drop(['block_id'], axis = 1, inplace = True)
            except Exception as e:
                print('Failed to remove block_id column')

        # Merge data in final gdf 
        try:
            final_gdf = final_gdf.merge(gdf, on = 'FID',how = 'left')
        except Exception as e:
            print('Failed to merge data')
            print(e)

    print(final_gdf.shape)
    print('#'*100)

