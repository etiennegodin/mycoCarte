from pygbif import species as gSpecie
import pandas as pd

# Input species list, checks gbif for species info (taxon, rank, etc)
# Save species list with infos for queryGbif.py

def create_specie_dict(queryName, rank = 'species'):
    #gbif_specie object
    try:
        print('Searching for species info for {}'.format(queryName))
        gbif_species = gSpecie.name_suggest(q=queryName, rank = rank, limit = 1)
    except:
        print('Error querying species info from gbif')
    
    #print(gbif_species)
    #Returned as list, isolate first
    gbif_specie = gbif_species[0]

    # define instance parameters
    name = gbif_specie['canonicalName']
    name = name.replace(" ", "_")

    try:
        key = gbif_specie['key']
    except:
        key = None
    try:
        taxonomic_rank = gbif_specie['rank']
    except:
        taxonomic_rank = None
    try:
        order = gbif_specie['order']
    except:
        order = None
    try:
        family = gbif_specie['family']
    except:
        family = None
    try:
        genus = gbif_specie['genus']
    except:
        genus = None

    specie = {'name' : name, 'key' : key, 'taxonomic_rank' : taxonomic_rank, 'order' : order, 'family' : family, 'genus' : genus}  
    return specie 

def create_species_list(species_file):
    species_name_list = read_species_name_list(species_file)

    species_dict_list = []
    for idx, specie_name in enumerate(species_name_list):

        specie = create_specie_dict(specie_name, rank = 'Species')

        species_dict_list.append(specie)

    return species_dict_list

def read_species_name_list(species_list_file):
    df_species = pd.read_csv(species_list_file)
    species_list = list(df_species['Species'])
    print(species_list)
    return species_list

def write_species_list(species_dict_list, output_file):
    df = pd.DataFrame(species_dict_list)
    df.to_csv(output_file, index = False)

    print('Species list written to {}'.format(output_file))
    
if __name__ == '__main__':


    species_dict_list = create_species_list('data/species/input/species.csv')
    write_species_list(species_dict_list, 'data/species/input/output/species_list.csv')