#!/usr/bin/env python
"""
Run the complete healthcare analytics pipeline

This script executes all ETL steps in sequence:
1. Download data
2. Load raw data
3. Transform to staging
4. Build analytics tables

Usage:
    python run_pipeline.py
"""

import sys
import subprocess
from pathlib import Path

def run_script(script_path, description):
    """
    Run a Python script and handle errors
    """
    print("\n" + "=" * 80)
    print(f"STEP: {description}")
    print("=" * 80 + "\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ {description} failed: {e}")
        return False


def main():
    print("\n" + "=" * 80)
    print("HEALTHCARE ANALYTICS PIPELINE")
    print("Full ETL execution")
    print("=" * 80)
    
    pipeline_root = Path(__file__).parent / "data_pipeline"
    
    steps = [
        (pipeline_root / "01_download_data.py", "Download datasets"),
        (pipeline_root / "02_load_raw.py", "Load raw data into DuckDB"),
        (pipeline_root / "03_transform_staging.py", "Transform to staging tables"),
        (pipeline_root / "04_build_analytics.py", "Build analytics tables"),
    ]
    
    results = []
    
    for script_path, description in steps:
        success = run_script(script_path, description)
        results.append((description, success))
        
        if not success:
            print("\n" + "=" * 80)
            print("PIPELINE FAILED")
            print("=" * 80)
            print(f"\nFailed at step: {description}")
            print("Please check the error messages above and fix any issues.")
            sys.exit(1)
    
    # Summary
    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)
    
    for description, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {description}")
    
    print("\n" + "=" * 80)
    print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Explore data with SQL queries (see sql/analysis/)")
    print("2. Set up Apache Superset for visualization")
    print("3. Create dashboards and insights")
    print("\nDatabase location: data/analytics.ddb")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
