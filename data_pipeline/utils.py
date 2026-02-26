"""
Utility functions for data pipeline
"""
import logging
import sys
from pathlib import Path
from typing import Optional
import requests
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def download_file(url: str, output_path: Path, chunk_size: int = 8192) -> bool:
    """
    Download a file from URL with progress bar
    
    Args:
        url: URL to download from
        output_path: Path to save the file
        chunk_size: Size of chunks to download
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Downloading from {url}")
        
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Stream download with progress bar
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_path.name) as pbar:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        
        logger.info(f"Successfully downloaded to {output_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error downloading {url}: {e}")
        return False


def check_file_exists(file_path: Path) -> bool:
    """
    Check if a file exists and has non-zero size
    
    Args:
        file_path: Path to check
        
    Returns:
        bool: True if file exists and has content
    """
    if file_path.exists() and file_path.stat().st_size > 0:
        logger.info(f"File already exists: {file_path}")
        return True
    return False


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to file
        
    Returns:
        float: File size in MB
    """
    if file_path.exists():
        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    return 0.0


def validate_csv_structure(file_path: Path, required_columns: Optional[list] = None) -> bool:
    """
    Validate CSV file structure
    
    Args:
        file_path: Path to CSV file
        required_columns: List of required column names
        
    Returns:
        bool: True if valid
    """
    try:
        import pandas as pd
        
        # Try reading first few rows
        df = pd.read_csv(file_path, nrows=5)
        
        if required_columns:
            missing_cols = set(required_columns) - set(df.columns)
            if missing_cols:
                logger.error(f"Missing columns in {file_path}: {missing_cols}")
                return False
        
        logger.info(f"CSV validation passed for {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to validate {file_path}: {e}")
        return False


def get_ruca_category(ruca_code: float) -> str:
    """
    Convert RUCA numeric code to simplified category
    
    Args:
        ruca_code: RUCA numeric code
        
    Returns:
        str: Category name (Metropolitan, Micropolitan, Small Town, Rural)
    """
    from data_pipeline.config import RUCA_SIMPLIFIED
    
    if ruca_code is None:
        return "Unknown"
    
    for category, codes in RUCA_SIMPLIFIED.items():
        if ruca_code in codes:
            return category
    
    return "Unknown"


def format_npi(npi: str) -> str:
    """
    Format NPI to standard 10-digit format
    
    Args:
        npi: NPI number as string
        
    Returns:
        str: Formatted NPI
    """
    if npi is None:
        return None
    
    # Remove any non-numeric characters
    npi_clean = ''.join(filter(str.isdigit, str(npi)))
    
    # Pad with zeros if needed
    return npi_clean.zfill(10) if npi_clean else None


def format_fips(state_fips: str, county_fips: str) -> str:
    """
    Format state and county FIPS into 5-digit code
    
    Args:
        state_fips: 2-digit state FIPS
        county_fips: 3-digit county FIPS
        
    Returns:
        str: 5-digit combined FIPS code
    """
    if state_fips is None or county_fips is None:
        return None
    
    state_str = str(state_fips).zfill(2)
    county_str = str(county_fips).zfill(3)
    
    return f"{state_str}{county_str}"


def clean_zip_code(zip_code: str) -> str:
    """
    Clean and standardize ZIP code to 5-digit format
    
    Args:
        zip_code: ZIP code string (may be ZIP+4 format)
        
    Returns:
        str: 5-digit ZIP code
    """
    if zip_code is None:
        return None
    
    # Convert to string and remove any non-numeric characters except hyphen
    zip_str = str(zip_code).strip()
    
    # Take first 5 digits
    zip_5 = ''.join(filter(str.isdigit, zip_str))[:5]
    
    return zip_5.zfill(5) if zip_5 else None


class ProgressLogger:
    """
    Simple progress logger for ETL operations
    """
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.description = description
        self.processed = 0
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def update(self, increment: int = 1):
        self.processed += increment
        if self.processed % 10000 == 0 or self.processed == self.total:
            pct = (self.processed / self.total) * 100 if self.total > 0 else 0
            self.logger.info(f"{self.description}: {self.processed:,}/{self.total:,} ({pct:.1f}%)")
    
    def finish(self):
        self.logger.info(f"{self.description}: Completed {self.processed:,} records")
