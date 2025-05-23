import geopandas as gpd
import pandas as pd 
import os 
import fiona
from mycoCarte import Utils

# Global vars 
ordinal_columns = ['ty_couv_et','cl_dens','cl_haut','cl_age_et','etagement','cl_pent','hauteur']
categorical_columns = ['dep_sur','cl_drai', 'eta_ess_pc']
gdf_columns = ['geoc_maj', 'geometry']
all_columns = ordinal_columns + categorical_columns + gdf_columns

INPUT_GPKG_PATH = 'data/raw/geodata/foretOuverte/PEE_MAJ_PROV/gpkg'
OUPTUT_SHP_PATH = 'data/interim/geodata/vector/mergedGpkg'

def combine_gpkg_layers(gpkg_file, layers, verbose = False):
    
    gdf_combined = gpd.GeoDataFrame()
    largest_layer_features = 0

    for layer in layers:
        # --- Read the GeoPackage Layer ---
        try:
            print(f"Reading layer '{layer if layer else 'default'}' from GeoPackage: {gpkg_file}...")
            layer_gdf = gpd.read_file(gpkg_file, layer=layer)
            if len(layer_gdf) > largest_layer_features:
                largest_layer_features = len(layer_gdf) 
            if verbose:
                print(f"Read {len(layer_gdf)} features.")
            feature_count_diff = largest_layer_features - len(layer_gdf)
            if verbose:
                print(f"Read {len(layer_gdf)} features.")
                print(f'{feature_count_diff} features less than largest layers ')
            #print(layer_gdf.head())

            if gdf_combined.empty:
                gdf_combined = layer_gdf
                pass
            else:
                try:
                    gdf_combined = gdf_combined.merge(layer_gdf, on = 'geoc_maj')
                    print(f'Combined {layer}')
                except Exception as e:
                    print(f"Error merging GeoPackage file: {e}")
                    exit() # Exit if reading fails

        except Exception as e:
            print(f"Error reading GeoPackage file: {e}")
            print("Please check the file path and ensure the layer name (if specified) is correct.")
            exit() # Exit if reading fails

    return gdf_combined

def find_gpkg_layers(input_gpkg_path = INPUT_GPKG_PATH):
        
    layer_name = None

    try:
        print(f"Layers available in '{input_gpkg_path}':")
        layers = list(fiona.listlayers(input_gpkg_path))
        print(layers)
        return layers 
    except Exception as e:
        print(f"Could not list layers (maybe file doesn't exist?): {e}")
        # Decide if you want to exit or continue assuming the default layer

        # exit()
        
def write_gdf(gdf, output_path):

    # --- Write to Shapefile ---
    try:
        print(f"Writing GeoDataFrame to Shapefile: {output_path}...")
        # The driver is usually inferred from the extension,
        # but specifying it is robust.
        gdf.to_file(output_path, driver='ESRI Shapefile')
        print("Conversion successful!")

    except Exception as e:
        print(f"Error writing Shapefile: {e}")
        # Common Shapefile errors relate to long field names or mixed geometry typ


def filter_gdf(gdf, filters = None):

    condition = (gdf['type_ter'] == 'TRF') & (gdf['co_ter'].isna())
    filtered_gdf = gdf[condition]

    return filtered_gdf

def merge_region_gpkg(region, main_layers = True, perimeter_layer = True, write = False, verbose = False):

    gpkg_file = INPUT_GPKG_PATH + f'/CARTE_ECO_MAJ_{region}.gpkg'

    layers = find_gpkg_layers(gpkg_file)

    #layers_to_combine = [layers[1], layers[3], layers[4]]
    layers_to_combine = [layers[1], layers[4]]
    #layers_to_combine = [layers[1]]

    gdf_combined = combine_gpkg_layers(gpkg_file, layers = layers_to_combine)

    filtered_gf = filter_gdf(gdf_combined)
    
    #quick clean if duplicates
    filtered_gf = filtered_gf.drop_duplicates()
    
    perimeter_gdf = combine_gpkg_layers(gpkg_file, layers = [layers[0]])
    if verbose:
        print(filtered_gf)

    if write:
        output_path = OUPTUT_SHP_PATH + f'{region}_raw_merge.shp'
        filtered_gf.to_file(output_path, driver='ESRI Shapefile')
        write_gdf(filtered_gf, output_path)
    
    if write:
        perimeter_output_path = 'data/interim/geodata/vector/region_perimeter/' + f'{region}_perimeter.shp'
        perimeter_gdf.to_file(perimeter_output_path, driver='ESRI Shapefile')

    return filtered_gf, perimeter_gdf

def importForetOuvertLayers(region, overwrite = False, verbose = False):
    print(f'##{__name__}.importForetOuvertLayers')
    #Expected paths 
    output_path = OUPTUT_SHP_PATH + f'{region}_raw_merge.shp'
    perimeter_output_path = 'data/interim/geodata/vector/region_perimeter/' + f'{region}_perimeter.shp'


    if os.path.isfile(output_path):
        if overwrite:
            print(f'{region} gpkg extracted, ### overwriting ###')
            filtered_gf, perimeter_gdf = merge_region_gpkg(region, write = True)
        else:
            print(f'{region} gpkg already extracted reading file ')
            filtered_gf, perimeter_gdf = readExtractedLayersOnDisk(output_path, perimeter_output_path)

    else:
        print(f'{region} gpkg not extracted running extraction')
        filtered_gf, perimeter_gdf = merge_region_gpkg(region, write = True)

    return filtered_gf, perimeter_gdf

def readExtractedLayersOnDisk(output_path, perimeter_output_path):
    filtered_gf = gpd.read_file(output_path)
    perimeter_gdf = gpd.read_file(perimeter_output_path)

    return filtered_gf, perimeter_gdf


def main(region, overwrite = False, verbose = False):
    """
    Input : Takes in a region subsets, reads and cleans it
    
    Output: Cleaned gdf, region perimeter gdf
    """
    print(f'#{__name__}.cleanForetOuverteData')

    gdf, perimeter_gdf = importForetOuvertLayers(region, overwrite = overwrite, verbose = verbose )
    #keep only relevant columns
    gdf = gdf[all_columns]

    return (gdf, perimeter_gdf)
