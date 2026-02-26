# Apache Superset Setup Guide

## Overview
Apache Superset is an open-source data visualization and business intelligence tool. This guide will help you set up Superset to visualize the healthcare analytics data.

## Prerequisites
- Docker Desktop installed
- Completed data pipeline (analytics.ddb database created)
- Docker Compose

## Quick Start with Docker

### Step 1: Start Superset
```bash
cd superset
docker-compose up -d
```

This will:
- Pull the Apache Superset Docker image
- Create admin user (username: `admin`, password: `admin`)
- Start Superset on http://localhost:8088

### Step 2: Access Superset
1. Open browser to: http://localhost:8088
2. Login with:
   - Username: `admin`
   - Password: `admin`

**IMPORTANT**: Change the admin password after first login!

### Step 3: Connect DuckDB Database

1. Click **Settings** → **Database Connections** → **+ Database**
2. Select **Other** as database type
3. Configure connection:
   - **Display Name**: Healthcare Analytics
   - **SQLAlchemy URI**: 
     ```
     duckdb:////path/to/your/data/analytics.ddb
     ```
     Replace `/path/to/your/` with your actual path. On Windows use forward slashes:
     ```
     duckdb:///C:/Users/YourName/project/data/analytics.ddb
     ```

4. Click **Test Connection**
5. If successful, click **Connect**

### Step 4: Add Datasets

1. Click **Data** → **Datasets** → **+ Dataset**
2. Select **Healthcare Analytics** database
3. Select **analytics** schema
4. Add these tables:
   - `provider_network_summary`
   - `rural_access_gaps`
   - `provider_service_patterns`
   - `spending_by_region`

5. Click **Add** for each table

## Creating Your First Chart

### Example: Rural Access by State

1. Click **Charts** → **+ Chart**
2. Choose dataset: `rural_access_gaps`
3. Choose chart type: **Table** or **Bar Chart**
4. Configure:
   - **Dimensions**: `state`
   - **Metrics**: `COUNT(*)`
   - Group by: `priority_tier`

5. Click **Run Query**
6. Click **Save** to add to a dashboard

## Pre-built Dashboard Ideas

### Dashboard 1: Rural Access Overview
**Charts:**
1. **Map**: Counties by priority tier
2. **Bar Chart**: Top 10 underserved rural areas
3. **Table**: ZIP codes with < 5 providers
4. **KPI**: Total rural population without adequate access

### Dashboard 2: Provider Network Analysis
**Charts:**
1. **Scatter Plot**: Providers per 1000 elderly vs County population
2. **Heat Map**: Provider density by state
3. **Line Chart**: Provider trends over time
4. **Table**: Counties with provider gaps

### Dashboard 3: VA & Medicare Spending
**Charts:**
1. **Pie Chart**: Spending distribution by region
2. **Bar Chart**: Top 10 states by per-capita spending
3. **Comparison**: VA spending vs Medicare utilization
4. **Trend**: Spending growth by rural classification

## SQL Lab (Ad-hoc Analysis)

Use SQL Lab for custom queries:

```sql
-- Find rural areas with high need
SELECT 
    state,
    zip_code,
    classification,
    medicare_provider_count,
    beneficiary_count,
    priority_tier
FROM analytics.rural_access_gaps
WHERE priority_tier = 'High Priority'
ORDER BY beneficiary_count DESC
LIMIT 20;
```

```sql
-- Provider concentration by rural classification
SELECT 
    ruca_classification,
    COUNT(DISTINCT npi) as provider_count,
    SUM(unique_beneficiaries) as total_beneficiaries,
    AVG(avg_charge_per_service) as avg_charge
FROM analytics.provider_service_patterns
GROUP BY ruca_classification
ORDER BY provider_count DESC;
```

```sql
-- States with highest VA spending per elderly
SELECT 
    state_name,
    total_population,
    elderly_population,
    va_spending,
    va_spending_per_elderly
FROM analytics.spending_by_region
ORDER BY va_spending_per_elderly DESC
LIMIT 15;
```

## Troubleshooting

### DuckDB Connection Issues

**Error**: "Cannot connect to database"
- Ensure path to analytics.ddb is absolute
- Use forward slashes (/) even on Windows
- Check file permissions

**Solution for Windows**:
```
duckdb:///C:/Users/YourName/Data%20Quality%20Framework/data/analytics.ddb
```
Note: URL encode spaces as `%20`

### Container Won't Start

```bash
# Check logs
docker-compose logs superset

# Restart with fresh state
docker-compose down
docker volume rm superset_superset_data
docker-compose up -d
```

### DuckDB Driver Not Found

If Superset doesn't recognize DuckDB:

1. Access container:
```bash
docker exec -it healthcare_superset bash
```

2. Install DuckDB connector:
```bash
pip install duckdb-engine
```

3. Restart container:
```bash
docker-compose restart
```

## Alternative: Local Installation (Without Docker)

### Install Superset

```bash
# Create virtual environment
python -m venv superset_venv
source superset_venv/bin/activate  # On Windows: superset_venv\Scripts\activate

# Install Superset
pip install apache-superset
pip install duckdb-engine

# Initialize database
superset db upgrade

# Create admin user
superset fab create-admin

# Create default roles
superset init

# Start server
superset run -p 8088 --with-threads --reload --debugger
```

## Export Dashboards for GitHub

To share your dashboards:

```bash
# Export dashboard as JSON
docker exec healthcare_superset superset export-dashboards -f /tmp/dashboards.zip

# Copy to local machine
docker cp healthcare_superset:/tmp/dashboards.zip ./dashboards/export_dashboards.zip
```

Include screenshots in your README!

## Screenshots for Portfolio

Create these visualizations for your GitHub README:

1. **Rural Access Heat Map** - Geographic distribution
2. **Provider Density Chart** - Bar chart by state
3. **Spending Analysis Dashboard** - Multi-chart dashboard
4. **SQL Lab Query** - Show your SQL skills

Save as PNG and add to your repo's `docs/images/` folder.

## Security Notes

⚠️ **For Production Use**:
- Change default admin password immediately
- Set strong `SUPERSET_SECRET_KEY`
- Use environment variables for secrets
- Enable HTTPS
- Configure proper authentication (OAuth, LDAP)
- Set up database backups

## Resources

- [Superset Documentation](https://superset.apache.org/docs/intro)
- [DuckDB-Engine GitHub](https://github.com/Mause/duckdb_engine)
- [Chart Gallery](https://superset.apache.org/docs/creating-charts-dashboards/exploring-data)

---

**Next Steps**: Create your dashboards and take screenshots for your portfolio!
