-- Spending Pattern Analysis Queries
-- Healthcare Provider Analytics Project

-- ============================================================================
-- 1. VA SPENDING PER CAPITA BY STATE: Resource allocation efficiency
-- ============================================================================

SELECT 
    state_name,
    total_population,
    elderly_population,
    va_spending,
    va_spending_per_elderly,
    ROUND(va_spending * 1.0 / NULLIF(total_population, 0), 2) as va_spending_per_capita,
    counties_with_spending
FROM analytics.spending_by_region
WHERE va_spending > 0
ORDER BY va_spending_per_elderly DESC
LIMIT 20;


-- ============================================================================
-- 2. TOP SPENDING STATES: Highest total VA expenditure
-- ============================================================================

SELECT 
    state_name,
    va_spending,
    elderly_population,
    va_spending_per_elderly,
    RANK() OVER (ORDER BY va_spending DESC) as spending_rank
FROM analytics.spending_by_region
WHERE va_spending > 0
ORDER BY va_spending DESC
LIMIT 15;


-- ============================================================================
-- 3. SPENDING EFFICIENCY: Bang for buck analysis
-- ============================================================================

WITH spending_metrics AS (
    SELECT 
        s.state_name,
        s.va_spending,
        s.elderly_population,
        s.va_spending_per_elderly,
        COUNT(DISTINCT p.npi) as medicare_providers
    FROM analytics.spending_by_region s
    LEFT JOIN staging.medicare_utilization p 
        ON s.state_name = p.state
    WHERE s.va_spending > 0
    GROUP BY s.state_name, s.va_spending, s.elderly_population, s.va_spending_per_elderly
)
SELECT 
    state_name,
    va_spending,
    elderly_population,
    medicare_providers,
    va_spending_per_elderly,
    ROUND(va_spending / NULLIF(medicare_providers, 0), 2) as va_spending_per_provider,
    CASE 
        WHEN va_spending_per_elderly > 1000 THEN 'High Spending'
        WHEN va_spending_per_elderly > 500 THEN 'Moderate Spending'
        ELSE 'Low Spending'
    END as spending_category
FROM spending_metrics
ORDER BY va_spending_per_elderly DESC;


-- ============================================================================
-- 4. MEDICARE SPENDING PATTERNS: Average charges by rurality
-- ============================================================================

SELECT 
    ruca_classification,
    COUNT(DISTINCT npi) as providers,
    SUM(unique_beneficiaries) as beneficiaries,
    SUM(total_services) as services,
    ROUND(AVG(avg_charge_per_service), 2) as avg_charge_per_service,
    ROUND(SUM(total_services) * AVG(avg_charge_per_service), 2) as estimated_total_charges
FROM analytics.provider_service_patterns
WHERE avg_charge_per_service > 0
GROUP BY ruca_classification
ORDER BY avg_charge_per_service DESC;


-- ============================================================================
-- 5. HIGH-COST PROVIDERS: Providers with highest average charges
-- ============================================================================

SELECT 
    npi,
    provider_name,
    state,
    ruca_classification,
    total_services,
    unique_beneficiaries,
    ROUND(avg_charge_per_service, 2) as avg_charge,
    ROUND(total_services * avg_charge_per_service, 2) as estimated_total_revenue
FROM analytics.provider_service_patterns
WHERE total_services > 1000
    AND avg_charge_per_service > 0
ORDER BY avg_charge_per_service DESC
LIMIT 50;


-- ============================================================================
-- 6. SPENDING VARIANCE BY STATE: Identify outliers
-- ============================================================================

WITH state_charges AS (
    SELECT 
        state,
        AVG(avg_charge_per_service) as avg_state_charge,
        STDDEV(avg_charge_per_service) as stddev_charge,
        COUNT(DISTINCT npi) as provider_count
    FROM analytics.provider_service_patterns
    WHERE avg_charge_per_service > 0
    GROUP BY state
)
SELECT 
    state,
    ROUND(avg_state_charge, 2) as avg_charge,
    ROUND(stddev_charge, 2) as charge_variance,
    provider_count,
    ROUND((stddev_charge / NULLIF(avg_state_charge, 0)) * 100, 1) as coefficient_of_variation
FROM state_charges
WHERE provider_count > 100
ORDER BY coefficient_of_variation DESC;


-- ============================================================================
-- 7. VA VS MEDICARE SPENDING CORRELATION: State-level comparison
-- ============================================================================

WITH medicare_by_state AS (
    SELECT 
        state,
        SUM(total_services) as total_medicare_services,
        AVG(avg_charge_per_service) as avg_medicare_charge
    FROM analytics.provider_service_patterns
    GROUP BY state
)
SELECT 
    s.state_name,
    s.va_spending,
    s.va_spending_per_elderly,
    m.total_medicare_services,
    ROUND(m.avg_medicare_charge, 2) as avg_medicare_charge,
    ROUND(s.va_spending / NULLIF(m.total_medicare_services, 0), 4) as va_per_medicare_service
FROM analytics.spending_by_region s
LEFT JOIN medicare_by_state m ON s.state_name = m.state
WHERE s.va_spending > 0
ORDER BY va_per_medicare_service DESC;


-- ============================================================================
-- 8. SPENDING INTENSITY: Spending relative to population size
-- ============================================================================

SELECT 
    state_name,
    total_population,
    elderly_population,
    va_spending,
    ROUND((elderly_population * 100.0) / NULLIF(total_population, 0), 2) as pct_elderly,
    va_spending_per_elderly,
    CASE 
        WHEN va_spending_per_elderly > (SELECT AVG(va_spending_per_elderly) FROM analytics.spending_by_region) 
        THEN 'Above Average'
        ELSE 'Below Average'
    END as vs_national_avg
FROM analytics.spending_by_region
WHERE va_spending > 0
ORDER BY va_spending_per_elderly DESC;


-- ============================================================================
-- 9. RURAL SPENDING PREMIUM: Compare rural vs urban charges
-- ============================================================================

WITH rurality_spending AS (
    SELECT 
        CASE 
            WHEN ruca_classification IN ('Rural', 'Small Town') THEN 'Rural/Small Town'
            ELSE 'Urban/Metro'
        END as area_type,
        AVG(avg_charge_per_service) as avg_charge,
        COUNT(DISTINCT npi) as providers,
        SUM(unique_beneficiaries) as beneficiaries
    FROM analytics.provider_service_patterns
    WHERE avg_charge_per_service > 0
    GROUP BY area_type
)
SELECT 
    area_type,
    ROUND(avg_charge, 2) as avg_charge_per_service,
    providers,
    beneficiaries,
    ROUND(avg_charge - LAG(avg_charge) OVER (ORDER BY area_type), 2) as charge_difference
FROM rurality_spending
ORDER BY area_type;


-- ============================================================================
-- 10. TOTAL HEALTHCARE SPENDING ESTIMATE: National overview
-- ============================================================================

SELECT 
    'Total VA Spending' as metric,
    ROUND(SUM(va_spending), 2) as value,
    '$' as unit
FROM analytics.spending_by_region

UNION ALL

SELECT 
    'States with VA Spending',
    COUNT(*),
    'states'
FROM analytics.spending_by_region
WHERE va_spending > 0

UNION ALL

SELECT 
    'Average VA Spending per Elderly',
    ROUND(AVG(va_spending_per_elderly), 2),
    '$'
FROM analytics.spending_by_region
WHERE va_spending > 0

UNION ALL

SELECT 
    'Total Medicare Services',
    SUM(total_services),
    'services'
FROM analytics.provider_service_patterns

UNION ALL

SELECT 
    'Average Medicare Charge',
    ROUND(AVG(avg_charge_per_service), 2),
    '$'
FROM analytics.provider_service_patterns
WHERE avg_charge_per_service > 0;


-- ============================================================================
-- 11. SPENDING TRENDS: Identify growth opportunities
-- ============================================================================
-- Placeholder for multi-year analysis when historical data available

SELECT 
    state_name,
    va_spending,
    elderly_population,
    'Add year-over-year comparison when multi-year data available' as note
FROM analytics.spending_by_region
WHERE va_spending > 0
ORDER BY va_spending DESC
LIMIT 10;


-- ============================================================================
-- 12. EXPORT: Spending summary for visualization
-- ============================================================================

COPY (
    SELECT 
        state_name,
        total_population,
        elderly_population,
        va_spending,
        va_spending_per_elderly,
        counties_with_spending
    FROM analytics.spending_by_region
    WHERE va_spending > 0
    ORDER BY va_spending DESC
) TO 'output/spending_analysis_export.csv' (HEADER, DELIMITER ',');
