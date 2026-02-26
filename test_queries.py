import duckdb

con = duckdb.connect('data/analytics.ddb')

print("\n" + "="*80)
print("SAMPLE ANALYTICS QUERIES")
print("="*80)

query = """
SELECT 
    state_name,
    COUNT(*) as total_counties,
    SUM(population_total) as total_population,
    SUM(population_65plus) as total_seniors,
    SUM(va_facilities_count) as va_facilities,
    ROUND(AVG(pct_elderly), 2) as avg_pct_elderly
FROM analytics.analytics.provider_network_summary
GROUP BY state_name
ORDER BY total_population DESC
LIMIT 10
"""

print("\nTop 10 States by Total Population:\n")
results = con.execute(query).fetchdf()
print(results.to_string(index=False))

print("\n" + "="*80)
print("\nVA Spending by State (Top 5):\n")
print("="*80)

query2 = """
SELECT 
    state_name,
    va_spending as total_va_spending,
    total_population as population,
    elderly_population as seniors,
    ROUND(va_spending_per_elderly, 2) as spending_per_senior,
    counties_with_spending as counties
FROM analytics.analytics.spending_by_region
ORDER BY va_spending DESC
LIMIT 5
"""

results2 = con.execute(query2).fetchdf()
print(results2.to_string(index=False))

con.close()
