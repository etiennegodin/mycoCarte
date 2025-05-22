import pandas as pd
from mycoMap import utils 
# Species class based on gbif 
class Specie:
    def __init__(self, name, key, taxonomic_rank, order, family, genus):
        
        name = name.replace(" ", "_")
        self.name = name 
        self.key = key 
        self.taxonomic_rank = str.lower(taxonomic_rank)
        self.order = order
        self.family = family
        self.genus = genus

        # From prepare_species_gbif funct 
        self.folder = 'data/raw/gbifQueries/' + name + '/'
        # Create folder for specie data, if already created returns path 
        utils.create_folder(self.folder)

        #Set expected file for occurence data 
        self.occurence_file = self.folder + name + '.csv'

        #Set expected file for request key 
        self.request_key_path = self.folder + name + '_request_key.txt'

        #Set expected file for occurences geodata  
        self.geodata_file = self.folder + name + '_geodata.csv'

        print(" # Created specie object for {}".format(name))

    def set_request_key(self,key):
        self.request_key = key
    
    def set_index(self,idx):
        self.index = idx
      
    def __str__(self):
        return self.name

def create_specieObject(specie_row, rank = 'species'):

    # define instance parameters
    name = specie_row['name']

    try:
        key = specie_row['key']
    except:
        key = None
    try:
        taxonomic_rank = specie_row['taxonomic_rank']
    except:
        taxonomic_rank = None
    try:
        order = specie_row['order']
    except:
        order = None
    try:
        family = specie_row['family']
    except:
        family = None
    try:
        genus = specie_row['genus']
    except:
        genus = None
    print('x' * 50)
    print(name,key,taxonomic_rank, order, family, genus)
    # Create instance of specie with info 
    specie = Specie(name,key,taxonomic_rank, order, family, genus)
    return specie 

def create_species_instances(species_file, length = None, species_list_range = None):

    if species_list_range != None:
        df_species = create_species_list_df(species_file, species_list_range)
    elif length != None:
        species_list_range = [0,length]
        df_species = create_species_list_df(species_file, species_list_range)
    else:
        df_species = create_species_list_df(species_file)

    species_instances = []
    for idx, specie_row in df_species.iterrows():

        specie = create_specieObject(specie_row, rank = 'Species')
        print(' ############################## {} ############################## {}'.format(specie.name, idx))

        specie.set_index(idx)
        species_instances.append(specie)

    print('Created {} species instances'.format(len(species_instances)))
    return species_instances

def create_species_list_df(species_list_file, species_list_range = None):

    df_species = pd.read_csv(species_list_file)

    if species_list_range != None:
        min = species_list_range[0]
        max = species_list_range[1]

        df_species = df_species.iloc[min:max]

    return df_species
