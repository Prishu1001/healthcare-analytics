import duckdb

con = duckdb.connect('data/analytics.ddb')

print("\n" + "="*80)
print("DATABASE CONTENTS")
print("="*80)

# Show all schemas
print("\nSCHEMAS:")
schemas = con.execute("SELECT DISTINCT table_schema FROM information_schema.tables ORDER BY table_schema").fetchall()
for (schema,) in schemas:
    print(f"  - {schema}")

# Show all tables
print("\nALL TABLES:")
tables = con.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables 
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    ORDER BY table_schema, table_name
""").fetchall()

for schema, table in tables:
    try:
        count = con.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
        print(f"  ✓ {schema}.{table}: {count:,} rows")
    except Exception as e:
        print(f"  ✗ {schema}.{table}: Error - {str(e)[:50]}")

import os
print(f"\nDatabase file size: {os.path.getsize('data/analytics.ddb') / (1024*1024):.2f} MB")
con.close()
