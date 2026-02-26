# Superset configuration for Healthcare Analytics project

import os

# Superset specific config
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088

# Security
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'change_this_in_production')
WTF_CSRF_ENABLED = True
WTF_CSRF_EXEMPT_LIST = []
WTF_CSRF_TIME_LIMIT = None

# Database connection
# Note: Update the path to your analytics.ddb file
SQLALCHEMY_DATABASE_URI = 'duckdb:////app/data/analytics.ddb'

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Custom branding (optional)
APP_NAME = "Healthcare Analytics"
