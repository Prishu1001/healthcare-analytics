"""
Configuration settings for the data pipeline
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# DuckDB database path
DUCKDB_PATH = DATA_DIR / "analytics.ddb"

# Create directories if they don't exist
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Data source URLs
DATA_SOURCES = {
    "va_facilities": {
        "url": "https://services3.arcgis.com/aqgBd3l68G8hEFFE/arcgis/rest/services/VHA_Facilities/FeatureServer/0/query?where=1%3D1&outFields=*&f=json",
        "file_name": "va_facilities.json",
        "description": "VA Medical Facilities locations and services"
    },
    "va_spending_fy2008": {
        "url": "https://catalog.data.gov/dataset/geographic-distribution-of-va-expenditures-fy2008",
        # Note: This may require manual download or finding the direct CSV link
        "file_name": "va_expenditures_fy2008.csv",
        "description": "VA expenditures by geographic location"
    },
    "medicare_providers_2022": {
        "url": "https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service/data",
        "file_name": "medicare_providers_2022.csv",
        "description": "Medicare Provider Utilization and Payment Data"
    },
    "ruca_codes": {
        "url": "https://www.ers.usda.gov/webdocs/DataFiles/53241/ruca2010zipcode.xlsx?v=5435.8",
        "file_name": "ruca_codes.xlsx",
        "description": "Rural-Urban Commuting Area Codes"
    },
    "census_population": {
        "url": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2023/counties/totals/co-est2023-alldata.csv",
        "file_name": "census_population.csv",
        "description": "County Population Estimates"
    }
}

# Data schema
RAW_SCHEMA = "raw"
STAGING_SCHEMA = "staging"
ANALYTICS_SCHEMA = "analytics"

# RUCA Classification mapping
RUCA_CLASSIFICATION = {
    1.0: "Metropolitan - Urban core",
    1.1: "Metropolitan - Urban core",
    2.0: "Metropolitan - Suburban",
    2.1: "Metropolitan - Suburban",
    3.0: "Metropolitan - Large town",
    4.0: "Micropolitan - Urban core",
    4.1: "Micropolitan - Urban core",
    5.0: "Micropolitan - Suburban",
    5.1: "Micropolitan - Suburban",
    6.0: "Micropolitan - Large town",
    7.0: "Small town - Low commuting",
    7.1: "Small town - Low commuting",
    7.2: "Small town - High commuting",
    7.3: "Small town - High commuting",
    7.4: "Small town - High commuting",
    8.0: "Rural - Low commuting",
    8.1: "Rural - Low commuting",
    8.2: "Rural - High commuting",
    8.3: "Rural - High commuting",
    8.4: "Rural - High commuting",
    9.0: "Rural - Primary flow to tract outside UA/UC",
    9.1: "Rural - Primary flow to tract outside UA/UC",
    9.2: "Rural - Primary flow to tract outside UA/UC",
    10.0: "Rural - No commuting",
    10.1: "Rural - No commuting",
    10.2: "Rural - No commuting",
    10.3: "Rural - No commuting",
    10.4: "Rural - No commuting",
    10.5: "Rural - No commuting",
    10.6: "Rural - No commuting"
}

# Simplified RUCA categories
RUCA_SIMPLIFIED = {
    "Metropolitan": [1.0, 1.1, 2.0, 2.1, 3.0],
    "Micropolitan": [4.0, 4.1, 5.0, 5.1, 6.0],
    "Small Town": [7.0, 7.1, 7.2, 7.3, 7.4],
    "Rural": [8.0, 8.1, 8.2, 8.3, 8.4, 9.0, 9.1, 9.2, 10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6]
}

# CMS Medicare data columns to keep (reduce file size)
MEDICARE_COLUMNS_TO_KEEP = [
    'Rndrng_NPI',
    'Rndrng_Prvdr_Last_Org_Name',
    'Rndrng_Prvdr_First_Name',
    'Rndrng_Prvdr_MI',
    'Rndrng_Prvdr_Crdntls',
    'Rndrng_Prvdr_Gndr',
    'Rndrng_Prvdr_Ent_Cd',
    'Rndrng_Prvdr_St1',
    'Rndrng_Prvdr_City',
    'Rndrng_Prvdr_State_Abrvtn',
    'Rndrng_Prvdr_State_FIPS',
    'Rndrng_Prvdr_Zip5',
    'Rndrng_Prvdr_RUCA',
    'Rndrng_Prvdr_RUCA_Desc',
    'Rndrng_Prvdr_Type',
    'Rndrng_Prvdr_Mdcr_Prtcptg_Ind',
    'HCPCS_Cd',
    'HCPCS_Desc',
    'Tot_Srvcs',
    'Tot_Benes',
    'Tot_Srvcs_Benes',
    'Avg_Sbmtd_Chrg',
    'Avg_Mdcr_Alowd_Amt',
    'Avg_Mdcr_Pymt_Amt'
]

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
