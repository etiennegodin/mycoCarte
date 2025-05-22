# Async script to query gbif occurences of species
# Input species list 

import json, os
from zipfile import ZipFile

import argparse
import asyncio
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from . import specie as sp
from .. import utils
from pygbif import occurrences as occ


gbif_queries_path = 'data/raw/gbifQueries/'

decimal_longitude = '-79.3439314990000071,-63.9999979090000011'
decimal_latitude = '45.0000682390000009, 50.0000022050000013'

# Request

# Functions
def construct_gbif_occurence_query(*args):

    #unpack certain arguments 
    specie = args[0]
    specie_path = args[3]
    

    # list to receive predicate dict
    predicate_list = []

    #Key from specie.key
    predicates_dict = {"HAS_COORDINATE" : True,
               "HAS_GEOSPATIAL_ISSUE" : False,
               "COUNTRY" : "CA", 
               "TAXON_KEY" : specie.key,
               "DECIMAL_LONGITUDE" : args[1],
               "DECIMAL_LATITUDE" : args[2]
               }
    
    for key, value in predicates_dict.items():
        predicate = { "type" : 'equals',
                     "key" : key,
                     "value" : value
                     }
        
        predicate_list.append(predicate)
    

    query = { "type": "and",
            "predicates": predicate_list
    }
    output_json_file = specie_path + specie.name + '.json'

    with open(output_json_file, mode="w", encoding="utf-8") as write_file:
        json.dump(query, write_file)
    #query = json.dumps(query)
    return query

def skip_gbif_process(specie):

    if os.path.exists(specie.occurence_file):
        print(f'{specie.index} | {specie} occurence data already requested and downloaded to disk')
        return True

    else:

        return False

def unzip_occurence_file(file_path, specie_path):

    with ZipFile(file_path, 'r') as zObject: 
        # Extracting all the members of the zip  
        # into a specific location. 
        zObject.extractall( 
            path = specie_path)
    

# Asynchronous functions 

async def gbif_occurences_request(specie):
    
    if not os.path.exists(specie.request_key_path):
            
        #Create json query to send to gbif, also writes json
        query = construct_gbif_occurence_query(specie,decimal_longitude,decimal_latitude, specie.folder )
        print(f"Starting API request for {specie} {specie.index}")
        downloadQuery = occ.download(queries= query, format= 'SIMPLE_CSV', user = 'egodin', pwd = '4AWkTW8_4D$8q7.', email = 'etiennegodin@duck.com', pred_type='and')
        request_key = downloadQuery[0]
        print(f"Completed API request for {specie} {specie.index}")

        # Set request key to specie object 
        specie.set_request_key(request_key)
    
        # Write download key to disk
        with open(specie.request_key_path, mode="w", encoding="utf-8") as write_file:
                write_file.write(request_key)

        return specie.request_key
    
    elif os.path.exists(specie.request_key_path):
        print(f'{specie} occurences request already made to gbif, ready request_key from disk')

        with open(specie.request_key_path) as write_file:
            request_key = write_file.read()

        # Set request key to specie object 
        specie.set_request_key(request_key)
        
        return specie.request_key

async def gbif_occurences_get(specie, unzip = True):
    print(f"Attempting to download data for {specie} {specie.index}")
    print(specie.request_key)
    occurences_dict = occ.download_get(specie.request_key, path = specie.folder)

    print(f"Successfully downloaded data for {specie} ({specie.index})")

         # Main command to get zip from occurence request key 
        # returns dict with some infos 
        # ex
        # {'path': 'data/raw/gbifQueries/Cantharellus enelensis//0056321-241126133413365.zip',
        #  'size': 12835,
    #  'key': '0056321-241126133413365'}

    # Option to unzip downloaded file
    if unzip == True:

        print('Unziping file')
        zip_file_path = occurences_dict['path']
        #Unzip file
        unzip_occurence_file(zip_file_path, specie.folder )

        csv_to_rename_path = specie.folder + "{}.csv".format(specie.request_key)
        renamed_file_path = specie.folder + "{}.csv".format(specie.name)

        # Rename file from key.csv to specie's name for better readability
        os.rename(csv_to_rename_path,renamed_file_path)
        print(renamed_file_path)
        return renamed_file_path
    else:
        print('Downloaded zip file to {}'.format(occurences_dict['path']))
        return (occurences_dict['path'])

async def process_gbif_occurences(specie, semaphore, max_retries = 15, delay = 20):

    async with semaphore:
        # Set 
        await gbif_occurences_request(specie)

        retries = 0 
        while retries < max_retries:
            try:
                await gbif_occurences_get(specie)
                print(f'Took {retries}')
                break  # Exit loop if download is successful

            except:
                print(f"Retry {retries + 1}/{max_retries} for {specie} {specie.index}")
                retries += 1
                await asyncio.sleep(delay) 
        else:
            print(f"Failed to download data for {specie} after {max_retries} retries.")

    pass

async def main(species_instances):

    # Check if occurence already downloaded, if so remove from list
    filtered_species_instances = []

    for specie in species_instances:
        if not skip_gbif_process(specie):
            filtered_species_instances.append(specie)


    max_concurrent_requests = 3 
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    tasks = [process_gbif_occurences(specie, semaphore) for specie in filtered_species_instances]
    await asyncio.gather(*tasks)  # Wait for all tasks to complete

    print('All occurences data on disk')
    return True



if __name__ == '__main__':


    import argparse
    parser = argparse.ArgumentParser(prog = 'Geo data procesing',
                                     description= "Assigns environmental variables to specie's occurences"
                                     )
    parser.add_argument('-f', '--file', help = 'Location of species list', type = str, default = 'data/input/table/species_list.csv')
    parser.add_argument('-l', '--length', help = 'Number of species to request from list', type = int, default = 5 )
    parser.add_argument('--range', help = 'Specify species_list range to load ', default = None )       
     
    args = parser.parse_args()

    # Interpret arguments
    if args.range != None:
        print('Using range')
        species_list_range = utils.interpret_args_range(args.range) 
    else: 
        species_list_range = None

    print(f'Species list location : {args.file}')

    print(f'Requesting {args.length} species')
    species_instances = sp.create_species_instances(species_file= args.file,length = args.length, species_list_range = species_list_range)
    
    gbif_complete = asyncio.run(main(species_instances))

   