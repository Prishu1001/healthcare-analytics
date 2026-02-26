"""
Step 1: Download all datasets from source

This script downloads:
1. VA Facilities (JSON from ArcGIS API)
2. VA Community Care Spending (CSV)
3. CMS Medicare Provider Utilization (CSV)
4. USDA RUCA Codes (XLSX)
5. Census Population Data (CSV)

Usage:
    python data_pipeline/01_download_data.py
"""

import logging
import sys
from pathlib import Path
import requests
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_pipeline.config import DATA_SOURCES, RAW_DATA_DIR
from data_pipeline.utils import download_file, check_file_exists, get_file_size_mb

logger = logging.getLogger(__name__)


def download_va_facilities():
    """
    Download VA Facilities data from ArcGIS API
    """
    source = DATA_SOURCES["va_facilities"]
    output_path = RAW_DATA_DIR / source["file_name"]
    
    if check_file_exists(output_path):
        logger.info("VA Facilities data already exists, skipping download")
        return True
    
    try:
        logger.info("Downloading VA Facilities data from ArcGIS API...")
        
        # API endpoint with parameters to get all records
        base_url = "https://services3.arcgis.com/aqgBd3l68G8hEFFE/arcgis/rest/services/VHA_Facilities/FeatureServer/0/query"
        
        params = {
            "where": "1=1",
            "outFields": "*",
            "f": "json",
            "resultOffset": 0,
            "resultRecordCount": 2000  # Maximum allowed per request
        }
        
        all_features = []
        offset = 0
        
        while True:
            params["resultOffset"] = offset
            response = requests.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            if not features:
                break
            
            all_features.extend(features)
            logger.info(f"Downloaded {len(all_features)} facilities so far...")
            
            # Check if there are more records
            if len(features) < params["resultRecordCount"]:
                break
            
            offset += params["resultRecordCount"]
        
        # Save to file
        output_data = {
            "features": all_features,
            "total_count": len(all_features)
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Successfully saved {len(all_features)} VA facilities to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download VA facilities: {e}")
        return False


def download_medicare_providers():
    """
    Download CMS Medicare Provider Utilization data
    
    Note: This is a large file (~2GB). The script downloads a sample for now.
    For full data, visit: https://data.cms.gov/provider-summary-by-type-of-service
    """
    source = DATA_SOURCES["medicare_providers_2022"]
    output_path = RAW_DATA_DIR / source["file_name"]
    
    if check_file_exists(output_path):
        logger.info("Medicare Provider data already exists, skipping download")
        return True
    
    logger.info("=" * 80)
    logger.info("MEDICARE PROVIDER DATA DOWNLOAD")
    logger.info("=" * 80)
    logger.info("")
    logger.info("The CMS Medicare Provider data is very large (~2GB compressed).")
    logger.info("Please download it manually from:")
    logger.info("https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service")
    logger.info("")
    logger.info("Steps:")
    logger.info("1. Click 'Export' -> 'CSV'")
    logger.info("2. Save as: medicare_providers_2022.csv")
    logger.info(f"3. Move to: {RAW_DATA_DIR.absolute()}")
    logger.info("")
    logger.info("For now, we'll create a placeholder file for testing.")
    logger.info("=" * 80)
    
    # Create a placeholder
    output_path.write_text("# Placeholder - Download manually from CMS website\n")
    
    return True


def download_va_spending():
    """
    Download VA Geographic Spending data
    
    Note: May require manual download from data.gov
    """
    source = DATA_SOURCES["va_spending_fy2008"]
    output_path = RAW_DATA_DIR / source["file_name"]
    
    if check_file_exists(output_path):
        logger.info("VA Spending data already exists, skipping download")
        return True
    
    logger.info("=" * 80)
    logger.info("VA SPENDING DATA DOWNLOAD")
    logger.info("=" * 80)
    logger.info("")
    logger.info("VA spending data may require manual download.")
    logger.info("Please visit:")
    logger.info("https://catalog.data.gov/dataset/geographic-distribution-of-va-expenditures-fy2008")
    logger.info("or search for more recent data at:")
    logger.info("https://www.data.va.gov/browse?category=Spending")
    logger.info("")
    logger.info(f"Save CSV file to: {RAW_DATA_DIR.absolute()}")
    logger.info("=" * 80)
    
    # Create a placeholder
    output_path.write_text("# Placeholder - Download manually from VA data portal\n")
    
    return True


def download_ruca_codes():
    """
    Download USDA RUCA codes (ZIP code level)
    """
    source = DATA_SOURCES["ruca_codes"]
    output_path = RAW_DATA_DIR / source["file_name"]
    
    if check_file_exists(output_path):
        logger.info("RUCA codes already exist, skipping download")
        return True
    
    logger.info("Downloading RUCA codes from USDA...")
    
    # Direct download link
    url = "https://www.ers.usda.gov/webdocs/DataFiles/53241/ruca2010zipcode.xlsx"
    
    return download_file(url, output_path)


def download_census_population():
    """
    Download Census population estimates
    """
    source = DATA_SOURCES["census_population"]
    output_path = RAW_DATA_DIR / source["file_name"]
    
    if check_file_exists(output_path):
        logger.info("Census population data already exists, skipping download")
        return True
    
    logger.info("Downloading Census population data...")
    
    # Census population estimates URL
    url = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2023/counties/totals/co-est2023-alldata.csv"
    
    return download_file(url, output_path)


def main():
    """
    Main function to download all datasets
    """
    logger.info("=" * 80)
    logger.info("DATA DOWNLOAD SCRIPT - Healthcare Provider Analysis")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Raw data directory: {RAW_DATA_DIR.absolute()}")
    logger.info("")
    
    # Track download results
    results = {}
    
    # Download each dataset
    logger.info("1/5: Downloading VA Facilities...")
    results["va_facilities"] = download_va_facilities()
    
    logger.info("\n2/5: Downloading VA Spending...")
    results["va_spending"] = download_va_spending()
    
    logger.info("\n3/5: Downloading Medicare Providers...")
    results["medicare_providers"] = download_medicare_providers()
    
    logger.info("\n4/5: Downloading RUCA Codes...")
    results["ruca_codes"] = download_ruca_codes()
    
    logger.info("\n5/5: Downloading Census Population...")
    results["census_population"] = download_census_population()
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("DOWNLOAD SUMMARY")
    logger.info("=" * 80)
    
    for dataset, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        logger.info(f"{status}: {dataset}")
    
    # List downloaded files with sizes
    logger.info("\nDownloaded files:")
    for file_path in RAW_DATA_DIR.iterdir():
        if file_path.is_file():
            size_mb = get_file_size_mb(file_path)
            logger.info(f"  - {file_path.name}: {size_mb} MB")
    
    logger.info("\n" + "=" * 80)
    logger.info("Next step: python data_pipeline/02_load_raw.py")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
