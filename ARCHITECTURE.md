# Data Stack Architecture: Healthcare Provider & Beneficiary Utilization Analysis

## Project Overview
**Portfolio Project**: Public Health Provider Network & Rural Access Analysis  
**Tech Stack**: DuckDB + Apache Superset + Python  
**GitHub Repo**: Prishu1001

## Business Problem
Analyze provider referral patterns and beneficiary utilization to uncover:
- Healthcare access disparities (rural vs urban)
- Provider network efficiency and gaps
- Geographic distribution of VA and Medicare services
- Population-adjusted utilization rates

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES (Raw)                         │
├──────────────────────────────────────────────────────────────────┤
│  VA Facilities  │  VA Spending  │  CMS Medicare  │  RUCA  │ Census│
│     (JSON)      │    (CSV)      │     (CSV)      │ (XLSX) │ (CSV) │
└────────┬─────────────────┬────────────┬──────────┬────────┬───────┘
         │                 │            │          │        │
         │                 └────────────┴──────────┴────────┘
         │                              │
         │                    ┌─────────▼─────────┐
         │                    │  Python ETL Layer │
         │                    │  (data_pipeline/)  │
         │                    │                    │
         │                    │  • Download APIs   │
         │                    │  • Data cleaning   │
         │                    │  • Transformations │
         └────────────────────│  • Geocoding       │
                              │  • Standardization │
                              └─────────┬──────────┘
                                        │
                              ┌─────────▼──────────┐
                              │   DuckDB Database  │
                              │   (analytics.ddb)  │
                              │                    │
                              │  Schema:           │
                              │   • raw_*          │
                              │   • staging_*      │
                              │   • analytics_*    │
                              └─────────┬──────────┘
                                        │
                              ┌─────────▼──────────┐
                              │ Apache Superset    │
                              │ (Visualization)    │
                              │                    │
                              │  • Dashboards      │
                              │  • SQL Lab         │
                              │  • Charts          │
                              └────────────────────┘
```

---

## Data Sources Specification

### 1. VA Facilities (Core Network Data)
- **Source**: https://catalog.data.gov/dataset/va-facilities-api
- **Format**: JSON (API)
- **Key Fields**: 
  - Facility ID, Name, Type (Medical Center, Clinic, etc.)
  - Address, City, State, ZIP, Lat/Long
  - Services offered
- **Update Frequency**: Monthly
- **Volume**: ~2,000 facilities

### 2. VA Community Care Spending
- **Source**: https://catalog.data.gov/dataset/geographic-distribution-of-va-expenditures-fy2008
- **Format**: CSV
- **Key Fields**: 
  - State, County
  - Expenditure amount
  - Fiscal year
  - Program type
- **Update Frequency**: Annual
- **Volume**: ~3,000 county records per year

### 3. CMS Medicare Provider Utilization
- **Source**: https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners
- **Format**: CSV (multiple files)
- **Key Fields**: 
  - NPI, Provider name, credentials
  - Address, City, State, ZIP
  - HCPCS codes, service counts
  - Beneficiary counts, submitted charges
- **Update Frequency**: Annual
- **Volume**: ~1M provider records

### 4. RUCA Codes (Rural-Urban Classification)
- **Source**: https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/
- **Format**: XLSX/CSV
- **Key Fields**: 
  - ZIP code or Census tract
  - RUCA code (1-10)
  - Primary RUCA code
  - Secondary RUCA code
- **Update Frequency**: Periodic (Census-based)
- **Volume**: ~40,000 ZIP codes

### 5. Census Population Data
- **Source**: https://www.census.gov/data/datasets/time-series/demo/popest/2020s-counties-total.html
- **Format**: CSV
- **Key Fields**: 
  - State, County FIPS
  - Population estimates by year
  - Age breakdowns
- **Update Frequency**: Annual
- **Volume**: ~3,200 counties

---

## Database Schema (DuckDB)

### Layer 1: Raw Tables (Exact copy from sources)
```sql
-- Raw data as-is from sources
raw.va_facilities
raw.va_expenditures
raw.medicare_providers
raw.ruca_codes
raw.census_population
```

### Layer 2: Staging Tables (Cleaned & Standardized)
```sql
staging.facilities (
    facility_id VARCHAR PRIMARY KEY,
    facility_name VARCHAR,
    facility_type VARCHAR,
    address VARCHAR,
    city VARCHAR,
    state CHAR(2),
    zip_code VARCHAR(10),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    services ARRAY,
    load_date DATE
)

staging.va_spending (
    state CHAR(2),
    county_fips VARCHAR(5),
    county_name VARCHAR,
    fiscal_year INTEGER,
    program_type VARCHAR,
    expenditure_amount DECIMAL(15,2),
    load_date DATE
)

staging.medicare_utilization (
    npi VARCHAR(10) PRIMARY KEY,
    provider_name VARCHAR,
    credentials VARCHAR,
    gender VARCHAR(1),
    address VARCHAR,
    city VARCHAR,
    state CHAR(2),
    zip_code VARCHAR(10),
    hcpcs_code VARCHAR(10),
    hcpcs_description VARCHAR,
    service_count INTEGER,
    beneficiary_count INTEGER,
    submitted_charge DECIMAL(15,2),
    allowed_amount DECIMAL(15,2),
    year INTEGER,
    load_date DATE
)

staging.rural_urban_codes (
    zip_code VARCHAR(10) PRIMARY KEY,
    state CHAR(2),
    county_fips VARCHAR(5),
    ruca_primary INTEGER,
    ruca_secondary DECIMAL(3,1),
    classification VARCHAR(50),  -- Metro, Micropolitan, Small Town, Rural
    load_date DATE
)

staging.population (
    state_fips CHAR(2),
    county_fips VARCHAR(5) PRIMARY KEY,
    county_name VARCHAR,
    state_name VARCHAR,
    population_total INTEGER,
    population_65plus INTEGER,
    year INTEGER,
    load_date DATE
)
```

### Layer 3: Analytics Tables (Business Logic Applied)
```sql
analytics.provider_network_summary (
    state CHAR(2),
    county_fips VARCHAR(5),
    county_name VARCHAR,
    ruca_classification VARCHAR(50),
    population_total INTEGER,
    population_65plus INTEGER,
    va_facilities_count INTEGER,
    medicare_providers_count INTEGER,
    total_va_expenditure DECIMAL(15,2),
    total_medicare_spending DECIMAL(15,2),
    beneficiaries_per_provider DECIMAL(10,2),
    spending_per_capita DECIMAL(10,2),
    facility_per_100k DECIMAL(6,2)
)

analytics.rural_access_gaps (
    county_fips VARCHAR(5) PRIMARY KEY,
    county_name VARCHAR,
    state CHAR(2),
    ruca_classification VARCHAR(50),
    population_65plus INTEGER,
    nearest_va_distance_miles DECIMAL(8,2),
    medicare_providers_count INTEGER,
    access_score DECIMAL(5,2),  -- Composite metric
    priority_tier VARCHAR(20)    -- High, Medium, Low need
)

analytics.provider_service_patterns (
    npi VARCHAR(10),
    provider_name VARCHAR,
    specialty VARCHAR,
    state CHAR(2),
    ruca_classification VARCHAR(50),
    total_services INTEGER,
    unique_beneficiaries INTEGER,
    avg_charge_per_service DECIMAL(10,2),
    service_diversity_score DECIMAL(5,2)
)
```

---

## Technology Stack Details

### DuckDB (Analytical Database)
**Why DuckDB?**
- ✅ Embedded, serverless (no infrastructure setup)
- ✅ Fast analytical queries (columnar storage)
- ✅ Parquet support (efficient storage)
- ✅ SQL interface (familiar to analysts)
- ✅ Python integration (native library)
- ✅ Small footprint (single file database)

**Configuration:**
- Database file: `data/analytics.ddb`
- Memory limit: 4GB (configurable)
- Threads: Auto (use all CPU cores)
- Extensions: `httpfs` for remote data, `spatial` for geo-queries

### Apache Superset (Visualization Layer)
**Why Superset?**
- ✅ Open-source BI tool
- ✅ Rich visualization library
- ✅ SQL Lab for ad-hoc analysis
- ✅ Dashboard sharing capabilities
- ✅ DuckDB connector available

**Setup:**
- Docker-based deployment (easy setup)
- SQLAlchemy connection to DuckDB
- Pre-built dashboards for portfolio showcase

### Python (ETL & Orchestration)
**Key Libraries:**
- `duckdb` - Database interactions
- `pandas` - Data manipulation
- `requests` - API calls
- `openpyxl` - Excel file parsing
- `geopandas` (optional) - Spatial analysis

---

## Project Structure

```
prishu1001/
├── README.md                          # Project overview & quick start
├── ARCHITECTURE.md                    # This file
├── requirements.txt                   # Python dependencies
├── setup.sh                           # One-command setup script
├── .gitignore
│
├── data/                              # Data files (gitignored except samples)
│   ├── raw/                           # Downloaded source files
│   ├── processed/                     # Cleaned data
│   └── analytics.ddb                  # DuckDB database
│
├── data_pipeline/                     # ETL scripts
│   ├── __init__.py
│   ├── 01_download_data.py           # Download all datasets
│   ├── 02_load_raw.py                # Load into raw schema
│   ├── 03_transform_staging.py       # Clean & standardize
│   ├── 04_build_analytics.py         # Business logic layer
│   ├── config.py                      # Configuration settings
│   └── utils.py                       # Helper functions
│
├── sql/                               # SQL queries & schema
│   ├── schema/
│   │   ├── 01_create_raw_tables.sql
│   │   ├── 02_create_staging_tables.sql
│   │   └── 03_create_analytics_tables.sql
│   └── analysis/
│       ├── rural_access_analysis.sql
│       ├── provider_network_gaps.sql
│       └── spending_patterns.sql
│
├── superset/                          # Superset configuration
│   ├── docker-compose.yml
│   ├── superset_config.py
│   └── dashboards/
│       └── export_dashboards.json     # Pre-built dashboards
│
├── notebooks/                         # Jupyter notebooks for exploration
│   ├── 01_data_exploration.ipynb
│   ├── 02_rural_access_analysis.ipynb
│   └── 03_provider_patterns.ipynb
│
├── docs/                              # Documentation
│   ├── SETUP_GUIDE.md                 # Step-by-step setup
│   ├── DATA_DICTIONARY.md             # Field descriptions
│   └── ANALYSIS_EXAMPLES.md           # Sample queries & insights
│
└── tests/                             # Unit tests
    ├── test_etl.py
    └── test_data_quality.py
```

---

## Data Pipeline Flow

### Step 1: Data Acquisition
```python
# Downloads all 5 datasets
python data_pipeline/01_download_data.py
```
- VA Facilities: API call → JSON
- VA Spending: Direct download → CSV
- Medicare: CMS bulk download → multiple CSVs
- RUCA: Excel download → XLSX
- Census: API or CSV download

### Step 2: Load Raw Data
```python
# Loads into DuckDB raw schema
python data_pipeline/02_load_raw.py
```
- Create raw schema tables
- Load files as-is (minimal transformation)
- Add metadata columns (source, load_date)

### Step 3: Transform to Staging
```python
# Cleans & standardizes data
python data_pipeline/03_transform_staging.py
```
- Data type conversions
- Address parsing & geocoding
- ZIP code standardization
- RUCA code mapping
- Deduplication

### Step 4: Build Analytics Layer
```python
# Creates business metrics
python data_pipeline/04_build_analytics.py
```
- County-level aggregations
- Rural access calculations
- Provider network metrics
- Spending per capita
- Gap analysis

---

## Key Metrics & Analysis

### 1. Rural Access Score
Composite metric combining:
- Distance to nearest VA facility
- Medicare providers per 1,000 elderly population
- Average wait time (if available)
- Specialty availability

### 2. Network Efficiency
- Beneficiaries per provider ratio
- Geographic coverage (service area overlap)
- Referral pattern analysis

### 3. Spending Patterns
- VA expenditure vs Medicare spending by county
- Rural vs urban spending per capita
- High-cost service concentration

### 4. Geographic Disparities
- RUCA-based access comparison
- State-level variations
- Distance to care analysis

---

## Deployment & Showcase

### For GitHub Portfolio:
1. **README with visual appeal**: Charts, architecture diagram, sample insights
2. **Automated setup**: Single command to reproduce entire pipeline
3. **Jupyter notebooks**: Interactive exploration & storytelling
4. **SQL examples**: Demonstrated SQL skills for analytics roles
5. **Docker Superset**: Live dashboard screenshots or demo link

### Performance Targets:
- Full ETL pipeline: < 10 minutes
- Query response time: < 2 seconds
- Database size: ~500MB-1GB
- Memory usage: < 4GB

---

## Future Enhancements

1. **Real-time data**: Scheduled updates via GitHub Actions
2. **Machine learning**: Predict access gaps, demand forecasting
3. **Interactive maps**: Folium or Deck.gl integration
4. **API layer**: FastAPI for programmatic access
5. **dbt integration**: For data transformation lineage

---

## Technical Advantages for Portfolio

✅ **Modern data stack** (DuckDB as OLAP database)  
✅ **End-to-end ownership** (ingestion → analysis → visualization)  
✅ **Public health impact** (addresses real-world problem)  
✅ **Reproducible** (fully automated pipeline)  
✅ **Scalable** (can handle larger datasets)  
✅ **Cloud-ready** (easy to deploy on AWS/GCP)  

---

## Contact & Contributions
**Project by**: [Your Name]  
**GitHub**: https://github.com/Prishu1001  
**LinkedIn**: [Your Profile]

