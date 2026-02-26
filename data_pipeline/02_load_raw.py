"""
Step 2: Load raw data into DuckDB

This script creates raw schema tables and loads downloaded data as-is.

Usage:
    python data_pipeline/02_load_raw.py
"""

import logging
import sys
from pathlib import Path
import json
import duckdb
import pandas as pd
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_pipeline.config import RAW_DATA_DIR, DUCKDB_PATH, RAW_SCHEMA
from data_pipeline.utils import ProgressLogger

logger = logging.getLogger(__name__)


def create_raw_schema(con):
    """
    Create raw schema and tables in DuckDB
    """
    logger.info("Creating raw schema...")
    
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")
    
    # Drop existing tables
    con.execute(f"DROP TABLE IF EXISTS {RAW_SCHEMA}.va_facilities")
    con.execute(f"DROP TABLE IF EXISTS {RAW_SCHEMA}.va_expenditures")
    con.execute(f"DROP TABLE IF EXISTS {RAW_SCHEMA}.medicare_providers")
    con.execute(f"DROP TABLE IF EXISTS {RAW_SCHEMA}.ruca_codes")
    con.execute(f"DROP TABLE IF EXISTS {RAW_SCHEMA}.census_population")
    
    logger.info("Raw schema created successfully")


def load_va_facilities(con):
    """
    Load VA Facilities from JSON
    """
    logger.info("Loading VA Facilities data...")
    
    json_file = RAW_DATA_DIR / "va_facilities.json"
    
    if not json_file.exists():
        logger.error(f"VA Facilities file not found: {json_file}")
        return False
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Extract features and flatten attributes
        records = []
        for feature in data.get("features", []):
            attrs = feature.get("attributes", {})
            geometry = feature.get("geometry", {})
            
            record = {
                **attrs,
                "longitude": geometry.get("x"),
                "latitude": geometry.get("y"),
                "load_date": date.today().isoformat()
            }
            records.append(record)
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Register DataFrame and create table
        con.execute(f"CREATE TABLE {RAW_SCHEMA}.va_facilities AS SELECT * FROM df")
        
        count = con.execute(f"SELECT COUNT(*) FROM {RAW_SCHEMA}.va_facilities").fetchone()[0]
        logger.info(f"Loaded {count:,} VA facility records")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to load VA facilities: {e}")
        return False


def load_ruca_codes(con):
    """
    Load RUCA codes from Excel
    """
    logger.info("Loading RUCA codes...")
    
    excel_file = RAW_DATA_DIR / "ruca_codes.xlsx"
    
    if not excel_file.exists():
        logger.error(f"RUCA codes file not found: {excel_file}")
        return False
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        
        # Add load date
        df['load_date'] = date.today().isoformat()
        
        # Create table
        con.execute(f"CREATE TABLE {RAW_SCHEMA}.ruca_codes AS SELECT * FROM df")
        
        count = con.execute(f"SELECT COUNT(*) FROM {RAW_SCHEMA}.ruca_codes").fetchone()[0]
        logger.info(f"Loaded {count:,} RUCA code records")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to load RUCA codes: {e}")
        return False


def load_census_population(con):
    """
    Load Census population data from CSV
    """
    logger.info("Loading Census population data...")
    
    csv_file = RAW_DATA_DIR / "census_population.csv"
    
    if not csv_file.exists():
        logger.error(f"Census population file not found: {csv_file}")
        return False
    
    try:
        # Read CSV with latin1 encoding (Census files use this)
        df = pd.read_csv(csv_file, encoding='latin1')
        
        # Add load date
        df['load_date'] = date.today().isoformat()
        
        # Create table
        con.execute(f"CREATE TABLE {RAW_SCHEMA}.census_population AS SELECT * FROM df")
        
        count = con.execute(f"SELECT COUNT(*) FROM {RAW_SCHEMA}.census_population").fetchone()[0]
        logger.info(f"Loaded {count:,} census population records")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to load census population: {e}")
        return False


def load_medicare_providers(con):
    """
    Load Medicare Provider data from CSV
    
    Note: This file is very large. We'll load it in chunks.
    """
    logger.info("Loading Medicare Provider data...")
    
    csv_file = RAW_DATA_DIR / "medicare_providers_2022.csv"
    
    if not csv_file.exists():
        logger.warning(f"Medicare provider file not found: {csv_file}")
        logger.warning("Creating empty table for now. Please download the full dataset.")
        
        # Create empty table with expected schema
        con.execute(f"""
            CREATE TABLE {RAW_SCHEMA}.medicare_providers (
                Rndrng_NPI VARCHAR,
                Rndrng_Prvdr_Last_Org_Name VARCHAR,
                Rndrng_Prvdr_First_Name VARCHAR,
                Rndrng_Prvdr_MI VARCHAR,
                Rndrng_Prvdr_Crdntls VARCHAR,
                Rndrng_Prvdr_Gndr VARCHAR,
                Rndrng_Prvdr_Ent_Cd VARCHAR,
                Rndrng_Prvdr_St1 VARCHAR,
                Rndrng_Prvdr_City VARCHAR,
                Rndrng_Prvdr_State_Abrvtn VARCHAR,
                Rndrng_Prvdr_Zip5 VARCHAR,
                HCPCS_Cd VARCHAR,
                HCPCS_Desc VARCHAR,
                Tot_Srvcs BIGINT,
                Tot_Benes BIGINT,
                Avg_Sbmtd_Chrg DOUBLE,
                Avg_Mdcr_Alowd_Amt DOUBLE,
                Avg_Mdcr_Pymt_Amt DOUBLE,
                load_date DATE
            )
        """)
        
        return False
    
    try:
        # For very large files, use DuckDB's native CSV reader
        con.execute(f"""
            CREATE TABLE {RAW_SCHEMA}.medicare_providers AS 
            SELECT *, CURRENT_DATE as load_date
            FROM read_csv_auto('{csv_file.as_posix()}', 
                header=True, 
                sample_size=100000)
        """)
        
        count = con.execute(f"SELECT COUNT(*) FROM {RAW_SCHEMA}.medicare_providers").fetchone()[0]
        logger.info(f"Loaded {count:,} Medicare provider records")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to load Medicare providers: {e}")
        return False


def load_va_spending(con):
    """
    Load VA spending/expenditure data
    """
    logger.info("Loading VA spending data...")
    
    csv_file = RAW_DATA_DIR / "va_expenditures_fy2008.csv"
    
    if not csv_file.exists():
        logger.warning(f"VA spending file not found: {csv_file}")
        logger.warning("Creating empty table. Please download actual data.")
        
        con.execute(f"""
            CREATE TABLE {RAW_SCHEMA}.va_expenditures (
                state VARCHAR,
                county VARCHAR,
                expenditure_amount DOUBLE,
                fiscal_year INTEGER,
                load_date DATE
            )
        """)
        
        return False
    
    try:
        df = pd.read_csv(csv_file)
        df['load_date'] = date.today().isoformat()
        
        con.execute(f"CREATE TABLE {RAW_SCHEMA}.va_expenditures AS SELECT * FROM df")
        
        count = con.execute(f"SELECT COUNT(*) FROM {RAW_SCHEMA}.va_expenditures").fetchone()[0]
        logger.info(f"Loaded {count:,} VA expenditure records")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to load VA spending: {e}")
        return False


def show_data_summary(con):
    """
    Show summary of loaded data
    """
    logger.info("\n" + "=" * 80)
    logger.info("DATA LOADING SUMMARY")
    logger.info("=" * 80)
    
    tables = [
        "va_facilities",
        "va_expenditures", 
        "medicare_providers",
        "ruca_codes",
        "census_population"
    ]
    
    for table in tables:
        try:
            count = con.execute(f"SELECT COUNT(*) FROM {RAW_SCHEMA}.{table}").fetchone()[0]
            logger.info(f"{RAW_SCHEMA}.{table}: {count:,} records")
        except:
            logger.warning(f"{RAW_SCHEMA}.{table}: Table not found or empty")
    
    # Database file size
    if DUCKDB_PATH.exists():
        size_mb = DUCKDB_PATH.stat().st_size / (1024 * 1024)
        logger.info(f"\nDatabase size: {size_mb:.2f} MB")


def main():
    """
    Main function to load all raw data
    """
    logger.info("=" * 80)
    logger.info("LOAD RAW DATA - Healthcare Provider Analysis")
    logger.info("=" * 80)
    logger.info(f"Database: {DUCKDB_PATH.absolute()}")
    logger.info("")
    
    try:
        # Connect to DuckDB
        con = duckdb.connect(str(DUCKDB_PATH))
        
        # Create schema
        create_raw_schema(con)
        
        # Load each dataset
        results = {}
        
        logger.info("\n1/5: Loading VA Facilities...")
        results["va_facilities"] = load_va_facilities(con)
        
        logger.info("\n2/5: Loading VA Spending...")
        results["va_spending"] = load_va_spending(con)
        
        logger.info("\n3/5: Loading Medicare Providers...")
        results["medicare_providers"] = load_medicare_providers(con)
        
        logger.info("\n4/5: Loading RUCA Codes...")
        results["ruca_codes"] = load_ruca_codes(con)
        
        logger.info("\n5/5: Loading Census Population...")
        results["census_population"] = load_census_population(con)
        
        # Show summary
        show_data_summary(con)
        
        # Close connection
        con.close()
        
        logger.info("\n" + "=" * 80)
        logger.info("Next step: python data_pipeline/03_transform_staging.py")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Failed to load raw data: {e}")
        raise


if __name__ == "__main__":
    main()
