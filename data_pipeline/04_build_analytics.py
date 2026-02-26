"""
Step 4: Build analytics tables with business metrics

This script creates the final analytics layer for visualization.

Usage:
    python data_pipeline/04_build_analytics.py
"""

import logging
import sys
from pathlib import Path
import duckdb

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_pipeline.config import DUCKDB_PATH, STAGING_SCHEMA, ANALYTICS_SCHEMA

logger = logging.getLogger(__name__)


def create_analytics_schema(con):
    """
    Create analytics schema
    """
    logger.info("Creating analytics schema...")
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {ANALYTICS_SCHEMA}")


def build_provider_network_summary(con):
    """
    Build county-level provider network summary
    """
    logger.info("Building provider network summary...")
    
    con.execute(f"DROP TABLE IF EXISTS {ANALYTICS_SCHEMA}.provider_network_summary")
    
    con.execute(f"""
        CREATE TABLE {ANALYTICS_SCHEMA}.provider_network_summary AS
        WITH county_data AS (
            SELECT 
                p.state_fips,
                p.county_fips,
                p.county_name,
                p.state_name,
                p.population_total,
                p.population_65plus
            FROM {STAGING_SCHEMA}.population p
        ),
        va_facilities_by_county AS (
            SELECT 
                f.state,
                COUNT(*) as facility_count
            FROM {STAGING_SCHEMA}.facilities f
            GROUP BY f.state
        ),
        medicare_by_county AS (
            SELECT 
                m.state,
                m.zip_code,
                COUNT(DISTINCT m.npi) as provider_count,
                SUM(m.beneficiary_count) as total_beneficiaries,
                SUM(m.service_count) as total_services
            FROM {STAGING_SCHEMA}.medicare_utilization m
            GROUP BY m.state, m.zip_code
        ),
        ruca_by_zip AS (
            SELECT 
                zip_code,
                state,
                classification
            FROM {STAGING_SCHEMA}.rural_urban_codes
        )
        SELECT 
            cd.state_fips,
            cd.county_fips,
            cd.county_name,
            cd.state_name,
            cd.population_total,
            cd.population_65plus,
            COALESCE(vf.facility_count, 0) as va_facilities_count,
            -- Note: Need better county aggregation for Medicare
            CAST(cd.population_65plus / NULLIF(cd.population_total, 0) * 100 AS DECIMAL(5,2)) as pct_elderly,
            CURRENT_DATE as load_date
        FROM county_data cd
        LEFT JOIN va_facilities_by_county vf ON cd.state_name = vf.state
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {ANALYTICS_SCHEMA}.provider_network_summary").fetchone()[0]
    logger.info(f"Created provider network summary with {count:,} counties")


def build_rural_access_gaps(con):
    """
    Build rural access gap analysis
    """
    logger.info("Building rural access gaps analysis...")
    
    con.execute(f"DROP TABLE IF EXISTS {ANALYTICS_SCHEMA}.rural_access_gaps")
    
    con.execute(f"""
        CREATE TABLE {ANALYTICS_SCHEMA}.rural_access_gaps AS
        WITH zip_classification AS (
            SELECT 
                r.zip_code,
                r.state,
                r.classification,
                r.ruca_primary
            FROM {STAGING_SCHEMA}.rural_urban_codes r
        ),
        medicare_by_zip AS (
            SELECT 
                m.zip_code,
                m.state,
                COUNT(DISTINCT m.npi) as provider_count,
                SUM(m.beneficiary_count) as beneficiary_count,
                AVG(m.submitted_charge) as avg_charge
            FROM {STAGING_SCHEMA}.medicare_utilization m
            GROUP BY m.zip_code, m.state
        )
        SELECT 
            z.zip_code,
            z.state,
            z.classification,
            z.ruca_primary,
            COALESCE(m.provider_count, 0) as medicare_provider_count,
            COALESCE(m.beneficiary_count, 0) as beneficiary_count,
            COALESCE(m.avg_charge, 0) as avg_charge_per_service,
            CASE 
                WHEN z.classification = 'Rural' AND COALESCE(m.provider_count, 0) < 5 THEN 'High Priority'
                WHEN z.classification = 'Rural' AND COALESCE(m.provider_count, 0) < 10 THEN 'Medium Priority'
                WHEN z.classification IN ('Small Town', 'Micropolitan') AND COALESCE(m.provider_count, 0) < 20 THEN 'Medium Priority'
                ELSE 'Low Priority'
            END as priority_tier,
            CURRENT_DATE as load_date
        FROM zip_classification z
        LEFT JOIN medicare_by_zip m ON z.zip_code = m.zip_code
        WHERE z.classification IN ('Rural', 'Small Town', 'Micropolitan')
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {ANALYTICS_SCHEMA}.rural_access_gaps").fetchone()[0]
    logger.info(f"Created rural access gaps with {count:,} ZIP codes")


def build_provider_service_patterns(con):
    """
    Build provider service pattern analysis
    """
    logger.info("Building provider service patterns...")
    
    con.execute(f"DROP TABLE IF EXISTS {ANALYTICS_SCHEMA}.provider_service_patterns")
    
    # Check if Medicare data exists
    check = con.execute(f"SELECT COUNT(*) FROM {STAGING_SCHEMA}.medicare_utilization").fetchone()[0]
    
    if check == 0:
        logger.warning("No Medicare data available. Creating empty analytics table.")
        con.execute(f"""
            CREATE TABLE {ANALYTICS_SCHEMA}.provider_service_patterns (
                npi VARCHAR,
                provider_name VARCHAR,
                state VARCHAR,
                zip_code VARCHAR,
                ruca_classification VARCHAR,
                total_services INTEGER,
                unique_beneficiaries INTEGER,
                unique_procedures INTEGER,
                avg_charge_per_service DOUBLE,
                load_date DATE
            )
        """)
        return
    
    con.execute(f"""
        CREATE TABLE {ANALYTICS_SCHEMA}.provider_service_patterns AS
        WITH provider_aggregates AS (
            SELECT 
                m.npi,
                m.provider_name,
                m.state,
                m.zip_code,
                SUM(m.service_count) as total_services,
                SUM(m.beneficiary_count) as unique_beneficiaries,
                COUNT(DISTINCT m.hcpcs_code) as unique_procedures,
                AVG(m.submitted_charge) as avg_charge_per_service
            FROM {STAGING_SCHEMA}.medicare_utilization m
            GROUP BY m.npi, m.provider_name, m.state, m.zip_code
        )
        SELECT 
            p.npi,
            p.provider_name,
            p.state,
            p.zip_code,
            COALESCE(r.classification, 'Unknown') as ruca_classification,
            p.total_services,
            p.unique_beneficiaries,
            p.unique_procedures,
            CAST(p.avg_charge_per_service AS DECIMAL(10,2)) as avg_charge_per_service,
            CURRENT_DATE as load_date
        FROM provider_aggregates p
        LEFT JOIN {STAGING_SCHEMA}.rural_urban_codes r 
            ON p.zip_code = r.zip_code
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {ANALYTICS_SCHEMA}.provider_service_patterns").fetchone()[0]
    logger.info(f"Created provider service patterns for {count:,} providers")


def build_spending_analysis(con):
    """
    Build spending pattern analysis
    """
    logger.info("Building spending analysis...")
    
    con.execute(f"DROP TABLE IF EXISTS {ANALYTICS_SCHEMA}.spending_by_region")
    
    con.execute(f"""
        CREATE TABLE {ANALYTICS_SCHEMA}.spending_by_region AS
        WITH population_base AS (
            SELECT 
                state_name,
                state_fips,
                SUM(population_total) as total_population,
                SUM(population_65plus) as elderly_population
            FROM {STAGING_SCHEMA}.population
            GROUP BY state_name, state_fips
        ),
        va_spending_by_state AS (
            SELECT 
                state,
                SUM(expenditure_amount) as total_va_spending,
                COUNT(*) as county_count
            FROM {STAGING_SCHEMA}.va_spending
            GROUP BY state
        )
        SELECT 
            p.state_name,
            p.state_fips,
            p.total_population,
            p.elderly_population,
            COALESCE(v.total_va_spending, 0) as va_spending,
            COALESCE(v.county_count, 0) as counties_with_spending,
            CAST(COALESCE(v.total_va_spending, 0) / NULLIF(p.elderly_population, 0) AS DECIMAL(10,2)) as va_spending_per_elderly,
            CURRENT_DATE as load_date
        FROM population_base p
        LEFT JOIN va_spending_by_state v ON p.state_name = v.state
    """)
    
    count = con.execute(f"SELECT COUNT(*) FROM {ANALYTICS_SCHEMA}.spending_by_region").fetchone()[0]
    logger.info(f"Created spending analysis for {count:,} states")


def show_analytics_summary(con):
    """
    Show summary of analytics data
    """
    logger.info("\n" + "=" * 80)
    logger.info("ANALYTICS DATA SUMMARY")
    logger.info("=" * 80)
    
    tables = [
        "provider_network_summary",
        "rural_access_gaps",
        "provider_service_patterns",
        "spending_by_region"
    ]
    
    for table in tables:
        try:
            count = con.execute(f"SELECT COUNT(*) FROM {ANALYTICS_SCHEMA}.{table}").fetchone()[0]
            logger.info(f"{ANALYTICS_SCHEMA}.{table}: {count:,} records")
            
            # Show sample
            logger.info(f"  Sample columns:")
            cols = con.execute(f"DESCRIBE {ANALYTICS_SCHEMA}.{table}").fetchall()
            for col in cols[:5]:
                logger.info(f"    - {col[0]} ({col[1]})")
            if len(cols) > 5:
                logger.info(f"    ... and {len(cols) - 5} more columns")
            
        except Exception as e:
            logger.warning(f"{ANALYTICS_SCHEMA}.{table}: Error - {e}")
        
        logger.info("")


def main():
    """
    Main function to build analytics tables
    """
    logger.info("=" * 80)
    logger.info("BUILD ANALYTICS - Healthcare Provider Analysis")
    logger.info("=" * 80)
    logger.info(f"Database: {DUCKDB_PATH.absolute()}")
    logger.info("")
    
    try:
        # Connect to DuckDB
        con = duckdb.connect(str(DUCKDB_PATH))
        
        # Create schema
        create_analytics_schema(con)
        
        # Build analytics tables
        logger.info("\n1/4: Building provider network summary...")
        build_provider_network_summary(con)
        
        logger.info("\n2/4: Building rural access gaps...")
        build_rural_access_gaps(con)
        
        logger.info("\n3/4: Building provider service patterns...")
        build_provider_service_patterns(con)
        
        logger.info("\n4/4: Building spending analysis...")
        build_spending_analysis(con)
        
        # Show summary
        show_analytics_summary(con)
        
        # Close connection
        con.close()
        
        logger.info("=" * 80)
        logger.info("✓ Analytics pipeline complete!")
        logger.info("=" * 80)
        logger.info("\nNext steps:")
        logger.info("1. Explore data with SQL queries (see sql/analysis/ folder)")
        logger.info("2. Set up Apache Superset for visualization")
        logger.info("3. Create dashboards and insights")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Failed to build analytics: {e}")
        raise


if __name__ == "__main__":
    main()
