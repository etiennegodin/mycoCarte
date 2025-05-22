import geopandas as gpd 

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