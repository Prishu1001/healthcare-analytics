import duckdb

con = duckdb.connect('data/analytics.ddb')

print("=" * 60)
print("DATABASE DIAGNOSTIC")
print("=" * 60)

# Check raw schema tables
print("\nTables in raw schema:")
try:
    tables = con.execute("SHOW TABLES FROM raw").fetchall()
    if tables:
        for table in tables:
            count = con.execute(f"SELECT COUNT(*) FROM raw.{table[0]}").fetchone()[0]
            print(f"  ✓ {table[0]}: {count:,} rows")
    else:
        print("  (no tables found)")
except Exception as e:
    print(f"  Error: {e}")

# Check what files exist in raw data folder
print("\nFiles in data/raw folder:")
import os
if os.path.exists('data/raw'):
    for file in os.listdir('data/raw'):
        size = os.path.getsize(f'data/raw/{file}') / (1024*1024)
        print(f"  - {file} ({size:.2f} MB)")
else:
    print("  (data/raw folder not found)")

con.close()

print("\n" + "=" * 60)
