# Step-by-Step Setup Guide

## Table of Contents
1. [Environment Setup](#1-environment-setup)
2. [Download Datasets](#2-download-datasets)
3. [Run ETL Pipeline](#3-run-etl-pipeline)
4. [Setup Visualization](#4-setup-visualization)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Environment Setup

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk Space**: 2GB free space
- **Docker**: Required for Superset (optional for core pipeline)

### Step 1.1: Install Python

**Windows:**
```powershell
# Download from python.org or use Microsoft Store
# Verify installation
python --version
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.11
python3 --version
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip python3-venv
python3 --version
```

### Step 1.2: Clone Repository

```bash
git clone https://github.com/Prishu1001/healthcare-analytics.git
cd healthcare-analytics
```

### Step 1.3: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal.

### Step 1.4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Expected packages:
- ✅ duckdb==0.9.2
- ✅ pandas>=2.0.0
- ✅ requests==2.31.0
- ✅ openpyxl>=3.0.0
- ✅ tqdm==4.66.1

Verify installation:
```bash
python -c "import duckdb; print('DuckDB version:', duckdb.__version__)"
```

---

## 2. Download Datasets

### Automated Downloads

Run the download script:
```bash
python data_pipeline/01_download_data.py
```

**What gets downloaded automatically:**
- ✅ VA Facilities (JSON from API)
- ✅ RUCA Codes (Excel file)
- ✅ Census Population (CSV)

**Expected output:**
```
Downloading VA Facilities data from ArcGIS API...
Downloaded 1,847 facilities so far...
Successfully saved 1,847 VA facilities

Downloading RUCA codes from USDA...
ruca_codes.xlsx: 100%|████████████| 2.1MB/2.1MB

Downloading Census population data...
census_population.csv: 100%|██████| 12.4MB/12.4MB

✓ Success: va_facilities
✓ Success: ruca_codes
✓ Success: census_population
```

### Manual Downloads (Required)

Some datasets require manual download due to data.gov redirect policies:

#### Medicare Provider Data (~2GB)
1. Visit: https://data.cms.gov/provider-summary-by-type-of-service/medicare-physician-other-practitioners/medicare-physician-other-practitioners-by-provider-and-service
2. Click **"Export"** → **"CSV"**
3. Save as: `medicare_providers_2022.csv`
4. Move to: `data/raw/medicare_providers_2022.csv`

#### VA Community Care Spending
1. Visit: https://www.data.va.gov/browse?category=Spending
2. Search for "Geographic Distribution" or "Community Care"
3. Download CSV file
4. Save as: `data/raw/va_expenditures_fy2008.csv`

**Alternative**: Use sample data for testing:
```bash
# The pipeline will run with sample data if these files are missing
# You can add real data later
```

### Verify Downloads

```bash
ls -lh data/raw/
```

Expected files:
```
va_facilities.json         (~500KB)
ruca_codes.xlsx           (~2MB)
census_population.csv     (~12MB)
medicare_providers_2022.csv (~2GB) - optional
va_expenditures_fy2008.csv (~5MB) - optional
```

---

## 3. Run ETL Pipeline

### Step 3.1: Load Raw Data

```bash
python data_pipeline/02_load_raw.py
```

This creates the DuckDB database and loads source data.

**Expected output:**
```
Loading VA Facilities data...
Loaded 1,847 VA facility records

Loading RUCA codes...
Loaded 42,741 RUCA code records

Loading Census population data...
Loaded 3,221 census population records

Database size: 125.43 MB
```

### Step 3.2: Transform to Staging

```bash
python data_pipeline/03_transform_staging.py
```

This cleans and standardizes the data.

**Expected output:**
```
Transforming VA facilities to staging...
Transformed 1,847 facility records

Transforming RUCA codes to staging...
Transformed 42,741 RUCA code records

Transforming Census population to staging...
Transformed 3,221 population records
```

### Step 3.3: Build Analytics Tables

```bash
python data_pipeline/04_build_analytics.py
```

This creates business metrics and aggregations.

**Expected output:**
```
Building provider network summary...
Created provider network summary with 3,221 counties

Building rural access gaps...
Created rural access gaps with 15,437 ZIP codes

Building provider service patterns...
Created provider service patterns for 742,381 providers

✓ Analytics pipeline complete!
```

### Verify Pipeline Success

```bash
# Connect to DuckDB and check data
python -c "
import duckdb
con = duckdb.connect('data/analytics.ddb')
print('Tables in analytics schema:')
for row in con.execute('SHOW TABLES FROM analytics').fetchall():
    print(f'  - {row[0]}')
con.close()
"
```

Expected output:
```
Tables in analytics schema:
  - provider_network_summary
  - rural_access_gaps
  - provider_service_patterns
  - spending_by_region
```

---

## 4. Setup Visualization

### Option A: Docker (Recommended)

**Prerequisites**: Docker Desktop installed

```bash
cd superset
docker-compose up -d
```

Wait 2-3 minutes for initialization, then:
1. Open browser: http://localhost:8088
2. Login: `admin` / `admin`
3. Change password (Settings → User Info)

**Connect Database:**
1. Settings → Database Connections → + Database
2. Display Name: `Healthcare Analytics`
3. SQLAlchemy URI: 
   ```
   duckdb:///C:/Users/YourName/healthcare-analytics/data/analytics.ddb
   ```
   (Use ABSOLUTE path with forward slashes)

4. Test Connection → Connect

**Add Datasets:**
- Data → Datasets → + Dataset
- Select each table from `analytics` schema:
  - provider_network_summary
  - rural_access_gaps
  - provider_service_patterns
  - spending_by_region

See detailed guide: [docs/SUPERSET_SETUP.md](SUPERSET_SETUP.md)

### Option B: Jupyter Notebooks

```bash
jupyter notebook notebooks/data_exploration.ipynb
```

Sample queries and visualizations included!

### Option C: DuckDB CLI

```bash
# Install DuckDB CLI
# Windows: Download from duckdb.org
# macOS: brew install duckdb
# Linux: apt install duckdb

# Connect to database
duckdb data/analytics.ddb

# Run queries
SELECT * FROM analytics.provider_network_summary LIMIT 5;
```

---

## 5. Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'duckdb'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "No such file or directory: data/raw/..."

**Solution:**
- Ensure you ran `01_download_data.py` first
- Check files exist in `data/raw/` folder
- For Medicare data, download manually (see Step 2)

### Issue: DuckDB "database is locked"

**Solution:**
```bash
# Close all Python processes
# On Windows:
taskkill /F /IM python.exe

# On macOS/Linux:
pkill -9 python
```

### Issue: Superset can't connect to DuckDB

**Solution:**
1. Use ABSOLUTE file path (not relative)
2. Use forward slashes `/` (even on Windows)
3. URL encode spaces: `%20`
4. Example: `duckdb:///C:/Users/Name/project/data/analytics.ddb`

### Issue: "Out of memory" during ETL

**Solution:**
```bash
# Process Medicare data in chunks
# Edit config.py and reduce batch size
# Or increase available RAM
```

### Issue: Permission denied on data/ folder

**Solution:**
```bash
# Windows (PowerShell as Admin):
icacls data /grant Users:F /T

# macOS/Linux:
chmod -R 755 data/
```

---

## Quick Reference Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\Activate.ps1  # Windows

# Run full pipeline
python data_pipeline/01_download_data.py
python data_pipeline/02_load_raw.py
python data_pipeline/03_transform_staging.py
python data_pipeline/04_build_analytics.py

# Start Superset
cd superset && docker-compose up -d

# Stop Superset
cd superset && docker-compose down

# Check database
python -c "import duckdb; con=duckdb.connect('data/analytics.ddb'); con.execute('SHOW TABLES').fetchall()"

# Deactivate virtual environment
deactivate
```

---

## Getting Help

1. **Check logs**: Each script prints detailed progress
2. **Read documentation**: See `docs/` folder
3. **Open issue**: [GitHub Issues](https://github.com/Prishu1001/healthcare-analytics/issues)
4. **Review architecture**: [ARCHITECTURE.md](../ARCHITECTURE.md)

---

## Next Steps

After successful setup:

1. ✅ Explore data with SQL queries (see `sql/analysis/`)
2. ✅ Create Superset dashboards (see `docs/SUPERSET_SETUP.md`)
3. ✅ Run Jupyter notebooks (see `notebooks/`)
4. ✅ Document your findings
5. ✅ Take screenshots for portfolio
6. ✅ Push to GitHub!

---

**Estimated Setup Time**: 30-45 minutes (excluding large file downloads)
