# ============================================================================
# CANADIAN CRIME STATISTICS ANALYZER - GOOGLE COLAB NOTEBOOK
# ============================================================================
# Data Source: Statistics Canada Table 35-10-0177-01
# Author: tonHS
#
# This notebook generates 5 PNG outputs:
# 1. Top 10 violent crimes by crime rate (2024)
# 2. Top 10 property crimes by crime rate (2024)
# 3. Top 10 other crimes by crime rate (2024)
# 4. Shoplifting under $5,000 crime rate trend (2000-2024)
# 5. Shoplifting over $5,000 crime rate trend (2000-2024)
# ============================================================================

# ============================================================================
# CELL 1: Install and Import Required Packages
# ============================================================================

# Uncomment if running in fresh Colab environment
# !pip install pandas numpy matplotlib requests

import pandas as pd
import numpy as np
import requests
import zipfile
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime

print("="*80)
print("CANADIAN CRIME METRICS GENERATOR")
print("="*80)
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Data Source: Statistics Canada Table 35-10-0177-01")
print("="*80)


# ============================================================================
# CELL 2: Define Helper Functions
# ============================================================================

def fetch_statcan_data(table_id, table_name="data"):
    """
    Fetch data from Statistics Canada table

    Args:
        table_id: Statistics Canada table ID (format: "35100177" without dashes)
        table_name: Descriptive name for the dataset

    Returns:
        pd.DataFrame: Loaded data or None if fetching fails
    """
    print(f"\n📥 Fetching {table_name} (Table {table_id})...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        # Try the WDS API
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
            # Fallback: Try direct CSV download
            csv_url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{table_id}-eng.zip"
            response = requests.get(csv_url, headers=headers, timeout=60)
            response.raise_for_status()

            with zipfile.ZipFile(BytesIO(response.content)) as z:
                csv_files = [f for f in z.namelist() if f.endswith('.csv')]
                if not csv_files:
                    raise ValueError("No CSV file found in ZIP")

                df = pd.read_csv(z.open(csv_files[0]), low_memory=False)

        print(f"✓ Successfully loaded: {len(df):,} rows, {len(df.columns)} columns")
        return df

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def create_table_as_png(data, title, filename, figsize=(14, 10)):
    """
    Create a table visualization and save as PNG

    Args:
        data: DataFrame with table data
        title: Title for the table
        filename: Output filename
        figsize: Figure size tuple
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('tight')
    ax.axis('off')

    # Create table
    table = ax.table(cellText=data.values,
                     colLabels=data.columns,
                     cellLoc='left',
                     loc='center',
                     bbox=[0, 0, 1, 1])

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Header styling
    for i in range(len(data.columns)):
        cell = table[(0, i)]
        cell.set_facecolor('#2E86AB')
        cell.set_text_props(weight='bold', color='white', fontsize=11)

    # Alternating row colors
    for i in range(1, len(data) + 1):
        for j in range(len(data.columns)):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#F9F9F9')
            else:
                cell.set_facecolor('#FFFFFF')

    # Add title
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✓ Saved: {filename}")


def get_crime_rate_data(df, violation_name, year, stats_col):
    """Get crime rate for a specific violation and year"""
    if stats_col:
        mask = (df['Violation'] == violation_name) & \
               (df['Year'] == year) & \
               (df[stats_col].str.contains('rate', case=False, na=False))
    else:
        # Fallback: assume all data is rate
        mask = (df['Violation'] == violation_name) & (df['Year'] == year)

    result = df[mask]['VALUE'].sum()
    return result


# ============================================================================
# CELL 3: Fetch Data from Statistics Canada
# ============================================================================

print("\n" + "="*80)
print("FETCHING DATA FROM STATISTICS CANADA")
print("="*80)

# Fetch the crime data
df_raw = fetch_statcan_data("35100177", "Crime Statistics")

if df_raw is None:
    raise Exception("Failed to fetch data. Please check your internet connection.")


# ============================================================================
# CELL 4: Prepare and Clean Data
# ============================================================================

print("\n" + "="*80)
print("PREPARING AND CLEANING DATA")
print("="*80)

# Create cleaned version
df = df_raw.copy()

# Convert REF_DATE to year
if 'REF_DATE' in df.columns:
    df['Year'] = df['REF_DATE'].astype(int)
    print(f"✓ Years available: {df['Year'].min()} to {df['Year'].max()}")

# Remove rows with missing values
df = df[df['VALUE'].notna()]

# Find violation column
violation_col = None
for col in df.columns:
    if 'violation' in col.lower():
        violation_col = col
        break

if violation_col:
    df['Violation'] = df[violation_col]
    print(f"✓ Found {df['Violation'].nunique()} unique violation types")
else:
    raise Exception("Could not find violation column")

# Find statistics type column (to distinguish rate vs actual)
stats_col = None
for col in df.columns:
    if 'statistic' in col.lower():
        stats_col = col
        break

if stats_col:
    print(f"✓ Statistics types available: {df[stats_col].unique()}")
else:
    print("⚠ Warning: Could not find statistics column")

# Filter for rate-based statistics only (as required)
if stats_col:
    df = df[df[stats_col].str.contains('rate', case=False, na=False)].copy()
    print(f"✓ Filtered to rate-based statistics only: {len(df):,} rows")

print(f"✓ Data preparation complete")


# ============================================================================
# CELL 5: Generate Top 10 Violent Crimes Table (by Crime Rate)
# ============================================================================

print("\n" + "="*80)
print("GENERATING TOP 10 VIOLENT CRIMES TABLE")
print("="*80)

# Keywords for violent crimes
violent_keywords = [
    'homicide', 'murder', 'assault', 'sexual', 'robbery', 'kidnapping',
    'abduction', 'extortion', 'criminal harassment', 'uttering threats',
    'discharge firearm', 'weapons', 'threatening', 'forcible'
]

# Filter for violent crimes in 2024
mask_violent = df['Violation'].str.lower().str.contains('|'.join(violent_keywords), na=False)
mask_violent = mask_violent & ~df['Violation'].str.contains('Total', case=False, na=False)
mask_violent = mask_violent & (df['Year'] == 2024)

df_violent_2024 = df[mask_violent].copy()
violent_2024 = df_violent_2024.groupby('Violation')['VALUE'].sum().sort_values(ascending=False)

# Get top 10
top_10_violent = violent_2024.head(10)

# Calculate growth metrics
violent_results = []
for idx, (violation, rate_2024) in enumerate(top_10_violent.items(), 1):
    # Get historical data
    rate_2019 = get_crime_rate_data(df, violation, 2019, stats_col)
    rate_2014 = get_crime_rate_data(df, violation, 2014, stats_col)

    # Calculate growth
    growth_5yr = ((rate_2024 - rate_2019) / rate_2019 * 100) if rate_2019 > 0 else np.nan
    growth_10yr = ((rate_2024 - rate_2014) / rate_2014 * 100) if rate_2014 > 0 else np.nan

    violent_results.append({
        'Rank': idx,
        'Violation': violation[:60],  # Truncate long names
        '2024 Rate': f'{rate_2024:,.2f}',
        'Growth from 2019 (%)': f'{growth_5yr:+.1f}%' if not pd.isna(growth_5yr) else 'N/A',
        'Growth from 2014 (%)': f'{growth_10yr:+.1f}%' if not pd.isna(growth_10yr) else 'N/A'
    })

df_violent_table = pd.DataFrame(violent_results)
create_table_as_png(
    df_violent_table,
    'Top 10 Violent Criminal Code Violations in 2024 (by Crime Rate)',
    '01_top10_violent_crimes_by_rate.png'
)


# ============================================================================
# CELL 6: Generate Top 10 Property Crimes Table (by Crime Rate)
# ============================================================================

print("\n" + "="*80)
print("GENERATING TOP 10 PROPERTY CRIMES TABLE")
print("="*80)

# Keywords for property crimes
property_keywords = [
    'theft', 'break and enter', 'fraud', 'mischief', 'arson',
    'shoplifting', 'motor vehicle theft', 'possession of stolen',
    'identity theft', 'identity fraud'
]

# Filter for property crimes in 2024
mask_property = df['Violation'].str.lower().str.contains('|'.join(property_keywords), na=False)
mask_property = mask_property & ~df['Violation'].str.contains('Total', case=False, na=False)
mask_property = mask_property & (df['Year'] == 2024)

df_property_2024 = df[mask_property].copy()
property_2024 = df_property_2024.groupby('Violation')['VALUE'].sum().sort_values(ascending=False)

# Get top 10
top_10_property = property_2024.head(10)

# Calculate growth metrics
property_results = []
for idx, (violation, rate_2024) in enumerate(top_10_property.items(), 1):
    # Get historical data
    rate_2019 = get_crime_rate_data(df, violation, 2019, stats_col)
    rate_2014 = get_crime_rate_data(df, violation, 2014, stats_col)

    # Calculate growth
    growth_5yr = ((rate_2024 - rate_2019) / rate_2019 * 100) if rate_2019 > 0 else np.nan
    growth_10yr = ((rate_2024 - rate_2014) / rate_2014 * 100) if rate_2014 > 0 else np.nan

    property_results.append({
        'Rank': idx,
        'Violation': violation[:60],
        '2024 Rate': f'{rate_2024:,.2f}',
        'Growth from 2019 (%)': f'{growth_5yr:+.1f}%' if not pd.isna(growth_5yr) else 'N/A',
        'Growth from 2014 (%)': f'{growth_10yr:+.1f}%' if not pd.isna(growth_10yr) else 'N/A'
    })

df_property_table = pd.DataFrame(property_results)
create_table_as_png(
    df_property_table,
    'Top 10 Criminal Code Property Violations in 2024 (by Crime Rate)',
    '02_top10_property_crimes_by_rate.png'
)


# ============================================================================
# CELL 7: Generate Top 10 Other Criminal Code Violations (by Crime Rate)
# ============================================================================

print("\n" + "="*80)
print("GENERATING TOP 10 OTHER CRIMINAL CODE VIOLATIONS TABLE")
print("="*80)

# Exclude violent and property crimes to get "other"
all_keywords = violent_keywords + property_keywords

mask_other = ~df['Violation'].str.lower().str.contains('|'.join(all_keywords), na=False)
mask_other = mask_other & ~df['Violation'].str.contains('Total', case=False, na=False)
mask_other = mask_other & (df['Year'] == 2024)

df_other_2024 = df[mask_other].copy()
other_2024 = df_other_2024.groupby('Violation')['VALUE'].sum().sort_values(ascending=False)

# Get top 10
top_10_other = other_2024.head(10)

# Calculate growth metrics
other_results = []
for idx, (violation, rate_2024) in enumerate(top_10_other.items(), 1):
    # Get historical data
    rate_2019 = get_crime_rate_data(df, violation, 2019, stats_col)
    rate_2014 = get_crime_rate_data(df, violation, 2014, stats_col)

    # Calculate growth
    growth_5yr = ((rate_2024 - rate_2019) / rate_2019 * 100) if rate_2019 > 0 else np.nan
    growth_10yr = ((rate_2024 - rate_2014) / rate_2014 * 100) if rate_2014 > 0 else np.nan

    other_results.append({
        'Rank': idx,
        'Violation': violation[:60],
        '2024 Rate': f'{rate_2024:,.2f}',
        'Growth from 2019 (%)': f'{growth_5yr:+.1f}%' if not pd.isna(growth_5yr) else 'N/A',
        'Growth from 2014 (%)': f'{growth_10yr:+.1f}%' if not pd.isna(growth_10yr) else 'N/A'
    })

df_other_table = pd.DataFrame(other_results)
create_table_as_png(
    df_other_table,
    'Top 10 Other Criminal Code Violations in 2024 (by Crime Rate)',
    '03_top10_other_crimes_by_rate.png'
)


# ============================================================================
# CELL 8: Generate Shoplifting Under $5,000 Line Graph (by Crime Rate)
# ============================================================================

print("\n" + "="*80)
print("GENERATING SHOPLIFTING UNDER $5,000 LINE GRAPH")
print("="*80)

# Find shoplifting under $5,000 violations
shoplifting_under_pattern = r'Shoplifting.*5,?000.*or under|Shoplifting.*under.*5,?000'

# Get yearly crime rate data for shoplifting under $5,000
years = list(range(2000, 2025))
under_rates = []

for year in years:
    df_year = df[df['Year'] == year]
    mask_under = df_year['Violation'].str.contains(shoplifting_under_pattern, case=False, na=False, regex=True)
    rate_under = df_year[mask_under]['VALUE'].sum()
    under_rates.append(rate_under)

# Create line graph
fig, ax = plt.subplots(figsize=(14, 8))
ax.plot(years, under_rates, marker='o', linewidth=2.5, markersize=8,
        color='#2E86AB', label='Shoplifting under $5,000')
ax.set_title('Criminal Code: Shoplifting under $5,000 Crime Rate (2000-2024)',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Crime Rate (per 100,000 population)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=12)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.1f}'))
ax.set_facecolor('#F8F9FA')
plt.tight_layout()
plt.savefig('04_shoplifting_under_5000_rate.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 04_shoplifting_under_5000_rate.png")


# ============================================================================
# CELL 9: Generate Shoplifting Over $5,000 Line Graph (by Crime Rate)
# ============================================================================

print("\n" + "="*80)
print("GENERATING SHOPLIFTING OVER $5,000 LINE GRAPH")
print("="*80)

# Find shoplifting over $5,000 violations
shoplifting_over_pattern = r'Shoplifting.*over.*5,?000'

# Get yearly crime rate data for shoplifting over $5,000
over_rates = []

for year in years:
    df_year = df[df['Year'] == year]
    mask_over = df_year['Violation'].str.contains(shoplifting_over_pattern, case=False, na=False, regex=True)
    rate_over = df_year[mask_over]['VALUE'].sum()
    over_rates.append(rate_over)

# Create line graph
fig, ax = plt.subplots(figsize=(14, 8))
ax.plot(years, over_rates, marker='s', linewidth=2.5, markersize=8,
        color='#A23B72', label='Shoplifting over $5,000')
ax.set_title('Criminal Code: Shoplifting over $5,000 Crime Rate (2000-2024)',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Crime Rate (per 100,000 population)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=12)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.1f}'))
ax.set_facecolor('#F8F9FA')
plt.tight_layout()
plt.savefig('05_shoplifting_over_5000_rate.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print("✓ Saved: 05_shoplifting_over_5000_rate.png")


# ============================================================================
# CELL 10: Summary
# ============================================================================

print("\n" + "="*80)
print("✅ ALL OUTPUTS GENERATED SUCCESSFULLY!")
print("="*80)

print("\n📊 Generated Files:")
print("   1. 01_top10_violent_crimes_by_rate.png")
print("   2. 02_top10_property_crimes_by_rate.png")
print("   3. 03_top10_other_crimes_by_rate.png")
print("   4. 04_shoplifting_under_5000_rate.png")
print("   5. 05_shoplifting_over_5000_rate.png")

print("\n📁 All files have been saved as PNG images in the current directory.")
print("   You can download them from the Colab Files panel on the left.")

print("\n" + "="*80)
print("Data Source: Statistics Canada Table 35-10-0177-01")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Author: tonHS")
print("="*80)

# Optional: Display images in notebook
# Uncomment the code below to preview images directly in Colab
"""
from IPython.display import Image, display
print("\n📷 Preview of generated images:")
display(Image('01_top10_violent_crimes_by_rate.png'))
display(Image('02_top10_property_crimes_by_rate.png'))
display(Image('03_top10_other_crimes_by_rate.png'))
display(Image('04_shoplifting_under_5000_rate.png'))
display(Image('05_shoplifting_over_5000_rate.png'))
"""
