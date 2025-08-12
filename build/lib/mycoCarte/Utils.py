import pandas as pd
import geopandas as gpd
import numpy as np
import os, ast, glob, pprint
from zipfile import ZipFile

def create_geometry_from_coordinates(lats, longs):
    """Returns a wkt polygon from lat_long coordinates

    lat_longs -- List of tuples
    """

    coords = [
        (longs[0], lats[0]),
        (longs[1], lats[0]),
        (longs[1], lats[1]),
        (longs[0], lats[1]),
        (longs[0], lats[0])
    ]


    from shapely import Polygon
    wkt = Polygon(coords).wkt

    return wkt


def create_folder(path):

    if not os.path.exists(path):
        print('Requested folder do not exists, creating:')
        os.makedirs(path)
        print(path)

        return path
    else:
        return path
    
def unzip_file(input_path, output_path, verbose = True):

    with ZipFile(input_path, 'r') as zObject: 
        # Extracting all the members of the zip  
        # into a specific location. 
        zObject.extractall( 
            path = output_path)
        
        if verbose:
            print(f'Unziped file {output_path}')

def mergeDfFromCsv(file1,file2,collumn = 'geoc_maj'):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Merge the DataFrames based on the common column "ID"
    merged_df = pd.merge(df1, df2, on='geoc_maj')

    return merged_df

def saveDfToCsv(df, output_path):
    # Save the merged DataFrame to a new CSV file
    print('Saving {}'.format(output_path))
    
    df.to_csv(output_path, index=False)

def pdToCsv(df, speciesFolder, filename = "occ.csv" ):
    outputpath = speciesFolder + filename 
    try:
        df.to_csv(outputpath)
        print('Writting pd as csv')
        print('{}'.format(outputpath))
    except:
        print(f'Error saving {outputpath}')
    return outputpath

def csvToPandas(csv):
    df = pd.read_csv(csv, index_col = 0)
    return(df)

def regions_folders(parent_folder_path):

    regions_codes = [ '21E', '21L', '21M', '21N','21O', 
                     '22A', '22B', '22C', '22G', '22H',
                     '31F', '31G', '31H', '31I', '31J', '31K','31L'
    ]

    for code in regions_codes:
        os.makedirs(parent_folder_path + code)

def convert_string_to_numeral(df, collumn = 'tree_cover'):
    df[collumn] = df[collumn].apply(ast.literal_eval)
    
    return df

def random_number_generator(count, min, max):
    max = max + 1

    if count > 0:
    # Generate random numbers between 30 and 50 that sum to 'count'

        random_values = np.random.randint(min, max, size=count)
        # Shuffle the random values for randomness
        np.random.shuffle(random_values)

        

    return random_values 
        # Example: Adding the mapping back to DataFrame (Optional)

def explore_df(df, describe = True, dtype = False, corr = False):

    df.shape
    if describe:
        print(df.describe())
    if dtype:
        print(df.dtypes)

    if corr:
        numeric_df = df.select_dtypes(include=['float64', 'int64', 'int32'])
        print(numeric_df.corr())

def delete_files_with_suffix(parent_folder, suffix, length, dry_run = True):
    """
    Delete all files that end with a specified suffix in the parent folder and its subdirectories.

    Parameters:
    - parent_folder: The path to the parent folder to search in.
    - suffix: The suffix the target files should end with (e.g., '.txt').
    """
    # Recursively search for files ending with the specified suffix
    pattern = os.path.join(parent_folder, "**", "*"+suffix)
    files_to_delete = glob.glob(pattern, recursive=True)
    # Delete each file found
    if dry_run:
        pprint.pprint(files_to_delete)
    elif not dry_run:
        files_to_delete = files_to_delete[:length]
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

def merge_raw_geodata():

    # Merge two datasets in one 

    # Merge region based geodata from 2 different datasets
    # CARTE ECO_MAJ + 

    env_factors_path = 'data/raw/region_env_factors/CARTE_ECO_MAJ_'
    region_data_path = 'data/raw/regions_data'

    regions_list = os.listdir('data/raw/regions_data')

    output_path = 'data/input/geodata/forest_composition'
    regions_data_cols = ['geoc_maj', #id
                    'cl_pent', # classe de pente
                    'dep_sur',# depot surface
                    'cl_age', # classe d'age 
                    'cl_drai', # classe drainage
                    'cl_haut', # classe hauteur
                    'type_couv', #ype couvert
                    'origine', # Perturbation d'origine
                    'an_origine', # annee pertrubation
                    'perturb', # Perturbation partielle
                    'an_perturb', # Année de la perturbation partielle
                    'X',
                    'Y']

    env_factors_cols = ['geoc_maj',
                        'ty_couv_et',
                        'densite',
                        'cl_age_et',
                        'tree_cover',
                        'hauteur',
                        ]

    for region in regions_list:

        regions_data_df = pd.read_csv(f'{region_data_path}/{region}/{region}.csv', usecols= regions_data_cols)

        env_factors_df = pd.read_csv(f'{env_factors_path}{region}.csv', usecols= env_factors_cols)

        merged_df = pd.merge(regions_data_df, env_factors_df, on='geoc_maj')

        saveDfToCsv(merged_df, f'{output_path}/{region}.csv')

        print(merged_df.head())


def interpret_args_range(input_range):

    split = input_range.split('-',1)

    if len(split) != 2:
        print('Range entered incorrectly, please use "min-max" syntax')  
    else:  
        try:
            min = int(split[0])-1
            max = int(split[-1])
        except ValueError as e:
            print('Please enter range as min-max using a dash to separate')
            min = None
            max = None

        output_range = [min,max]
        print(output_range)    
        return output_range
    
def shannonIndex(group):
    counts = group.value_counts()
    proportions = counts / counts.sum()
    return -np.sum(proportions * np.log(proportions))


def get_regionCodeList(range = (0,17), verbose = False):

    regionCodes = 'data/inputs/qc_regions.csv'

    regionCodeList = []
    regionCodeDict = pd.read_csv(regionCodes).to_dict()
    
    regionCodeDict = regionCodeDict['region']

    for i,(key, region) in enumerate(regionCodeDict.items()):
        regionCodeList.append(region)

    regionCodeList = regionCodeList[range[0]:range[1]]
    if verbose:
        print(regionCodeList)
    return regionCodeList


def df_to_gdf(df:pd.DataFrame,
               xy: list = ['decimalLongitude','decimalLatitude']):

    # Creates goepandas from dataframe with lat/long columns
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df[xy[0]], df[xy[1]]), crs="EPSG:4326"
    )
    return gdf

def gdf_to_df(gdf):
    df = pd.DataFrame(gdf.drop(columns='geometry'))
    return df


def unpackGPK(inputfile = '', output_file = ''):
    pass

if __name__ == '__main__':
    # Specify the parent folder and file suffix
    parent_folder = 'data/gbifQueries'  # Replace with your parent folder path
    suffix = "geodata.csv"  

    #delete_files_with_suffix(parent_folder, suffix, length = 400, dry_run = False)


def encodeBioclim(df):

    biolcimEncodingDict = { 'bioclim_01' : 'Annual Mean Temp',
                            'bioclim_02' : 'Mean Diurnal Range',
                            'bioclim_03' : 'Isothermality',
                            'bioclim_04' : 'Temp Seasonality',
                            'bioclim_05' : 'Max Temp of Warmest Month',
                            'bioclim_06' : 'Min Temp of Coldest Month',
                            'bioclim_07' : 'Temp Annual Range',
                            'bioclim_08' : 'Mean Temp of Wettest Quarter',
                            'bioclim_09' : 'Mean Temp of Driest Quarter',
                            'bioclim_10' : 'Mean Temp of Warmest Quarter',
                            'bioclim_11' : 'Mean Temp of Coldest Quarter',
                            'bioclim_12' : 'Annual Precip',
                            'bioclim_13' : 'Precip of Wettest Month',
                            'bioclim_14' : 'Precip of Driest Month',
                            'bioclim_15' : 'Precip Seasonality',
                            'bioclim_16' : 'Precip of Wettest Quarter',
                            'bioclim_17' : 'Precip of Driest Quarter',
                            'bioclim_18' : 'Precip of Warmest Quarter',
                            'bioclim_19' : 'Precip of Coldest Quarter'
                        }
    

    df = df.rename(columns = biolcimEncodingDict)
    return df

