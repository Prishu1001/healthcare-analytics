-- Provider Network Analysis Queries
-- Healthcare Provider Analytics Project

-- ============================================================================
-- 1. PROVIDER DENSITY BY STATE: Providers per 1000 elderly population
-- ============================================================================

SELECT 
    state_name,
    population_total,
    population_65plus,
    va_facilities_count,
    ROUND(pct_elderly, 2) as pct_elderly,
    ROUND(va_facilities_count * 100000.0 / NULLIF(population_65plus, 0), 2) as va_facilities_per_100k_elderly
FROM analytics.provider_network_summary
WHERE population_65plus > 50000
ORDER BY va_facilities_per_100k_elderly DESC
LIMIT 20;


-- ============================================================================
-- 2. COUNTIES WITH LARGEST 65+ POPULATIONS: High-impact areas
-- ============================================================================

SELECT 
    state_name,
    county_name,
    population_total,
    population_65plus,
    ROUND(pct_elderly, 1) as pct_elderly,
    va_facilities_count
FROM analytics.provider_network_summary
ORDER BY population_65plus DESC
LIMIT 50;


-- ============================================================================
-- 3. PROVIDER SERVICE DIVERSITY: Providers offering multiple specialties
-- ============================================================================

SELECT 
    state,
    ruca_classification,
    COUNT(DISTINCT npi) as provider_count,
    AVG(unique_procedures) as avg_procedures_per_provider,
    AVG(unique_beneficiaries) as avg_patients_per_provider,
    AVG(total_services) as avg_services_per_provider
FROM analytics.provider_service_patterns
GROUP BY state, ruca_classification
ORDER BY state, ruca_classification;


-- ============================================================================
-- 4. HIGH-VOLUME PROVIDERS: Top providers by service count
-- ============================================================================

SELECT 
    npi,
    provider_name,
    state,
    ruca_classification,
    total_services,
    unique_beneficiaries,
    unique_procedures,
    ROUND(total_services * 1.0 / NULLIF(unique_beneficiaries, 0), 1) as services_per_patient,
    ROUND(avg_charge_per_service, 2) as avg_charge
FROM analytics.provider_service_patterns
WHERE total_services > 0
ORDER BY total_services DESC
LIMIT 100;


-- ============================================================================
-- 5. RURAL PROVIDER SPECIALISTS: Providers in rural areas
-- ============================================================================

SELECT 
    state,
    COUNT(DISTINCT npi) as rural_providers,
    SUM(unique_beneficiaries) as total_rural_beneficiaries,
    AVG(unique_procedures) as avg_procedure_diversity,
    ROUND(AVG(avg_charge_per_service), 2) as avg_charge
FROM analytics.provider_service_patterns
WHERE ruca_classification = 'Rural'
GROUP BY state
HAVING COUNT(DISTINCT npi) > 100
ORDER BY rural_providers DESC;


-- ============================================================================
-- 6. PROVIDER CONCENTRATION INDEX: Evenness of provider distribution
-- ============================================================================

WITH state_provider_counts AS (
    SELECT 
        state,
        zip_code,
        COUNT(DISTINCT npi) as providers_in_zip
    FROM analytics.provider_service_patterns
    GROUP BY state, zip_code
)
SELECT 
    state,
    COUNT(DISTINCT zip_code) as zip_codes_with_providers,
    SUM(providers_in_zip) as total_providers,
    ROUND(AVG(providers_in_zip), 1) as avg_providers_per_zip,
    MAX(providers_in_zip) as max_providers_in_zip,
    ROUND(STDDEV(providers_in_zip), 1) as stddev_providers
FROM state_provider_counts
GROUP BY state
ORDER BY total_providers DESC
LIMIT 20;


-- ============================================================================
-- 7. PROVIDER GAPS BY COUNTY: Areas needing more providers
-- ============================================================================

WITH county_metrics AS (
    SELECT 
        p.state_name,
        p.county_name,
        p.population_65plus,
        COALESCE(COUNT(DISTINCT ps.npi), 0) as provider_count
    FROM analytics.provider_network_summary p
    LEFT JOIN staging.medicare_utilization ps 
        ON p.state_fips = ps.state  -- Simplified join
    WHERE p.population_65plus > 10000
    GROUP BY p.state_name, p.county_name, p.population_65plus
)
SELECT 
    state_name,
    county_name,
    population_65plus,
    provider_count,
    ROUND(provider_count * 1000.0 / NULLIF(population_65plus, 0), 2) as providers_per_1000_elderly,
    CASE 
        WHEN provider_count * 1000.0 / NULLIF(population_65plus, 0) < 5 THEN 'Critical Gap'
        WHEN provider_count * 1000.0 / NULLIF(population_65plus, 0) < 10 THEN 'Moderate Gap'
        ELSE 'Adequate'
    END as coverage_status
FROM county_metrics
WHERE provider_count * 1000.0 / NULLIF(population_65plus, 0) < 10
ORDER BY providers_per_1000_elderly ASC;


-- ============================================================================
-- 8. BENEFICIARY-TO-PROVIDER RATIO: Market saturation analysis
-- ============================================================================

SELECT 
    ruca_classification,
    COUNT(DISTINCT npi) as providers,
    SUM(unique_beneficiaries) as beneficiaries,
    ROUND(SUM(unique_beneficiaries) * 1.0 / NULLIF(COUNT(DISTINCT npi), 0), 1) as beneficiaries_per_provider,
    CASE 
        WHEN SUM(unique_beneficiaries) * 1.0 / NULLIF(COUNT(DISTINCT npi), 0) > 100 THEN 'Undersupplied'
        WHEN SUM(unique_beneficiaries) * 1.0 / NULLIF(COUNT(DISTINCT npi), 0) > 50 THEN 'Moderate'
        ELSE 'Well-supplied'
    END as market_status
FROM analytics.provider_service_patterns
GROUP BY ruca_classification
ORDER BY beneficiaries_per_provider DESC;


-- ============================================================================
-- 9. GEOGRAPHIC CLUSTERING: States with provider concentration
-- ============================================================================

WITH state_stats AS (
    SELECT 
        state,
        COUNT(DISTINCT npi) as providers,
        COUNT(DISTINCT zip_code) as zip_codes,
        SUM(unique_beneficiaries) as beneficiaries
    FROM analytics.provider_service_patterns
    GROUP BY state
)
SELECT 
    state,
    providers,
    zip_codes,
    beneficiaries,
    ROUND(providers * 1.0 / NULLIF(zip_codes, 0), 1) as providers_per_zip,
    ROUND(beneficiaries * 1.0 / NULLIF(providers, 0), 1) as beneficiaries_per_provider
FROM state_stats
ORDER BY providers DESC
LIMIT 20;


-- ============================================================================
-- 10. VA FACILITY COVERAGE: States with VA presence
-- ============================================================================

SELECT 
    state_name,
    SUM(va_facilities_count) as total_va_facilities,
    SUM(population_65plus) as elderly_population,
    ROUND(SUM(va_facilities_count) * 100000.0 / NULLIF(SUM(population_65plus), 0), 2) as va_per_100k_elderly
FROM analytics.provider_network_summary
GROUP BY state_name
HAVING SUM(va_facilities_count) > 0
ORDER BY va_per_100k_elderly DESC;


-- ============================================================================
-- 11. MULTI-STATE PROVIDERS: Providers operating across states
-- ============================================================================
-- Note: Requires provider-level analysis across states

SELECT 
    npi,
    provider_name,
    COUNT(DISTINCT state) as states_served,
    SUM(unique_beneficiaries) as total_beneficiaries,
    SUM(total_services) as total_services
FROM analytics.provider_service_patterns
GROUP BY npi, provider_name
HAVING COUNT(DISTINCT state) > 1
ORDER BY states_served DESC, total_services DESC
LIMIT 50;


-- ============================================================================
-- 12. EXPORT: Provider network summary for visualization
-- ============================================================================

COPY (
    SELECT 
        state_name,
        county_name,
        population_total,
        population_65plus,
        va_facilities_count,
        pct_elderly
    FROM analytics.provider_network_summary
    WHERE population_65plus > 5000
    ORDER BY state_name, county_name
) TO 'output/provider_network_export.csv' (HEADER, DELIMITER ',');
