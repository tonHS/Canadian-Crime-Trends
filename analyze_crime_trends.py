#!/usr/bin/env python3
"""
Canadian Crime Trends Analysis Script
======================================

Analyzes overall crime rate trends and retail crime in Canada using Statistics Canada data.

Data Sources:
- Table 35-10-0177-01: Incident-based crime statistics (Police-reported crime)
- Table 35-10-0062-01: Police-reported crime for selected offences and Criminal Code traffic violations by type of offence

Outputs:
1. Table: Top 10 violent Criminal Code violations in 2024 with growth metrics
2. Table: Top 10 Criminal Code property violations in 2024 with growth metrics
3. Visualizations: Shoplifting trends (under/over $5,000) for Criminal Code and Organized Crime

Author: tonHS
Date: 2025-11-21
"""

import pandas as pd
import numpy as np
import requests
import zipfile
from io import BytesIO
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import sys

# Configuration
DATA_DIR = Path('data')
OUTPUTS_DIR = Path('outputs')
FIGURES_DIR = Path('figures')

# Ensure directories exist
for directory in [DATA_DIR, OUTPUTS_DIR, FIGURES_DIR]:
    directory.mkdir(exist_ok=True)

# Styling constants
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#06A77D',
    'warning': '#D84315',
}

def print_header(title, char='='):
    """Print a formatted header"""
    line = char * 80
    print(f"\n{line}")
    print(f"{title.center(80)}")
    print(f"{line}\n")


def fetch_statcan_data(table_id, table_name="data"):
    """
    Fetch data from Statistics Canada table

    Args:
        table_id: Statistics Canada table ID (format: "35100177" without dashes)
        table_name: Descriptive name for the dataset

    Returns:
        pd.DataFrame: Loaded data or None if fetching fails
    """
    print(f"📥 Fetching {table_name} (Table {table_id})...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        # Method 1: Try the WDS API
        api_url = f"https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{table_id}/en"
        response = requests.get(api_url, headers=headers, timeout=60)

        if response.ok:
            zip_url = response.json()['object']
            zip_response = requests.get(zip_url, headers=headers, timeout=60)
            zip_response.raise_for_status()

            with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
                csv_files = [f for f in z.namelist() if f.endswith('.csv')]
                if not csv_files:
                    raise ValueError("No CSV file found in ZIP")

                df = pd.read_csv(z.open(csv_files[0]), low_memory=False)

        else:
            # Method 2: Try direct CSV download
            csv_url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{table_id}-eng.zip"
            response = requests.get(csv_url, headers=headers, timeout=60)
            response.raise_for_status()

            with zipfile.ZipFile(BytesIO(response.content)) as z:
                csv_files = [f for f in z.namelist() if f.endswith('.csv')]
                if not csv_files:
                    raise ValueError("No CSV file found in ZIP")

                df = pd.read_csv(z.open(csv_files[0]), low_memory=False)

        print(f"✓ Successfully loaded: {len(df):,} rows, {len(df.columns)} columns")

        # Save raw data
        output_path = DATA_DIR / f'{table_name.replace(" ", "_").lower()}_raw.csv'
        df.to_csv(output_path, index=False)
        print(f"✓ Saved to: {output_path}")

        return df

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print(f"   This may be due to network restrictions or API access issues")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def prepare_crime_data(df, data_type="general"):
    """
    Prepare and clean crime data

    Args:
        df: Raw crime data DataFrame
        data_type: Type of data ("general" or "organized")

    Returns:
        pd.DataFrame: Cleaned data
    """
    if df is None:
        return None

    print(f"🔧 Preparing {data_type} crime data...")

    df_clean = df.copy()

    # Convert REF_DATE to year
    if 'REF_DATE' in df_clean.columns:
        df_clean['Year'] = df_clean['REF_DATE'].astype(int)

    # Remove rows with missing values
    if 'VALUE' in df_clean.columns:
        df_clean = df_clean[df_clean['VALUE'].notna()]

    # Find violation column
    violation_col = None
    for col in df_clean.columns:
        if 'violation' in col.lower():
            violation_col = col
            break

    if violation_col:
        df_clean['violation_clean'] = df_clean[violation_col]
        print(f"✓ Found {df_clean['violation_clean'].nunique()} unique violation types")
    else:
        print("⚠ Warning: Could not find violation column")

    return df_clean


def analyze_violent_crimes(df, year=2024, top_n=10):
    """
    Analyze top violent Criminal Code violations

    Args:
        df: Cleaned crime data
        year: Year to analyze
        top_n: Number of top violations to return

    Returns:
        pd.DataFrame: Top violent crimes with growth metrics
    """
    print_header(f"ANALYZING TOP {top_n} VIOLENT CRIMES ({year})")

    if df is None:
        print("⚠ No data available")
        return None

    # Keywords for violent crimes
    violent_keywords = [
        'homicide', 'murder', 'assault', 'sexual', 'robbery', 'kidnapping',
        'abduction', 'extortion', 'criminal harassment', 'uttering threats',
        'discharge firearm', 'weapons offence', 'threatening', 'forcible'
    ]

    # Filter for violent crimes
    violation_col = 'violation_clean'
    if violation_col not in df.columns:
        print("⚠ Violation column not found")
        return None

    # Create mask for violent crimes
    mask = df[violation_col].str.lower().str.contains('|'.join(violent_keywords), na=False)
    df_violent = df[mask].copy()

    # Exclude totals
    df_violent = df_violent[~df_violent[violation_col].str.contains('Total', case=False, na=False)]

    print(f"Found {len(df_violent)} records for violent crimes")

    # Calculate statistics for target year
    df_year = df_violent[df_violent['Year'] == year]
    violations_year = df_year.groupby(violation_col)['VALUE'].sum().sort_values(ascending=False)

    # Get top N violations
    top_violations = violations_year.head(top_n)

    # Calculate growth metrics
    results = []
    for violation in top_violations.index:
        count_2024 = violations_year.get(violation, 0)

        # Get 2019 data (5-year comparison)
        df_2019 = df_violent[df_violent['Year'] == 2019]
        count_2019 = df_2019[df_2019[violation_col] == violation]['VALUE'].sum()

        # Get 2014 data (10-year comparison)
        df_2014 = df_violent[df_violent['Year'] == 2014]
        count_2014 = df_2014[df_2014[violation_col] == violation]['VALUE'].sum()

        # Calculate growth rates
        growth_5yr = ((count_2024 - count_2019) / count_2019 * 100) if count_2019 > 0 else np.nan
        growth_10yr = ((count_2024 - count_2014) / count_2014 * 100) if count_2014 > 0 else np.nan

        results.append({
            'Rank': len(results) + 1,
            'Violation': violation,
            f'{year} Count': int(count_2024),
            f'5-Year Growth (%)': growth_5yr,
            f'10-Year Growth (%)': growth_10yr
        })

    df_results = pd.DataFrame(results)

    # Save to CSV
    output_path = OUTPUTS_DIR / f'top_{top_n}_violent_crimes_{year}.csv'
    df_results.to_csv(output_path, index=False)
    print(f"\n✓ Results saved to: {output_path}")

    # Print formatted table
    print(f"\n{'='*80}")
    print(f"TOP {top_n} VIOLENT CRIMINAL CODE VIOLATIONS ({year})".center(80))
    print(f"{'='*80}\n")

    # Format for display
    df_display = df_results.copy()
    df_display[f'{year} Count'] = df_display[f'{year} Count'].apply(lambda x: f'{x:,}')
    df_display[f'5-Year Growth (%)'] = df_display[f'5-Year Growth (%)'].apply(
        lambda x: f'{x:+.1f}%' if not pd.isna(x) else 'N/A'
    )
    df_display[f'10-Year Growth (%)'] = df_display[f'10-Year Growth (%)'].apply(
        lambda x: f'{x:+.1f}%' if not pd.isna(x) else 'N/A'
    )

    print(df_display.to_string(index=False))
    print(f"\n{'='*80}\n")

    return df_results


def analyze_property_crimes(df, year=2024, top_n=10):
    """
    Analyze top property Criminal Code violations

    Args:
        df: Cleaned crime data
        year: Year to analyze
        top_n: Number of top violations to return

    Returns:
        pd.DataFrame: Top property crimes with growth metrics
    """
    print_header(f"ANALYZING TOP {top_n} PROPERTY CRIMES ({year})")

    if df is None:
        print("⚠ No data available")
        return None

    # Keywords for property crimes
    property_keywords = [
        'theft', 'break and enter', 'fraud', 'mischief', 'arson',
        'shoplifting', 'motor vehicle theft', 'possession of stolen',
        'break and enter', 'robbery', 'identity theft', 'identity fraud'
    ]

    violation_col = 'violation_clean'
    if violation_col not in df.columns:
        print("⚠ Violation column not found")
        return None

    # Create mask for property crimes
    mask = df[violation_col].str.lower().str.contains('|'.join(property_keywords), na=False)
    df_property = df[mask].copy()

    # Exclude totals
    df_property = df_property[~df_property[violation_col].str.contains('Total', case=False, na=False)]

    print(f"Found {len(df_property)} records for property crimes")

    # Calculate statistics for target year
    df_year = df_property[df_property['Year'] == year]
    violations_year = df_year.groupby(violation_col)['VALUE'].sum().sort_values(ascending=False)

    # Get top N violations
    top_violations = violations_year.head(top_n)

    # Calculate growth metrics
    results = []
    for violation in top_violations.index:
        count_2024 = violations_year.get(violation, 0)

        # Get 2019 data (5-year comparison)
        df_2019 = df_property[df_property['Year'] == 2019]
        count_2019 = df_2019[df_2019[violation_col] == violation]['VALUE'].sum()

        # Get 2014 data (10-year comparison)
        df_2014 = df_property[df_property['Year'] == 2014]
        count_2014 = df_2014[df_2014[violation_col] == violation]['VALUE'].sum()

        # Calculate growth rates
        growth_5yr = ((count_2024 - count_2019) / count_2019 * 100) if count_2019 > 0 else np.nan
        growth_10yr = ((count_2024 - count_2014) / count_2014 * 100) if count_2014 > 0 else np.nan

        results.append({
            'Rank': len(results) + 1,
            'Violation': violation,
            f'{year} Count': int(count_2024),
            f'5-Year Growth (%)': growth_5yr,
            f'10-Year Growth (%)': growth_10yr
        })

    df_results = pd.DataFrame(results)

    # Save to CSV
    output_path = OUTPUTS_DIR / f'top_{top_n}_property_crimes_{year}.csv'
    df_results.to_csv(output_path, index=False)
    print(f"\n✓ Results saved to: {output_path}")

    # Print formatted table
    print(f"\n{'='*80}")
    print(f"TOP {top_n} PROPERTY CRIMINAL CODE VIOLATIONS ({year})".center(80))
    print(f"{'='*80}\n")

    # Format for display
    df_display = df_results.copy()
    df_display[f'{year} Count'] = df_display[f'{year} Count'].apply(lambda x: f'{x:,}')
    df_display[f'5-Year Growth (%)'] = df_display[f'5-Year Growth (%)'].apply(
        lambda x: f'{x:+.1f}%' if not pd.isna(x) else 'N/A'
    )
    df_display[f'10-Year Growth (%)'] = df_display[f'10-Year Growth (%)'].apply(
        lambda x: f'{x:+.1f}%' if not pd.isna(x) else 'N/A'
    )

    print(df_display.to_string(index=False))
    print(f"\n{'='*80}\n")

    return df_results


def create_shoplifting_visualization(df_general, df_organized):
    """
    Create visualization comparing shoplifting trends

    Args:
        df_general: General crime data (from table 35-10-0177-01)
        df_organized: Organized crime data (from table 35-10-0062-01)
    """
    print_header("CREATING SHOPLIFTING TRENDS VISUALIZATION")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle('Shoplifting Trends in Canada:\nCriminal Code Violations vs Organized Crime',
                 fontsize=16, fontweight='bold', y=0.98)

    # Process Criminal Code shoplifting data
    if df_general is not None and 'violation_clean' in df_general.columns:
        print("📊 Processing Criminal Code shoplifting data...")

        violation_col = 'violation_clean'

        # Filter for shoplifting violations
        shoplifting_under = df_general[
            df_general[violation_col].str.contains('Shoplifting.*5,000 or under', case=False, na=False)
        ]
        shoplifting_over = df_general[
            df_general[violation_col].str.contains('Shoplifting.*over.*5,000', case=False, na=False)
        ]

        # Group by year
        under_5k = shoplifting_under.groupby('Year')['VALUE'].sum().sort_index()
        over_5k = shoplifting_over.groupby('Year')['VALUE'].sum().sort_index()

        # Plot Criminal Code violations
        if not under_5k.empty:
            ax1.plot(under_5k.index, under_5k.values, marker='o', linewidth=2.5,
                    markersize=8, label='Under $5,000', color=COLORS['primary'], zorder=3)
        if not over_5k.empty:
            ax1.plot(over_5k.index, over_5k.values, marker='s', linewidth=2.5,
                    markersize=8, label='Over $5,000', color=COLORS['secondary'], zorder=3)

        ax1.set_title('Criminal Code Violations', fontsize=14, fontweight='bold', pad=15)
        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Number of Incidents', fontsize=12, fontweight='bold')
        ax1.legend(fontsize=11, loc='best', framealpha=0.95)
        ax1.grid(True, alpha=0.3, linestyle='--', zorder=1)
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        ax1.set_facecolor('#F8F9FA')

        print(f"  ✓ Criminal Code: {len(under_5k) + len(over_5k)} data points")
    else:
        ax1.text(0.5, 0.5, 'Data Not Available', ha='center', va='center',
                transform=ax1.transAxes, fontsize=14, style='italic')
        ax1.set_title('Criminal Code Violations', fontsize=14, fontweight='bold', pad=15)

    # Process Organized Crime shoplifting data
    if df_organized is not None and 'violation_clean' in df_organized.columns:
        print("📊 Processing Organized Crime shoplifting data...")

        violation_col = 'violation_clean'

        # Filter for shoplifting violations
        org_shoplifting_under = df_organized[
            df_organized[violation_col].str.contains('Shoplifting.*5,000 or under', case=False, na=False)
        ]
        org_shoplifting_over = df_organized[
            df_organized[violation_col].str.contains('Shoplifting.*over.*5,000', case=False, na=False)
        ]

        # Group by year
        org_under_5k = org_shoplifting_under.groupby('Year')['VALUE'].sum().sort_index()
        org_over_5k = org_shoplifting_over.groupby('Year')['VALUE'].sum().sort_index()

        # Plot Organized Crime violations
        if not org_under_5k.empty:
            ax2.plot(org_under_5k.index, org_under_5k.values, marker='o', linewidth=2.5,
                    markersize=8, label='Under $5,000', color=COLORS['primary'], zorder=3)
        if not org_over_5k.empty:
            ax2.plot(org_over_5k.index, org_over_5k.values, marker='s', linewidth=2.5,
                    markersize=8, label='Over $5,000', color=COLORS['secondary'], zorder=3)

        ax2.set_title('Organized Crime', fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Number of Incidents', fontsize=12, fontweight='bold')
        ax2.legend(fontsize=11, loc='best', framealpha=0.95)
        ax2.grid(True, alpha=0.3, linestyle='--', zorder=1)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        ax2.set_facecolor('#F8F9FA')

        print(f"  ✓ Organized Crime: {len(org_under_5k) + len(org_over_5k)} data points")
    else:
        ax2.text(0.5, 0.5, 'Data Not Available', ha='center', va='center',
                transform=ax2.transAxes, fontsize=14, style='italic')
        ax2.set_title('Organized Crime', fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    # Save figure
    output_path = FIGURES_DIR / 'shoplifting_trends_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Visualization saved to: {output_path}")

    # Also save to root for easy access
    plt.savefig('shoplifting_trends_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')

    plt.close()

    return output_path


def main():
    """Main execution function"""

    print_header("CANADIAN CRIME TRENDS ANALYSIS", "=")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Author: tonHS\n")

    # Step 1: Fetch general crime data (35-10-0177-01)
    print_header("STEP 1: FETCHING GENERAL CRIME DATA")
    print("Table: 35-10-0177-01 (Incident-based crime statistics)")
    df_general_raw = fetch_statcan_data("35100177", "general_crime")
    df_general = prepare_crime_data(df_general_raw, "general")

    # Step 2: Fetch organized crime data (35-10-0062-01)
    print_header("STEP 2: FETCHING ORGANIZED CRIME DATA")
    print("Table: 35-10-0062-01 (Police-reported crime for selected offences)")
    df_organized_raw = fetch_statcan_data("35100062", "organized_crime")
    df_organized = prepare_crime_data(df_organized_raw, "organized")

    # Step 3: Analyze violent crimes
    print_header("STEP 3: ANALYZING VIOLENT CRIMES")
    df_violent_2024 = analyze_violent_crimes(df_general, year=2024, top_n=10)

    # Step 4: Analyze property crimes
    print_header("STEP 4: ANALYZING PROPERTY CRIMES")
    df_property_2024 = analyze_property_crimes(df_general, year=2024, top_n=10)

    # Step 5: Create shoplifting visualizations
    print_header("STEP 5: CREATING SHOPLIFTING VISUALIZATIONS")
    create_shoplifting_visualization(df_general, df_organized)

    # Summary
    print_header("ANALYSIS COMPLETE", "=")
    print("📁 Output Files:")
    print(f"   • {OUTPUTS_DIR}/")
    print(f"   • {FIGURES_DIR}/")
    print("\n✓ All analysis tasks completed successfully!")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
