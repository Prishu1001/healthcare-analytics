# Data Dictionary - Healthcare Provider & Beneficiary Analytics

## Overview
This document describes all fields in the analytics database schemas.

---

## Raw Schema (`raw.*`)

### raw.va_facilities
Original VA facility data from ArcGIS API.

| Field | Type | Description |
|-------|------|-------------|
| StationID | VARCHAR | Unique facility identifier |
| StationName | VARCHAR | Facility name |
| StationType | VARCHAR | Type (Medical Center, Clinic, etc.) |
| address1 | VARCHAR | Street address |
| City | VARCHAR | City name |
| State | VARCHAR | State abbreviation |
| Zip | VARCHAR | ZIP code |
| latitude | DOUBLE | Latitude coordinate |
| longitude | DOUBLE | Longitude coordinate |
| Phone | VARCHAR | Contact phone number |
| load_date | DATE | Date loaded into database |

### raw.medicare_providers
CMS Medicare Provider Utilization and Payment Data.

| Field | Type | Description |
|-------|------|-------------|
| Rndrng_NPI | VARCHAR | National Provider Identifier (10 digits) |
| Rndrng_Prvdr_Last_Org_Name | VARCHAR | Provider last name or organization |
| Rndrng_Prvdr_First_Name | VARCHAR | Provider first name |
| Rndrng_Prvdr_Crdntls | VARCHAR | Credentials (MD, DO, NP, etc.) |
| Rndrng_Prvdr_Gndr | VARCHAR | Gender (M/F) |
| Rndrng_Prvdr_St1 | VARCHAR | Street address |
| Rndrng_Prvdr_City | VARCHAR | City |
| Rndrng_Prvdr_State_Abrvtn | VARCHAR | State (2-letter) |
| Rndrng_Prvdr_Zip5 | VARCHAR | 5-digit ZIP code |
| HCPCS_Cd | VARCHAR | Healthcare procedure code |
| HCPCS_Desc | VARCHAR | Procedure description |
| Tot_Srvcs | INTEGER | Total services provided |
| Tot_Benes | INTEGER | Total unique beneficiaries |
| Avg_Sbmtd_Chrg | DOUBLE | Average submitted charge |
| Avg_Mdcr_Alowd_Amt | DOUBLE | Average Medicare allowed amount |
| Avg_Mdcr_Pymt_Amt | DOUBLE | Average Medicare payment |
| load_date | DATE | Load timestamp |

### raw.ruca_codes
USDA Rural-Urban Commuting Area Codes by ZIP.

| Field | Type | Description |
|-------|------|-------------|
| ZIP_CODE | VARCHAR | 5-digit ZIP code |
| STATE | VARCHAR | State abbreviation |
| RUCA1 | DOUBLE | Primary RUCA code (1.0-10.6) |
| RUCA2 | DOUBLE | Secondary RUCA code |
| load_date | DATE | Load timestamp |

**RUCA Code Meanings:**
- 1.0-3.0: Metropolitan areas
- 4.0-6.0: Micropolitan areas
- 7.0-7.4: Small towns
- 8.0-10.6: Rural areas

### raw.census_population
U.S. Census Bureau County Population Estimates.

| Field | Type | Description |
|-------|------|-------------|
| SUMLEV | VARCHAR | Summary level (050 = county) |
| STATE | VARCHAR | State FIPS code (2 digits) |
| COUNTY | VARCHAR | County FIPS code (3 digits) |
| STNAME | VARCHAR | State name |
| CTYNAME | VARCHAR | County name |
| POPESTIMATE2023 | INTEGER | 2023 population estimate |
| Various age fields | INTEGER | Population by age group |
| load_date | DATE | Load timestamp |

### raw.va_expenditures
VA spending by geographic location.

| Field | Type | Description |
|-------|------|-------------|
| state | VARCHAR | State name |
| county | VARCHAR | County name |
| expenditure_amount | DOUBLE | Dollar amount spent |
| fiscal_year | INTEGER | Federal fiscal year |
| load_date | DATE | Load timestamp |

---

## Staging Schema (`staging.*`)

### staging.facilities
Cleaned VA facility locations.

| Field | Type | Description |
|-------|------|-------------|
| facility_id | VARCHAR | Unique identifier |
| facility_name | VARCHAR | Facility name |
| facility_type | VARCHAR | Type (standardized) |
| address | VARCHAR | Street address |
| city | VARCHAR | City |
| state | CHAR(2) | State abbreviation |
| zip_code | VARCHAR(10) | ZIP code |
| latitude | DECIMAL(10,6) | Latitude |
| longitude | DECIMAL(10,6) | Longitude |
| phone | VARCHAR | Phone number |
| load_date | DATE | Processing date |

### staging.medicare_utilization
Cleaned Medicare provider data.

| Field | Type | Description |
|-------|------|-------------|
| npi | VARCHAR(10) | National Provider Identifier |
| provider_name | VARCHAR | Full provider name |
| credentials | VARCHAR | Professional credentials |
| gender | VARCHAR(1) | M/F |
| address | VARCHAR | Street address |
| city | VARCHAR | City |
| state | VARCHAR(2) | State code |
| zip_code | VARCHAR(10) | ZIP code |
| hcpcs_code | VARCHAR(10) | Procedure code |
| hcpcs_description | VARCHAR | Procedure name |
| service_count | INTEGER | Number of services |
| beneficiary_count | INTEGER | Unique patients |
| submitted_charge | DOUBLE | Charge amount |
| allowed_amount | DOUBLE | Medicare allowed amount |
| year | INTEGER | Data year |
| load_date | DATE | Processing date |

### staging.rural_urban_codes
Standardized RUCA classifications.

| Field | Type | Description |
|-------|------|-------------|
| zip_code | VARCHAR(10) | 5-digit ZIP |
| state | CHAR(2) | State code |
| county_fips | VARCHAR(5) | 5-digit FIPS code |
| ruca_primary | INTEGER | Primary RUCA (1-10) |
| ruca_secondary | DECIMAL(3,1) | Secondary RUCA |
| classification | VARCHAR(50) | Simplified category |
| load_date | DATE | Processing date |

**Classification Values:**
- Metropolitan
- Micropolitan
- Small Town
- Rural

### staging.population
Standardized county population data.

| Field | Type | Description |
|-------|------|-------------|
| state_fips | CHAR(2) | State FIPS |
| county_fips | VARCHAR(5) | County FIPS (state+county) |
| county_name | VARCHAR | County name |
| state_name | VARCHAR | State name |
| population_total | INTEGER | Total population |
| population_65plus | INTEGER | Population age 65+ |
| year | INTEGER | Estimate year |
| load_date | DATE | Processing date |

### staging.va_spending
Cleaned VA expenditure data.

| Field | Type | Description |
|-------|------|-------------|
| state | VARCHAR | State name |
| county_fips | VARCHAR(5) | County FIPS code |
| county_name | VARCHAR | County name |
| fiscal_year | INTEGER | Federal fiscal year |
| program_type | VARCHAR | Program category |
| expenditure_amount | DOUBLE | Dollar amount |
| load_date | DATE | Processing date |

---

## Analytics Schema (`analytics.*`)

### analytics.provider_network_summary
County-level provider and facility metrics.

| Field | Type | Description | Business Logic |
|-------|------|-------------|----------------|
| state_fips | CHAR(2) | State FIPS code | From census |
| county_fips | VARCHAR(5) | County FIPS code | Primary key |
| county_name | VARCHAR | County name | From census |
| state_name | VARCHAR | State name | From census |
| population_total | INTEGER | Total population | From census |
| population_65plus | INTEGER | Medicare-eligible pop | From census |
| va_facilities_count | INTEGER | Number of VA facilities | Aggregated by county |
| pct_elderly | DECIMAL(5,2) | % Population 65+ | (pop_65+ / pop_total) * 100 |
| load_date | DATE | Analysis date | Current date |

**Key Uses:**
- Identify counties with low facility coverage
- Calculate providers per capita
- Geographic distribution analysis

### analytics.rural_access_gaps
ZIP-level rural healthcare access assessment.

| Field | Type | Description | Business Logic |
|-------|------|-------------|----------------|
| zip_code | VARCHAR(10) | ZIP code | From RUCA |
| state | CHAR(2) | State code | From RUCA |
| classification | VARCHAR(50) | Rural classification | From RUCA |
| ruca_primary | INTEGER | RUCA code | From RUCA |
| medicare_provider_count | INTEGER | Providers in ZIP | Count by ZIP |
| beneficiary_count | INTEGER | Patients in ZIP | Sum by ZIP |
| avg_charge_per_service | DOUBLE | Average charge | Mean charge |
| priority_tier | VARCHAR(20) | Access priority | Calculated field |
| load_date | DATE | Analysis date | Current date |

**Priority Tier Logic:**
- High Priority: Rural + <5 providers
- Medium Priority: Rural + <10 providers OR Small Town + <20
- Low Priority: All others

**Key Uses:**
- Identify underserved rural areas
- Target intervention areas
- Policy recommendations

### analytics.provider_service_patterns
Provider-level utilization and service metrics.

| Field | Type | Description | Business Logic |
|-------|------|-------------|----------------|
| npi | VARCHAR(10) | Provider NPI | From Medicare |
| provider_name | VARCHAR | Provider name | From Medicare |
| state | VARCHAR(2) | State | From Medicare |
| zip_code | VARCHAR(10) | ZIP code | From Medicare |
| ruca_classification | VARCHAR(50) | Area type | Joined from RUCA |
| total_services | INTEGER | Total services | Sum across HCPCS |
| unique_beneficiaries | INTEGER | Unique patients | Sum across HCPCS |
| unique_procedures | INTEGER | Distinct procedures | Count distinct HCPCS |
| avg_charge_per_service | DOUBLE | Average charge | Mean charge |
| load_date | DATE | Analysis date | Current date |

**Key Uses:**
- Provider productivity analysis
- Service diversity assessment
- Charge pattern analysis

### analytics.spending_by_region
State-level spending and population metrics.

| Field | Type | Description | Business Logic |
|-------|------|-------------|----------------|
| state_name | VARCHAR | State name | From census |
| state_fips | CHAR(2) | State FIPS | From census |
| total_population | INTEGER | State population | Sum counties |
| elderly_population | INTEGER | Population 65+ | Sum counties |
| va_spending | DOUBLE | Total VA spending | Sum expenditures |
| counties_with_spending | INTEGER | Counties with data | Count non-null |
| va_spending_per_elderly | DECIMAL(10,2) | Per capita spending | va_spending / elderly_pop |
| load_date | DATE | Analysis date | Current date |

**Key Uses:**
- State-level resource allocation
- VA vs Medicare comparison
- Budget planning

---

## Calculated Fields & Metrics

### Access Score
Composite metric for healthcare access (future enhancement).

**Components:**
- Provider density (providers per 1,000 elderly)
- Distance to nearest facility
- Specialist availability
- Wait time estimates

### Service Diversity Index
Measure of procedure variety offered by provider.

**Formula:**
```
diversity_score = unique_procedures / log(total_services + 1)
```

**Interpretation:**
- High score: Offers many different services
- Low score: Specialized in few procedures

### Network Efficiency Ratio
Beneficiaries per provider in an area.

**Formula:**
```
efficiency_ratio = total_beneficiaries / total_providers
```

**Thresholds:**
- < 50: Oversupplied (potential waste)
- 50-100: Well-balanced
- > 100: Undersupplied (access gap)

---

## Data Quality Notes

### Missing Values
- **Medicare data**: ZIP codes may be missing for privacy
- **VA spending**: Some counties have no expenditures
- **RUCA codes**: Some ZIP codes may lack classification

### Data Freshness
- **Census**: Annual updates
- **Medicare**: Annual releases (1-2 year lag)
- **VA Facilities**: Monthly updates
- **RUCA**: Decennial (Census-based)

### Known Limitations
1. ZIP codes don't perfectly align with county boundaries
2. Provider addresses may not reflect service locations
3. Spending data may not include all programs
4. RUCA classifications based on 2010 Census

---

## Glossary

| Term | Definition |
|------|------------|
| **NPI** | National Provider Identifier - unique 10-digit provider ID |
| **HCPCS** | Healthcare Common Procedure Coding System |
| **RUCA** | Rural-Urban Commuting Area classification |
| **FIPS** | Federal Information Processing Standards (county codes) |
| **Beneficiary** | Medicare-enrolled patient |
| **FFS** | Fee-For-Service (original Medicare) |
| **CMS** | Centers for Medicare & Medicaid Services |
| **VA** | Department of Veterans Affairs |

---

## References

- **CMS Data**: https://data.cms.gov
- **RUCA Documentation**: https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/documentation/
- **Census Data**: https://www.census.gov/data/developers/data-sets/popest-popproj.html
- **VA Data**: https://www.data.va.gov

---

*Last Updated: 2024*
