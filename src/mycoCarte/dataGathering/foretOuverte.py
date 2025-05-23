import pandas as pd
import requests    
import asyncio
import os, sys 
from mycoCarte.Utils import unzip_file

zip_output_folder = 'data/raw/geodata/foretOuverte/PEE_MAJ_PROV/zip'
gpkg_output_folder = 'data/raw/geodata/foretOuverte/PEE_MAJ_PROV/gpkg'

regions_df = pd.read_csv('data/inputs/qc_regions.csv')

def skip_process(region):
    expected_path = gpkg_output_folder + f'CARTE_ECO_MAJ_{region}_GPKG.gpkg'
    if os.path.exists(expected_path):
        print(f'{region} data already requested and downloaded to disk')
        return True

    else:
        print(f'{region} data not found on disk')
        return False
    
async def get_zip_file(region):
        print(f'Request {region} data')
        url = f'https://diffusion.mffp.gouv.qc.ca/Diffusion/DonneeGratuite/Foret/DONNEES_FOR_ECO_SUD/Cartes_ecoforestieres_perturbations/{region}/CARTE_ECO_MAJ_{region}_GPKG.zip'
        filename = f'CARTE_ECO_MAJ_{region}_GPKG.zip'
        zip_download_path = f'{zip_output_folder}/{filename}'
        r = requests.get(url, allow_redirects=True)
        open(zip_download_path, 'wb').write(r.content)
        print(f'{zip_download_path} downloaded')

        return zip_download_path

async def async_unzip(region,zip_download_path):
    output_path = gpkg_output_folder + '/'
    unzip_file(zip_download_path, output_path)


async def process_region_data(region, semaphore, max_retries = 15, delay = 20):

    async with semaphore:
        zip_download_path = await get_zip_file(region)

        retries = 0
        while retries < max_retries:
            try:
                await async_unzip(region,zip_download_path)
                print(f'Took {retries} to unzip {region} file')
                break
            except:
                print(f"Retry {retries + 1}/{max_retries} to unzip {region} gpkg")
                retries += 1
                await asyncio.sleep(delay) 

async def main(regions):
    # check if file already downloaded 
    regions_to_process = []
    for r in regions:
        if not skip_process(r):
             regions_to_process.append(r)

    max_concurrent_requests = 5
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    tasks = [process_region_data(region, semaphore) for region in regions_to_process]
    await asyncio.gather(*tasks)  # Wait for all tasks to complete
    print('All occurences data on disk')
    return True

if __name__ == '__main__':

    print(regions_df)
    regions_list = []
    for row in regions_df.iterrows():
        region = row[1]['region']
        regions_list.append(region)

    completed = asyncio.run(main(regions_list))



    

    