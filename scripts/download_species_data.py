import pandas as pd
import asyncio
import os 
import json
from zipfile import ZipFile

from pygbif import occurrences as occ

from mycoCarte.Utils import create_geometry_from_coordinates
from mycoCarte.Species import Specie

USER = 'egodin'
PWD = '4AWkTW8_4D$8q7.'
EMAIL = 'etiennegodin@duck.com'


def create_species_instances(species_list_path, count = None):

    if count:
        df_species = pd.read_csv(species_list_path, nrows=count )
    else:
        df_species = pd.read_csv(species_list_path)

    species_instances = []
    for idx, specie_name in df_species.iterrows():
        idx = idx + 1
        specie = Specie(specie_name)
        print(f'# {specie.species} {idx}/{df_species.shape[0]}')
        specie.set_index(idx)
        species_instances.append(specie)

    print('Created {} species instances'.format(len(species_instances)))
    return species_instances

def mergeAllOccurences(species_instances, output_path):
    
    print('Merging all occurences on file')
    allOcurrences_df = pd.DataFrame()
    for s in species_instances:
        print(s.occurence_file)
        try:
            ocurrences_df = pd.read_csv(s.occurence_file, delimiter = '\t')
            allOcurrences_df = pd.concat([allOcurrences_df, ocurrences_df])
        except:
            pass

    print(allOcurrences_df)
    allOcurrences_df.to_csv(output_path)
    print(f'Merged occurences saved to disk{output_path}')

def unzip_occurence_file(file_path, specie_path):

    with ZipFile(file_path, 'r') as zObject: 
        # Extracting all the members of the zip  
        # into a specific location. 
        zObject.extractall( 
            path = specie_path)
    
def skip_gbif_process(specie):

    if os.path.exists(specie.occurence_file):
        print(f'{specie.index} | {specie} occurence data already requested and downloaded to disk')
        return True
    else:
        return False
    
def construct_gbif_query_predicate(*args):

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

# --- ### Asynchronous functions ### ---

async def main(species_instances : list):

    # Check if occurence already downloaded, if so remove from list
    species_instances_to_request = []
    for specie in species_instances:
        if not skip_gbif_process(specie):
            species_instances_to_request.append(specie)

    # Set max request (imposed by gbif)
    max_concurrent_requests = 3 
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    tasks = [process_gbif_occurences(specie, semaphore) for specie in species_instances_to_request]
    await asyncio.gather(*tasks)  # Wait for all tasks to complete

    print('All occurences data on disk')
    return True

async def process_gbif_occurences(specie, semaphore, max_retries = 15, delay = 20):

    async with semaphore:

        # Create request to gbif for occurence data
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

async def gbif_occurences_request(specie):
    
    if not os.path.exists(specie.request_key_path):
            
        #Create json query to send to gbif, also writes json
        query = construct_gbif_query_predicate(specie,decimal_longitude,decimal_latitude, specie.folder )
        print(f"Starting API request for {specie} {specie.index}")
        downloadQuery = occ.download(query= query, format= 'SIMPLE_CSV', user = USER, pwd = PWD, email = EMAIL, pred_type='and')
        request_key = downloadQuery[0]
        print(f"Completed API request for {specie} {specie.index}")

        # Set request key to specie object 
        specie.set_request_key(request_key)
    
        # Write download key to disk
        with open(specie.request_key_path, mode="w", encoding="utf-8") as write_file:
                write_file.write(request_key)

        return specie.request_key
    
    elif os.path.exists(specie.request_key_path):
        print(f'{specie} occurences request already made to gbif, reading request_key from disk')

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

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(prog = 'Download species occurences from gbif',
                                     description= "Download species occurences from gbif"
                                     )
    parser.add_argument('-f', '--file', help = 'Location of species list', type = str, default = 'data/inputs/species/species_list.csv')
    parser.add_argument('-n', '--number', help = 'Number of species to query from list', type = int, default = None)

    args = parser.parse_args()
    print(f'Species list location : {args.file}')


    decimal_longitude = [-79.3439314990000071,-63.9999979090000011]
    decimal_latitude = [45.0000682390000009, 50.0000022050000013]

    species_instances = create_species_instances(args.file, args.number)

    gbif_complete = asyncio.run(main(species_instances))

    if gbif_complete:
        mergeAllOccurences(species_instances, 'data/raw/occurences/allOcurrences.csv')


