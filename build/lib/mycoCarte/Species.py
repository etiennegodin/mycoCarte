from pygbif import species as sp
from mycoCarte import Utils
# Species class based on gbif 
class Specie:
    def __init__(self, specie_name):
        self._specie_name = specie_name
        self.getGbifSpeciesInfo(specie_name)
        self.name_underscored = self.species.replace(' ', '_')
        self.prepare_gbif_query()

    def prepare_gbif_query(self):
            
        # From prepare_species_gbif funct 
        self.folder = 'data/raw/gbifQueries/' + self.name_underscored + '/'
        # Create folder for specie data, if already created returns path 
        Utils.create_folder(self.folder)

        #Set expected file for occurence data 
        self.occurence_file = self.folder + self.name_underscored + '.csv'

        #Set expected file for request key 
        self.request_key_path = self.folder + self.name_underscored + '_request_key.txt'

        #Set expected file for occurences geodata  
        self.geodata_file = self.folder + self.name_underscored + '_geodata.csv'

        print(" # Created folder structure and paths as object arguments as for {}".format(self.species))
    
    def getGbifSpeciesInfo(self, specie_name, kingdom='fungi'):
        
        results = sp.name_backbone(name=specie_name, kingdom= kingdom)
        if results:
            for key, value in results.items():
                self.__setattr__(key, value)

    def set_request_key(self,key):
        self.request_key = key
    
    def set_index(self,idx):
        self.index = idx
      
    def __str__(self):
        return self.canonicalName
