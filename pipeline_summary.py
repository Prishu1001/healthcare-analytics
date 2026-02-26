import duckdb
import os

con = duckdb.connect('data/analytics.ddb')

print("\n" + "="*80)
print("HEALTHCARE ANALYTICS DATABASE - PIPELINE SUCCESS")
print("="*80)

print("\n📊 RAW LAYER (5 tables):")
raw_tables = [
    ('census_population', '3,195 US counties with population data'),
    ('medicare_providers', '3 sample provider records'),
    ('ruca_codes', '5 Rural-Urban Commuting Area codes'),
    ('va_expenditures', '6 VA spending records by county'),
    ('va_facilities', '3 VA medical facility locations')
]
for table, desc in raw_tables:
    count = con.execute(f'SELECT COUNT(*) FROM raw.{table}').fetchone()[0]
    print(f"  ✓ {table}: {count:,} rows - {desc}")

print("\n🔄 STAGING LAYER (5 tables):")
staging_tables = [
    ('facilities', 'Cleaned VA facility data'),
    ('medicare_utilization', 'Provider utilization & payments'),
    ('population', 'County demographics'),
    ('rural_urban_codes', 'ZIP-level rural classifications'),
    ('va_spending', 'Standardized VA expenditures')
]
for table, desc in staging_tables:
    count = con.execute(f'SELECT COUNT(*) FROM staging.{table}').fetchone()[0]
    print(f"  ✓ {table}: {count:,} rows - {desc}")

print("\n📈 ANALYTICS LAYER (4 tables):")
analytics_tables = [
    ('provider_network_summary', 'County-level provider density metrics'),
    ('provider_service_patterns', 'Service utilization patterns by rurality'),
    ('rural_access_gaps', 'Healthcare access gap analysis'),
    ('spending_by_region', 'VA spending aggregated by geography')
]
for table, desc in analytics_tables:
    count = con.execute(f'SELECT COUNT(*) FROM analytics.analytics.{table}').fetchone()[0]
    print(f"  ✓ {table}: {count:,} rows - {desc}")

print(f"\n💾 Database size: {os.path.getsize('data/analytics.ddb') / (1024*1024):.2f} MB")
print(f"📍 Location: data/analytics.ddb")

print("\n" + "="*80)
print("NEXT STEPS:")
print("="*80)
print("1. Run SQL queries in sql/analysis/ folder")
print("2. Set up Apache Superset with Docker (see docs/SUPERSET_SETUP.md)")
print("3. Create dashboards to visualize:")
print("   - Rural vs urban healthcare access patterns")
print("   - Provider network density by county")
print("   - VA spending distribution")
print("   - Medicare utilization trends")
print("="*80)

con.close()
