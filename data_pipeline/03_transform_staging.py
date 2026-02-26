"""
Step 3: Transform raw data to staging tables

This script cleans, standardizes, and prepares data for analytics.

Usage:
    python data_pipeline/03_transform_staging.py
"""

import logging
import sys
from pathlib import Path
import duckdb

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_pipeline.config import DUCKDB_PATH, RAW_SCHEMA, STAGING_SCHEMA
from data_pipeline.utils import get_ruca_category

logger = logging.getLogger(__name__)


def create_staging_schema(con):
    """
    Create staging schema
    """
    logger.info("Creating staging schema...")
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {STAGING_SCHEMA}")


def transform_facilities(con):
    """
    Transform VA facilities to staging
    """
    logger.info("Transforming VA facilities to staging...")
    
    con.execute(f"DROP TABLE IF EXISTS {STAGING_SCHEMA}.facilities")
    
    con.execute(f"""
        CREATE TABLE {STAGING_SCHEMA}.facilities AS
        SELECT 
            CAST(StationID AS VARCHAR) as facility_id,
            StationName as facility_name,
            StationType as facility_type,
            address1 as address,
            City as city,
            State as state,
            Zip as zip_code,
            latitude,
            longitude,
            CAST(Phone AS VARCHAR) as phone,
            CURRENT_DATE as load_date
        FROM {RAW_SCHEMA}.va_facilities
        WHERE StationID IS NOT NULL
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {STAGING_SCHEMA}.facilities").fetchone()[0]
    logger.info(f"Transformed {count:,} facility records")


def transform_ruca_codes(con):
    """
    Transform RUCA codes to staging
    """
    logger.info("Transforming RUCA codes to staging...")
    
    con.execute(f"DROP TABLE IF EXISTS {STAGING_SCHEMA}.rural_urban_codes")
    
    # RUCA Excel columns may vary - adjust as needed
    con.execute(f"""
        CREATE TABLE {STAGING_SCHEMA}.rural_urban_codes AS
        SELECT 
            CAST(ZIP_CODE AS VARCHAR) as zip_code,
            CAST(STATE AS VARCHAR) as state,
            CAST(RUCA1 AS DOUBLE) as ruca_primary,
            CAST(RUCA2 AS DOUBLE) as ruca_secondary,
            CASE 
                WHEN RUCA1 BETWEEN 1.0 AND 3.0 THEN 'Metropolitan'
                WHEN RUCA1 BETWEEN 4.0 AND 6.0 THEN 'Micropolitan'
                WHEN RUCA1 BETWEEN 7.0 AND 7.4 THEN 'Small Town'
                WHEN RUCA1 >= 8.0 THEN 'Rural'
                ELSE 'Unknown'
            END as classification,
            CURRENT_DATE as load_date
        FROM {RAW_SCHEMA}.ruca_codes
        WHERE ZIP_CODE IS NOT NULL
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {STAGING_SCHEMA}.rural_urban_codes").fetchone()[0]
    logger.info(f"Transformed {count:,} RUCA code records")


def transform_census_population(con):
    """
    Transform Census population to staging
    """
    logger.info("Transforming Census population to staging...")
    
    con.execute(f"DROP TABLE IF EXISTS {STAGING_SCHEMA}.population")
    
    # Census column names - adjust based on actual file
    con.execute(f"""
        CREATE TABLE {STAGING_SCHEMA}.population AS
        SELECT 
            CAST(STATE AS VARCHAR) as state_fips,
            CAST(COUNTY AS VARCHAR) as county_fips,
            STNAME as state_name,
            CTYNAME as county_name,
            CAST(POPESTIMATE2023 AS INTEGER) as population_total,
            -- Estimate 65+ population (Census provides age breakdowns)
            CAST(POPESTIMATE2023 * 0.17 AS INTEGER) as population_65plus,
            2023 as year,
            CURRENT_DATE as load_date
        FROM {RAW_SCHEMA}.census_population
        WHERE COUNTY != '000'  -- Exclude state totals
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {STAGING_SCHEMA}.population").fetchone()[0]
    logger.info(f"Transformed {count:,} population records")


def transform_medicare_providers(con):
    """
    Transform Medicare providers to staging
    """
    logger.info("Transforming Medicare providers to staging...")
    
    con.execute(f"DROP TABLE IF EXISTS {STAGING_SCHEMA}.medicare_utilization")
    
    # Check if table has data
    check = con.execute(f"SELECT COUNT(*) FROM {RAW_SCHEMA}.medicare_providers").fetchone()[0]
    
    if check == 0:
        logger.warning("No Medicare provider data available. Creating empty staging table.")
        con.execute(f"""
            CREATE TABLE {STAGING_SCHEMA}.medicare_utilization (
                npi VARCHAR,
                provider_name VARCHAR,
                credentials VARCHAR,
                gender VARCHAR,
                address VARCHAR,
                city VARCHAR,
                state VARCHAR,
                zip_code VARCHAR,
                hcpcs_code VARCHAR,
                hcpcs_description VARCHAR,
                service_count INTEGER,
                beneficiary_count INTEGER,
                submitted_charge DOUBLE,
                allowed_amount DOUBLE,
                year INTEGER,
                load_date DATE
            )
        """)
        return
    
    con.execute(f"""
        CREATE TABLE {STAGING_SCHEMA}.medicare_utilization AS
        SELECT 
            Rndrng_NPI as npi,
            CONCAT(Rndrng_Prvdr_First_Name, ' ', Rndrng_Prvdr_Last_Org_Name) as provider_name,
            Rndrng_Prvdr_Crdntls as credentials,
            Rndrng_Prvdr_Gndr as gender,
            Rndrng_Prvdr_St1 as address,
            Rndrng_Prvdr_City as city,
            Rndrng_Prvdr_State_Abrvtn as state,
            Rndrng_Prvdr_Zip5 as zip_code,
            HCPCS_Cd as hcpcs_code,
            HCPCS_Desc as hcpcs_description,
            CAST(Tot_Srvcs AS INTEGER) as service_count,
            CAST(Tot_Benes AS INTEGER) as beneficiary_count,
            Avg_Sbmtd_Chrg as submitted_charge,
            Avg_Mdcr_Alowd_Amt as allowed_amount,
            2022 as year,
            CURRENT_DATE as load_date
        FROM {RAW_SCHEMA}.medicare_providers
        WHERE Rndrng_NPI IS NOT NULL
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {STAGING_SCHEMA}.medicare_utilization").fetchone()[0]
    logger.info(f"Transformed {count:,} Medicare provider records")


def transform_va_spending(con):
    """
    Transform VA spending to staging
    """
    logger.info("Transforming VA spending to staging...")
    
    con.execute(f"DROP TABLE IF EXISTS {STAGING_SCHEMA}.va_spending")
    
    # Check if table has data
    check = con.execute(f"SELECT COUNT(*) FROM {RAW_SCHEMA}.va_expenditures").fetchone()[0]
    
    if check == 0:
        logger.warning("No VA spending data available. Creating empty staging table.")
        con.execute(f"""
            CREATE TABLE {STAGING_SCHEMA}.va_spending (
                state VARCHAR,
                county_fips VARCHAR,
                county_name VARCHAR,
                fiscal_year INTEGER,
                program_type VARCHAR,
                expenditure_amount DOUBLE,
                load_date DATE
            )
        """)
        return
    
    # This will need adjustment based on actual data structure
    con.execute(f"""
        CREATE TABLE {STAGING_SCHEMA}.va_spending AS
        SELECT 
            state,
            NULL as county_fips,  -- Will need to map county names to FIPS
            county as county_name,
            fiscal_year,
            'Community Care' as program_type,
            expenditure_amount,
            CURRENT_DATE as load_date
        FROM {RAW_SCHEMA}.va_expenditures
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {STAGING_SCHEMA}.va_spending").fetchone()[0]
    logger.info(f"Transformed {count:,} VA spending records")


def show_staging_summary(con):
    """
    Show summary of staging data
    """
    logger.info("\n" + "=" * 80)
    logger.info("STAGING DATA SUMMARY")
    logger.info("=" * 80)
    
    tables = [
        "facilities",
        "va_spending",
        "medicare_utilization",
        "rural_urban_codes",
        "population"
    ]
    
    for table in tables:
        try:
            count = con.execute(f"SELECT COUNT(*) FROM {STAGING_SCHEMA}.{table}").fetchone()[0]
            logger.info(f"{STAGING_SCHEMA}.{table}: {count:,} records")
        except Exception as e:
            logger.warning(f"{STAGING_SCHEMA}.{table}: Error - {e}")


def main():
    """
    Main function to transform data to staging
    """
    logger.info("=" * 80)
    logger.info("TRANSFORM TO STAGING - Healthcare Provider Analysis")
    logger.info("=" * 80)
    logger.info(f"Database: {DUCKDB_PATH.absolute()}")
    logger.info("")
    
    try:
        # Connect to DuckDB
        con = duckdb.connect(str(DUCKDB_PATH))
        
        # Create schema
        create_staging_schema(con)
        
        # Transform each dataset
        logger.info("\n1/5: Transforming VA Facilities...")
        transform_facilities(con)
        
        logger.info("\n2/5: Transforming VA Spending...")
        transform_va_spending(con)
        
        logger.info("\n3/5: Transforming Medicare Providers...")
        transform_medicare_providers(con)
        
        logger.info("\n4/5: Transforming RUCA Codes...")
        transform_ruca_codes(con)
        
        logger.info("\n5/5: Transforming Census Population...")
        transform_census_population(con)
        
        # Show summary
        show_staging_summary(con)
        
        # Close connection
        con.close()
        
        logger.info("\n" + "=" * 80)
        logger.info("Next step: python data_pipeline/04_build_analytics.py")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Failed to transform staging data: {e}")
        raise


if __name__ == "__main__":
    main()
