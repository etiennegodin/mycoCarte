import pandas as pd 
import geopandas as gpd

from mycoCarte import geoUtils
from mycoCarte.dataPreprocessing import foretOuverte, occurences, bioclim, bias

geoUtils.clusterGrid(clusters= 20, overwrite= False)
foretOuverte_df = foretOuverte.preprocessData(overwrite= False)
occurences_df = occurences.preprocessData(overwrite = False)
bioclim_df = bioclim.preprocessData()
bias_df =  bias.readBiasData()
#ph_df = 
#ph data
#Disturbance Data: Information on forest fires, insect outbreaks, logging history. These can significantly impact fungal communities.
# landsat 


# Remove occurences in urban area from bias layers  
occurences_df = occurences.biasFilter(occurences_df, bias_df)

datasets_to_merge = [foretOuverte_df,
            bioclim_df,
            bias_df

]

final_df = occurences_df

for dataset in datasets_to_merge:
    try:
        final_df = final_df.merge(dataset, on = 'FID',how = 'left')
    except Exception as e:
        print(f'Failed to merge {str(dataset)} data')
        print(e)

final_df.to_csv('data/interim/geodata/vector/unifiedPreprocessedData/unifiedPreprocessedData.csv')
print(final_df.head())
