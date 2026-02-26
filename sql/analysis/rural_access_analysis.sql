-- Rural Access Analysis Queries
-- Healthcare Provider Analytics Project

-- ============================================================================
-- 1. HIGH-PRIORITY RURAL AREAS: Find ZIP codes with critical access gaps
-- ============================================================================

SELECT 
    state,
    zip_code,
    classification as rural_classification,
    medicare_provider_count,
    beneficiary_count,
    priority_tier,
    ROUND(beneficiary_count / NULLIF(medicare_provider_count, 0), 1) as patients_per_provider
FROM analytics.rural_access_gaps
WHERE priority_tier = 'High Priority'
ORDER BY beneficiary_count DESC
LIMIT 50;


-- ============================================================================
-- 2. STATE-LEVEL RURAL ACCESS SUMMARY: Compare access by state
-- ============================================================================

SELECT 
    state,
    COUNT(*) as rural_zip_codes,
    SUM(CASE WHEN priority_tier = 'High Priority' THEN 1 ELSE 0 END) as high_priority_areas,
    SUM(beneficiary_count) as total_rural_beneficiaries,
    AVG(medicare_provider_count) as avg_providers_per_zip,
    ROUND(SUM(beneficiary_count) / NULLIF(SUM(medicare_provider_count), 0), 1) as beneficiaries_per_provider
FROM analytics.rural_access_gaps
WHERE classification IN ('Rural', 'Small Town')
GROUP BY state
ORDER BY high_priority_areas DESC;


-- ============================================================================
-- 3. RURAL CLASSIFICATION BREAKDOWN: Access metrics by rurality level
-- ============================================================================

SELECT 
    classification,
    COUNT(DISTINCT zip_code) as zip_codes,
    SUM(medicare_provider_count) as total_providers,
    SUM(beneficiary_count) as total_beneficiaries,
    ROUND(AVG(medicare_provider_count), 1) as avg_providers,
    ROUND(SUM(beneficiary_count) / NULLIF(SUM(medicare_provider_count), 0), 1) as beneficiaries_per_provider
FROM analytics.rural_access_gaps
GROUP BY classification
ORDER BY 
    CASE classification
        WHEN 'Rural' THEN 1
        WHEN 'Small Town' THEN 2
        WHEN 'Micropolitan' THEN 3
        WHEN 'Metropolitan' THEN 4
    END;


-- ============================================================================
-- 4. ZERO-PROVIDER RURAL AREAS: Critical gaps in coverage
-- ============================================================================

SELECT 
    state,
    zip_code,
    classification,
    beneficiary_count,
    priority_tier
FROM analytics.rural_access_gaps
WHERE medicare_provider_count = 0
    AND beneficiary_count > 0
ORDER BY beneficiary_count DESC
LIMIT 100;


-- ============================================================================
-- 5. RURAL VS URBAN COMPARISON: Access disparity analysis
-- ============================================================================

WITH category_stats AS (
    SELECT 
        CASE 
            WHEN classification IN ('Rural', 'Small Town') THEN 'Rural/Small Town'
            WHEN classification = 'Micropolitan' THEN 'Micropolitan'
            ELSE 'Metropolitan'
        END as area_type,
        zip_code,
        medicare_provider_count,
        beneficiary_count
    FROM analytics.rural_access_gaps
)
SELECT 
    area_type,
    COUNT(DISTINCT zip_code) as zip_codes,
    SUM(medicare_provider_count) as providers,
    SUM(beneficiary_count) as beneficiaries,
    ROUND(SUM(beneficiary_count) / NULLIF(SUM(medicare_provider_count), 0), 1) as beneficiaries_per_provider,
    ROUND(SUM(medicare_provider_count) * 1000.0 / NULLIF(SUM(beneficiary_count), 0), 2) as providers_per_1000_beneficiaries
FROM category_stats
GROUP BY area_type
ORDER BY area_type;


-- ============================================================================
-- 6. MOST UNDERSERVED COUNTIES: Identify priority intervention areas
-- ============================================================================

SELECT 
    p.state_name,
    p.county_name,
    p.population_65plus,
    COUNT(DISTINCT r.zip_code) as rural_zip_codes,
    SUM(r.medicare_provider_count) as total_providers,
    ROUND(SUM(r.medicare_provider_count) * 1000.0 / NULLIF(p.population_65plus, 0), 2) as providers_per_1000_elderly
FROM analytics.rural_access_gaps r
JOIN staging.population p 
    ON SUBSTRING(r.zip_code, 1, 5) = p.county_fips  -- Approximate join
WHERE r.classification = 'Rural'
GROUP BY p.state_name, p.county_name, p.population_65plus
HAVING SUM(r.medicare_provider_count) < 10
ORDER BY p.population_65plus DESC
LIMIT 30;


-- ============================================================================
-- 7. DISTANCE TO NEAREST VA FACILITY: Estimate for rural areas
-- ============================================================================
-- Note: This requires geographic calculations (future enhancement)

SELECT 
    'Analysis requires geospatial extension' as note,
    'Use PostGIS or DuckDB spatial extension for distance calculations' as recommendation;


-- ============================================================================
-- 8. TREND ANALYSIS: Change over time (if multi-year data available)
-- ============================================================================
-- Placeholder for temporal analysis when historical data is added

SELECT 
    state,
    classification,
    COUNT(*) as rural_areas,
    AVG(medicare_provider_count) as avg_providers,
    'Add year column for trend analysis' as note
FROM analytics.rural_access_gaps
WHERE classification = 'Rural'
GROUP BY state, classification
ORDER BY state;


-- ============================================================================
-- 9. EXPORT FOR VISUALIZATION: Top 100 underserved rural ZIP codes
-- ============================================================================

COPY (
    SELECT 
        zip_code,
        state,
        classification,
        medicare_provider_count,
        beneficiary_count,
        priority_tier,
        ROUND(beneficiary_count / NULLIF(medicare_provider_count, 1), 1) as patients_per_provider
    FROM analytics.rural_access_gaps
    WHERE priority_tier IN ('High Priority', 'Medium Priority')
    ORDER BY 
        CASE priority_tier 
            WHEN 'High Priority' THEN 1 
            ELSE 2 
        END,
        beneficiary_count DESC
    LIMIT 100
) TO 'output/rural_access_top100.csv' (HEADER, DELIMITER ',');


-- ============================================================================
-- 10. SUMMARY STATISTICS: Quick overview
-- ============================================================================

SELECT 
    'Total Rural ZIP Codes' as metric,
    COUNT(DISTINCT zip_code) as value
FROM analytics.rural_access_gaps
WHERE classification = 'Rural'

UNION ALL

SELECT 
    'High Priority Areas',
    COUNT(*)
FROM analytics.rural_access_gaps
WHERE priority_tier = 'High Priority'

UNION ALL

SELECT 
    'Total Rural Beneficiaries',
    SUM(beneficiary_count)
FROM analytics.rural_access_gaps
WHERE classification = 'Rural'

UNION ALL

SELECT 
    'Rural Areas with Zero Providers',
    COUNT(*)
FROM analytics.rural_access_gaps
WHERE medicare_provider_count = 0 AND classification = 'Rural';
