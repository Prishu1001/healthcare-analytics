# 🏥 Healthcare Provider & Beneficiary Utilization Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.9.2-yellow.svg)](https://duckdb.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **A comprehensive data analytics portfolio project examining healthcare access patterns, provider networks, and rural healthcare disparities using public health datasets.**

## 📊 Project Overview

This project analyzes provider referral patterns and beneficiary utilization to uncover critical insights about healthcare access, network efficiency, and rural impact across the United States. Built with modern data stack technologies (DuckDB + Apache Superset), it demonstrates end-to-end data engineering and analytics capabilities.

### Key Questions Addressed

- 🏥 **Healthcare Access**: Where are the gaps in rural healthcare access?
- 🗺️ **Geographic Disparities**: How does provider density vary by region?
- 💰 **Spending Patterns**: What is the relationship between VA spending and Medicare utilization?
- 👥 **Network Efficiency**: How many beneficiaries per provider in different areas?

### Demo Dashboard
> *Add screenshot of your Superset dashboard here*

---

## 🎯 Key Features

✅ **Automated ETL Pipeline** - Download, clean, and transform 5 public datasets  
✅ **DuckDB Analytics** - Fast SQL analytics on 1M+ provider records  
✅ **Rural Access Analysis** - RUCA-based classification of underserved areas  
✅ **Apache Superset** - Interactive dashboards and visualizations  
✅ **Reproducible** - Complete pipeline runs in < 10 minutes  
✅ **Production-Ready** - Modular design, error handling, logging  

---

## 📁 Project Structure

```
healthcare-analytics/
├── data_pipeline/              # ETL scripts
│   ├── 01_download_data.py    # Download datasets from sources
│   ├── 02_load_raw.py         # Load into DuckDB raw schema
│   ├── 03_transform_staging.py # Clean & standardize
│   ├── 04_build_analytics.py  # Create business metrics
│   ├── config.py              # Configuration settings
│   └── utils.py               # Helper functions
│
├── sql/                       # SQL queries
│   ├── schema/               # Table creation scripts
│   └── analysis/             # Analysis queries
│
├── superset/                  # Visualization setup
│   ├── docker-compose.yml    # Superset Docker config
│   └── superset_config.py    # Superset settings
│
├── notebooks/                 # Jupyter notebooks
│   └── data_exploration.ipynb
│
├── docs/                      # Documentation
│   ├── SETUP_GUIDE.md        # Step-by-step setup
│   ├── SUPERSET_SETUP.md     # Visualization guide
│   └── DATA_DICTIONARY.md    # Field descriptions
│
├── data/                      # Data files (gitignored)
│   ├── raw/                  # Downloaded source files
│   ├── processed/            # Cleaned data
│   └── analytics.ddb         # DuckDB database
│
├── ARCHITECTURE.md            # Technical architecture
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- 4GB RAM
- 2GB disk space

### Installation

```bash
# 1. Clone repository
git clone https://github.com/Prishu1001/healthcare-analytics.git
cd healthcare-analytics

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run complete pipeline
python data_pipeline/01_download_data.py
python data_pipeline/02_load_raw.py
python data_pipeline/03_transform_staging.py
python data_pipeline/04_build_analytics.py
```

**That's it!** You now have a fully populated DuckDB database ready for analysis.

---

## 📊 Data Sources

| Dataset | Source | Records | Description |
|---------|--------|---------|-------------|
| **VA Facilities** | [Data.gov](https://catalog.data.gov/dataset/va-facilities-api) | ~2,000 | Medical facilities locations & services |
| **VA Community Care** | [VA.gov](https://www.data.va.gov/dataset/Corporate-Data-Warehouse-CDW-/ftpi-epf7) | ~3,000 | Geographic spending distribution |
| **Medicare Providers** | [CMS.gov](https://data.cms.gov/provider-summary-by-type-of-service) | ~1M | Provider utilization & payment data |
| **RUCA Codes** | [USDA](https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes/) | ~40,000 | Rural-Urban classification by ZIP |
| **Census Population** | [Census.gov](https://www.census.gov/data/datasets/time-series/demo/popest/2020s-counties-total.html) | ~3,200 | County population estimates |

---

## 🔍 Sample Insights

### Finding 1: Rural Access Gaps
```sql
SELECT 
    state,
    COUNT(*) as underserved_zip_codes,
    SUM(beneficiary_count) as affected_beneficiaries
FROM analytics.rural_access_gaps
WHERE priority_tier = 'High Priority'
GROUP BY state
ORDER BY affected_beneficiaries DESC
LIMIT 10;
```

### Finding 2: Provider Concentration
```sql
SELECT 
    ruca_classification,
    COUNT(DISTINCT npi) as providers,
    AVG(unique_beneficiaries) as avg_patients_per_provider
FROM analytics.provider_service_patterns
GROUP BY ruca_classification;
```

### Finding 3: VA Spending vs Population
```sql
SELECT 
    state_name,
    elderly_population,
    va_spending_per_elderly,
    RANK() OVER (ORDER BY va_spending_per_elderly DESC) as spending_rank
FROM analytics.spending_by_region
WHERE elderly_population > 100000;
```

---

## 📈 Visualizations with Apache Superset

### Setup Superset (2 minutes)

```bash
cd superset
docker-compose up -d
```

Open http://localhost:8088 (admin/admin)

See full guide: [docs/SUPERSET_SETUP.md](docs/SUPERSET_SETUP.md)

### Recommended Dashboards

1. **Rural Access Overview** - Geographic heat map of underserved areas
2. **Provider Network Analysis** - Density metrics by county
3. **Spending Patterns** - VA & Medicare comparative analysis

---

## 🏗️ Architecture Highlights

### Tech Stack
- **DuckDB**: Columnar analytical database (fast, embedded)
- **Apache Superset**: Open-source BI platform
- **Python**: ETL orchestration & data processing
- **Pandas**: Data manipulation
- **Docker**: Containerized Superset deployment

### Data Pipeline
```
Raw Data → DuckDB (raw schema) → Staging (cleaned) → Analytics (metrics)
```

### Schema Design
- **Raw**: Unmodified source data
- **Staging**: Standardized, cleaned data
- **Analytics**: Business metrics, aggregations, derived fields

Full architecture: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 📝 Key Metrics Calculated

| Metric | Description | Use Case |
|--------|-------------|----------|
| **Rural Access Score** | Composite metric: distance + provider density | Identify underserved areas |
| **Provider per 1K elderly** | Medicare providers per 1,000 pop 65+ | Network adequacy |
| **VA spending per capita** | VA expenditure / elderly population | Resource allocation |
| **Service diversity index** | Unique HCPCS codes per provider | Specialty coverage |

---

## 🧪 Testing & Validation

```bash
# Run data quality checks
python tests/test_data_quality.py

# Check row counts
python tests/test_etl.py
```

---

## 📚 Documentation

- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed installation instructions
- **[Architecture](ARCHITECTURE.md)** - Technical design & data flow
- **[Superset Setup](docs/SUPERSET_SETUP.md)** - Visualization configuration
- **[Data Dictionary](docs/DATA_DICTIONARY.md)** - Field definitions

---

## 🎓 Learning Outcomes

This project demonstrates:

✅ **Data Engineering** - ETL pipeline design & implementation  
✅ **SQL Analytics** - Complex aggregations, window functions, CTEs  
✅ **Data Modeling** - Star schema, dimensional modeling  
✅ **Public Health Domain** - Healthcare metrics & terminology  
✅ **Modern Data Stack** - DuckDB, Superset, Docker  
✅ **Code Quality** - Modular design, logging, error handling  

---

## 🔮 Future Enhancements

- [ ] Machine learning: Predict future access gaps
- [ ] Time series analysis: Trend forecasting
- [ ] Interactive maps: Folium / Deck.gl integration
- [ ] REST API: FastAPI for programmatic access
- [ ] CI/CD: GitHub Actions for automated updates
- [ ] dbt integration: Data transformation lineage

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- **Data Sources**: CMS, VA, USDA, Census Bureau
- **Inspiration**: Public health data accessibility
- **Tools**: DuckDB, Apache Superset communities

---

## 📧 Contact

**Your Name** - [GitHub](https://github.com/Prishu1001) | [LinkedIn](https://linkedin.com/in/yourprofile)

**Project Link**: https://github.com/Prishu1001/healthcare-analytics

---

## 📊 Project Stats

![Lines of Code](https://img.shields.io/badge/Lines%20of%20Code-2000+-blue)
![Data Records](https://img.shields.io/badge/Records%20Processed-1M+-green)
![Database Size](https://img.shields.io/badge/Database%20Size-500MB-yellow)

---

<div align="center">
  <p>⭐ Star this repo if you found it helpful!</p>
  <p>Made with ❤️ for public health data transparency</p>
</div>
