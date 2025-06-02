import os
import geopandas as gpd
import pandas as pd
import itertools
import numpy as np
import gc

from mycoCarte import Utils
from mycoCarte import geoUtils


cell_agg_dict = { 'ty_couv_et': lambda x : x.mode()[0] if not x.mode().empty else np.nan,
                        'cl_dens' : lambda x : x.mode()[0] if not x.mode().empty else np.nan,
                        'cl_haut' : lambda x : x.mode()[0] if not x.mode().empty else np.nan,
                        'cl_age_et' : 'mean',
                        'etagement' : lambda x : x.mode()[0] if not x.mode().empty else np.nan,
                        'cl_pent' : lambda x : x.mode()[0] if not x.mode().empty else np.nan,
                        'hauteur' : 'mean',
                        'dep_sur' : lambda x : x.mode()[0] if not x.mode().empty else np.nan,
                        'cl_drai' : lambda x : x.mode()[0] if not x.mode().empty else np.nan,
                        'tree_cover' : lambda dicts : len(set(itertools.chain.from_iterable(d.keys() for d in dicts))),
                        'tree_shannon_index' : 'mean'
}

def aggregate(encoded_foretOuvert_gdf: gpd.GeoDataFrame, 
                            perimeter_gdf: gpd.GeoDataFrame,
                            grid: gpd.GeoDataFrame,
                            region : str,
                            subset_output_path : str,
                            verbose = False):
    print(f'#{__name__}.aggregateForetOuverte')
    print(f'Aggregating data for {region}')

    #Convert all to WSG84
    grid = grid.to_crs(4326)
    foretOuverte_gdf = encoded_foretOuvert_gdf.to_crs(4326)
    perimeter_gdf = perimeter_gdf.to_crs(4326)

    #Check if main gdf loaded correctly 
    print(foretOuverte_gdf.head())

    # Clip full grid by perimeter 
    clipped_grid = geoUtils.clip_grid_per_region(perimeter_gdf,grid, debug= False, keep_cols= ['FID', 'geometry', 'block_id'])

    # Foret ouvert gdf spatial join with clipped grid 
    # Assign each vector shape of foret ouverte a value of grid id 
    joined_gdf = gpd.sjoin(foretOuverte_gdf, clipped_grid, how ='inner', predicate= 'intersects')
    joined_gdf = joined_gdf.drop(['index_right'], axis = 1)
    
    #Aggregate field values grouped by cell id based on dict 
    try:
        aggregated_gdf = joined_gdf.groupby('FID').agg(cell_agg_dict).reset_index()
        #Performed tree richness based on tree cover column, rename 
        aggregated_gdf = aggregated_gdf.rename(columns= {'tree_cover' : 'tree_diver' })
    except Exception as e:
        print(e)

    result_gdf = clipped_grid.merge(aggregated_gdf, on = 'FID',how = 'left')

    #export as csv
    output_csv = subset_output_path
    df = Utils.gdf_to_df(result_gdf)
    try:
        df.to_csv(output_csv, index = False)
    except Exception as e:
        print("Failed to export csv")
        print(e)

    #Delete after saved 
    del result_gdf
    del df
    gc.collect()

    return output_csv


def mergeAllDataset(grid: gpd.GeoDataFrame, gdfs :list, output_path: str = None, write =True):
    print(f'#{__name__}.mergeAllDataset')

    shp_output_path = output_path + 'foretOuvertePreprocessed.shp'
    csv_output_path = output_path + 'foretOuvertePreprocessed.csv'

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


    # Removing all grid cells without value
    # (Mainly explained from grid covering whole area and foretOuverte data only in forested areas and in Qc boundaries )
    # 'cl_dens' used as 
    final_gdf = final_gdf.dropna(subset = ['cl_age_et'])
    print(final_gdf.shape)

    if write and output_path:
        final_gdf.to_file(shp_output_path, driver='ESRI Shapefile')
        print(f"# Exported {shp_output_path} ")
        final_gdf.to_csv(csv_output_path)
        print(f"# Exported {csv_output_path} ")

    return final_gdf