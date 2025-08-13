**Vegetation / host detection**

- **NIR (Near Infrared)** and **Red** → **NDVI = (NIR - Red)/(NIR + Red)** — proxy for live green biomass / host vegetation. (Sentinel-2 & Landsat) [Google for Developers+1](https://developers.google.com/earth-engine/datasets/catalog/sentinel-2?utm_source=chatgpt.com)
    
- **Red-edge bands (Sentinel-2 B5/B6/B7/B8A)** — sensitive to chlorophyll and plant stress; useful if fungi relate to stressed trees or subtle canopy changes. [Google for Developers](https://developers.google.com/earth-engine/datasets/catalog/sentinel-2?utm_source=chatgpt.com)
    

**Moisture / fungal fruiting drivers**

- **SWIR1 & SWIR2 (shortwave infrared)** → used for **NBR** (Normalized Burn Ratio) and moisture indices; detects canopy water content and recent disturbance. (Landsat & Sentinel-2) [Google for Developers+1](https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2?utm_source=chatgpt.com)
    
- **NDWI / MNDWI** — water / moisture proxies that can reflect wet microhabitats favourable to many fungi.
    

**Disturbance, age, structure**

- **NBR (Normalized Burn Ratio)** or change metrics from multi-date Landsat/Sentinel to detect past burns, harvests, and canopy loss. Hansen forest change is a ready product for loss/gain. [Google for Developers](https://developers.google.com/earth-engine/datasets/catalog/UMD_hansen_global_forest_change_2024_v1_12?utm_source=chatgpt.com)
    
- **GEDI canopy height / biomass** — fungi (especially wood-decay species) often depend on standing deadwood, canopy height, and biomass — GEDI gives structural variables you can use as predictors. [Google for Developers](https://developers.google.com/earth-engine/datasets/catalog/LARSE_GEDI_GEDI02_A_002_MONTHLY?utm_source=chatgpt.com)
    

**Phenology & seasonality**

- Use dense Sentinel-2 time series (5-day revisit) or Landsat time series to extract **phenological metrics**: green-up date, peak NDVI, season length — many fungi have strong seasonal/phenological signals.
    

**Structure under cloud / all-weather**

- **Sentinel-1 SAR** (VV/VH) gives information on canopy roughness and moisture even when optical sensors are clouded (northern Québec has a lot of cloud in some seasons). [Google for Developers](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD?utm_source=chatgpt.com)
    

**Topography & microclimate**

- **DEM → slope, aspect, elevation** strongly influence microclimate and fungal distributions (temperature, humidity). Use NRCan CDEM / HRDEM. [Google for Developers](https://developers.google.com/earth-engine/datasets/catalog/NRCan_CDEM?utm_source=chatgpt.com)[Open Government Canada](https://open.canada.ca/data/en/dataset/957782bf-847c-4644-a757-e383c0057995?utm_source=chatgpt.com)