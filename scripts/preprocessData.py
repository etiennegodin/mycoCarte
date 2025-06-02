import pandas as pd 
import geopandas as gpd

from mycoCarte import geoUtils
from mycoCarte.dataPreprocessing import foretOuverte, occurences, bioclim

bioclim_df = bioclim.preprocessData()
foretOuverte_df = foretOuverte.preprocessData(overwrite= False)
occurences_df = occurences.preprocessData()


#bias data sa
#ph data
#Disturbance Data: Information on forest fires, insect outbreaks, logging history. These can significantly impact fungal communities.


final_df = occurences_df

try:
    final_df = final_df.merge(foretOuverte_df, on = 'FID',how = 'left')
except Exception as e:
    print('Failed to merge foretOuverte_df data')
    print(e)

try:
    final_df = final_df.merge(bioclim_df, on = 'FID',how = 'left')
except Exception as e:
    print('Failed to merge bioclim_df data')
    print(e)

final_df.to_csv('data/interim/geodata/vector/unifiedPreprocessedData/unifiedPreprocessedData.csv')
print(final_df.head())
