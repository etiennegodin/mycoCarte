import geopandas as gpd 
import os
import numpy as np

from sklearn.cluster import KMeans
CLUSTERED_GRID_OUTPUT_PATH = 'data/interim/geodata/vector/geoUtils/clustered_0.5km_grid.shp'
GRID_PATH = 'data/interim/geodata/vector/geoUtils/0.5km_grid.shp'

def readGrid(overwrite = False):
    print(f'#{__name__}.readGrid')

    grid  = clusterGrid(GRID_PATH, overwrite = overwrite)
    print('Reading grid file')

    return grid

def clusterGrid(grid_path = GRID_PATH, clusters = 5, overwrite = False):
    print(f'#{__name__}.clusterGrid')

    def main(grid_path,clusters):

        # load grid
        grid = gpd.read_file(grid_path)
        grid = grid.to_crs(4326)
        centroids = grid.geometry.centroid

        coords = np.vstack([centroids.x, centroids.y]).T

        k = clusters
        kmeans = KMeans(n_clusters=k, random_state=42).fit(coords)
        grid['block_id'] = kmeans.labels_

        grid.to_file(CLUSTERED_GRID_OUTPUT_PATH, driver='ESRI Shapefile')
        print(f'Exported {CLUSTERED_GRID_OUTPUT_PATH}'
              )
        return grid 
    
    if os.path.isfile(CLUSTERED_GRID_OUTPUT_PATH):
        print(f'Grid already clustered')
        if overwrite:
            print('Overwritting')
            grid = main(grid_path,clusters)
        else:
            grid = gpd.read_file(CLUSTERED_GRID_OUTPUT_PATH)

    else:
        grid = main(grid_path,clusters)

    return grid

def clip_grid_per_region(perimeter_gdf, grid, debug = False, keep_cols = False):

    if debug:
        print('-'*100)
        print('Grid gdf')
        print(grid.head())

        print('-'*100)
        print('Perimeter gdf')
        print(perimeter_gdf.head())

    #Keep only geometry 
    perimeter_gdf = perimeter_gdf[['geometry']]

    #reproject to WSG84
    gdf_l = grid.to_crs(4326)
    gdf_r = perimeter_gdf.to_crs(4326)
        
    # clip operation
    try:
        clipped_grid = gpd.sjoin(gdf_l,gdf_r, how ='inner')
    except Exception as e:
        print(e)

    if not clipped_grid.empty:
        clipped_grid = clipped_grid.drop(['index_right'], axis = 1)
    
    if not keep_cols:
        try:
            clipped_grid = clipped_grid[['FID','geometry']]
        except Exception as e:
            print(e)
    else:
        if isinstance(keep_cols, list):
            try:
                clipped_grid = clipped_grid[keep_cols]
            except Exception as e:
                print(e)   

    if debug:
        print('-'*100)
        print('Clipped gdf')
        print(clipped_grid.head())

    if not clipped_grid.empty:
        return clipped_grid