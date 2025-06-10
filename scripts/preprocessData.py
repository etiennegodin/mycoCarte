import pandas as pd 
import geopandas as gpd

from mycoCarte import geoUtils
from mycoCarte.dataPreprocessing import foretOuverte, occurences, bioclim, bias, mergeDataset

grid = geoUtils.clusterGrid(clusters= 6, overwrite= False)
grid_df = grid.drop(['geometry'], axis = 1)
foretOuverte_df = foretOuverte.preprocessData(overwrite= False)
bioclim_df = bioclim.preprocessData()
bias_df =  bias.readBiasData()

occurences_df = occurences.preprocessData(overwrite = False)
aggregated_occurences_df = occurences.process_fungi_ecology_index(occurences_df)
print(aggregated_occurences_df)
#Classification écologique du territoire québécois
#block cv based on nature instead of arbitrary 
#https://www.donneesquebec.ca/recherche/fr/dataset/systeme-hierarchique-de-classification-ecologique-du-territoire

#Épidémie, chablis et verglas
#https://www.donneesquebec.ca/recherche/fr/dataset/epidemies-chablis-et-verglas

#Feux de forêt
#https://www.donneesquebec.ca/recherche/fr/dataset/feux-de-foret

#Récolte et autres interventions sylvicoles
#https://www.donneesquebec.ca/recherche/dataset/recolte-et-reboisement

#ph_df = 
# landsat 

# Remove occurences in urban area from bias layers  
#aggregated_occurences_df = occurences.biasFilter(aggregated_occurences_df, bias_df)

datasets_to_merge = { 'foretOuverte': foretOuverte_df,
            'bioclim' :bioclim_df,
            'bias' : bias_df,
            'grid': grid_df
}

merged_occurences_df = mergeDataset(occurences_df, datasets_to_merge)
merged_agg_occurences_df = mergeDataset(aggregated_occurences_df, datasets_to_merge)

merged_occurences_df.to_csv('data/interim/geodata/vector/unifiedPreprocessedData/unifiedPreprocessedData.csv')
merged_agg_occurences_df.to_csv('data/interim/geodata/vector/unifiedPreprocessedData/aggregatedPreprocessedData.csv')

print('-'*100)
print(merged_occurences_df.shape)
print(merged_occurences_df.head())

print('-'*100)
print(merged_agg_occurences_df.shape)
print(merged_agg_occurences_df.head())

