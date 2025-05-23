import pandas as pd
import requests    

output_folder = 'data/raw/geodata/twi'

urls = pd.read_csv('data/data_urls/twi_urls.csv', delimiter=';')

regions = pd.read_csv('data/inputs/qc_regions.csv')
print(regions)
print(urls )

filtered_urls = {}

for row in regions.iterrows():
    region = row[1]['region']
    for row in urls.iterrows():
        region_feuillet = row[1]['feuillet']
        region_urls = row[1]['twi_url']
        #print(filtered_urls.keys())
        if region_feuillet in filtered_urls.keys():
            pass
            #print('already in')
        else:
            if region_feuillet.startswith(region):
                filtered_urls[region_feuillet] = f'{region_urls}TWI_{region_feuillet}.tif'
    #url = row['twi_url']
    #print(feuillet)

print(len(filtered_urls))
test_urls = { '31K05SO' : 'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/Hydrographie/Indice_humidite_topographique/3-Donnees/31K/31K05SO/TWI_31K05SO.tif'
}

for idx, (key, url) in enumerate(filtered_urls.items()):
    print(idx+1 ,'/', len(filtered_urls))
    print(key)
    print(url)
    filename = f'{key}.tif'
    r = requests.get(url, allow_redirects=True)
    open(f'{output_folder}/{filename}', 'wb').write(r.content)
    print(f'{filename} downloaded')

