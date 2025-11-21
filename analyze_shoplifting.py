#!/usr/bin/env python3
"""
Shoplifting Data Analysis for Canadian Crime Trends
Creates separate visualizations for shoplifting under and over $5,000
"""

import pandas as pd
import requests
import zipfile
from io import BytesIO
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Create directories
data_dir = Path('data')
data_dir.mkdir(exist_ok=True)
figures_dir = Path('figures')
figures_dir.mkdir(exist_ok=True)

print("=" * 80)
print("FETCHING SHOPLIFTING DATA FROM STATISTICS CANADA")
print("=" * 80)

# StatCan table ID for organized crime statistics
# This table contains shoplifting data broken down by under/over $5,000
pid = "35100062"

try:
    print(f"\n📥 Downloading data from Statistics Canada (Table {pid})...")

    # Use the API endpoint to get the download URL
    api_url = f"https://www150.statcan.gc.ca/t1/wds/rest/getFullTableDownloadCSV/{pid}/en"
    print(f"Fetching from API: {api_url}")

    api_response = requests.get(api_url, timeout=60)

    if not api_response.ok:
        raise ValueError(f"API request failed: {api_response.status_code} - {api_response.text}")

    zip_url = api_response.json()['object']
    print(f"Got ZIP URL: {zip_url[:100]}...")

    # Download the ZIP file
    zip_response = requests.get(zip_url, timeout=60)

    if not zip_response.ok:
        raise ValueError(f"Data download failed: {zip_response.status_code} - {zip_response.text}")

    # Extract and load the CSV
    with zipfile.ZipFile(BytesIO(zip_response.content)) as z:
        csv_filename = f"{pid}.csv"
        if csv_filename not in z.namelist():
            # Try to find any CSV file
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            if not csv_files:
                raise ValueError("CSV file not found in ZIP")
            csv_filename = csv_files[0]

        print(f"✓ Downloaded and extracted: {csv_filename}")
        df = pd.read_csv(z.open(csv_filename), low_memory=False)

    print(f"✓ Data loaded successfully: {len(df):,} rows, {len(df.columns)} columns")

    # Save raw data
    raw_data_path = data_dir / 'shoplifting_raw.csv'
    df.to_csv(raw_data_path, index=False)
    print(f"✓ Raw data saved to: {raw_data_path}")

except Exception as e:
    print(f"❌ Error: {e}")
    raise

print("\n" + "=" * 80)
print("PROCESSING SHOPLIFTING DATA")
print("=" * 80)

# Explore the data structure
print(f"\n📊 Columns: {df.columns.tolist()}")
print(f"\n📋 Sample data:")
print(df.head())

# Find violation column
violation_col = None
for col in df.columns:
    if 'violation' in col.lower():
        violation_col = col
        break

if violation_col is None:
    print("Available columns:", df.columns.tolist())
    raise ValueError("Could not find violation column")

print(f"\n✓ Using '{violation_col}' as violation column")

# Filter for shoplifting violations
print(f"\n🔍 Searching for shoplifting violations...")
shoplifting_df = df[df[violation_col].str.contains('shoplifting', case=False, na=False)].copy()

if len(shoplifting_df) == 0:
    print("No shoplifting data found. Checking available violations...")
    print("\nAvailable violations (sample):")
    for i, v in enumerate(df[violation_col].unique()[:20], 1):
        print(f"   {i}. {v}")
    raise ValueError("No shoplifting violations found in data")

print(f"✓ Found {len(shoplifting_df):,} shoplifting records")

# Display unique shoplifting violations
print(f"\n📋 Shoplifting violation types:")
for i, violation in enumerate(shoplifting_df[violation_col].unique(), 1):
    print(f"   {i}. {violation}")

# Process year column
year_col = 'REF_DATE'
if year_col in shoplifting_df.columns:
    shoplifting_df['Year'] = shoplifting_df[year_col].astype(int)
else:
    print(f"Error: Could not find {year_col} column")
    print(f"Available columns: {shoplifting_df.columns.tolist()}")
    raise ValueError(f"Missing {year_col} column")

# Get value column
value_col = 'VALUE'
if value_col not in shoplifting_df.columns:
    possible_cols = [col for col in shoplifting_df.columns if 'value' in col.lower()]
    if possible_cols:
        value_col = possible_cols[0]
    else:
        raise ValueError("Could not find value column")

print(f"✓ Using '{value_col}' as value column")

# Remove NaN values
shoplifting_df = shoplifting_df[shoplifting_df[value_col].notna()]

# Filter for Canada-wide data (not provincial)
if 'GEO' in shoplifting_df.columns:
    canada_df = shoplifting_df[shoplifting_df['GEO'] == 'Canada'].copy()
    if len(canada_df) > 0:
        shoplifting_df = canada_df
        print(f"✓ Filtered to Canada-wide data")

# Separate under and over $5,000
under_5k = shoplifting_df[shoplifting_df[violation_col].str.contains('under|5,000 or under', case=False, na=False)]
over_5k = shoplifting_df[shoplifting_df[violation_col].str.contains('over|5,000 or over', case=False, na=False)]

print(f"\n📊 Data split:")
print(f"   • Under $5,000: {len(under_5k):,} records")
print(f"   • Over $5,000: {len(over_5k):,} records")

# Aggregate by year
under_5k_yearly = under_5k.groupby('Year')[value_col].sum().reset_index()
over_5k_yearly = over_5k.groupby('Year')[value_col].sum().reset_index()

under_5k_yearly.columns = ['Year', 'Incidents']
over_5k_yearly.columns = ['Year', 'Incidents']

print(f"\n✓ Yearly aggregation complete")
print(f"   • Years covered (Under $5,000): {under_5k_yearly['Year'].min()}-{under_5k_yearly['Year'].max()}")
print(f"   • Years covered (Over $5,000): {over_5k_yearly['Year'].min()}-{over_5k_yearly['Year'].max()}")

print("\n" + "=" * 80)
print("CREATING VISUALIZATIONS")
print("=" * 80)

# Visualization 1: Comparison chart (both lines)
print("\n📈 Creating comparison chart...")

fig, ax1 = plt.subplots(figsize=(14, 8))

# Plot Under $5,000 on left y-axis
color1 = '#2E86AB'
ax1.set_xlabel('Year', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Incidents', fontsize=14, fontweight='bold', color=color1)
ax1.plot(under_5k_yearly['Year'], under_5k_yearly['Incidents'],
         color=color1, marker='o', linewidth=2.5, markersize=8,
         label='Under $5,000', linestyle='-')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

# Plot Over $5,000 on right y-axis
ax2 = ax1.twinx()
color2 = '#A23B72'
ax2.set_ylabel('Number of Incidents', fontsize=14, fontweight='bold', color=color2)
ax2.plot(over_5k_yearly['Year'], over_5k_yearly['Incidents'],
         color=color2, marker='s', linewidth=2.5, markersize=8,
         label='Over $5,000', linestyle='-')
ax2.tick_params(axis='y', labelcolor=color2)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

# Title and formatting
plt.title('Shoplifting Trends in Canada: Criminal Code Violations\nCriminal Code Violations',
          fontsize=16, fontweight='bold', pad=20)

# Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12, framealpha=0.9)

# Grid
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('white')

plt.tight_layout()

# Save comparison chart
comparison_path = figures_dir / 'shoplifting_trends_comparison.png'
plt.savefig(comparison_path, dpi=300, bbox_inches='tight')
print(f"✓ Comparison chart saved to: {comparison_path}")
plt.close()

# Visualization 2: Separate chart for Over $5,000
print("\n📈 Creating separate chart for Over $5,000...")

fig, ax = plt.subplots(figsize=(14, 8))

# Plot Over $5,000 data
ax.plot(over_5k_yearly['Year'], over_5k_yearly['Incidents'],
        marker='o', linewidth=3, markersize=8,
        color='#A23B72', linestyle='-', label='Shoplifting Over $5,000')

# Formatting
ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Incidents', fontsize=14, fontweight='bold')
ax.set_title('Shoplifting Over $5,000 in Canada\nCriminal Code Violations',
             fontsize=16, fontweight='bold', pad=20)

# Format y-axis with commas
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

# Grid and styling
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(fontsize=12, loc='best', framealpha=0.9)
ax.set_facecolor('#FFF5F7')  # Light pink background
fig.patch.set_facecolor('white')

# Add statistics annotation
if len(over_5k_yearly) >= 2:
    start_year = over_5k_yearly['Year'].iloc[0]
    end_year = over_5k_yearly['Year'].iloc[-1]
    start_value = over_5k_yearly['Incidents'].iloc[0]
    end_value = over_5k_yearly['Incidents'].iloc[-1]

    if start_value > 0:
        pct_change = ((end_value - start_value) / start_value) * 100

        stats_text = f"Change {start_year}-{end_year}: {pct_change:+.1f}%\n"
        stats_text += f"{start_year}: {int(start_value):,} incidents\n"
        stats_text += f"{end_year}: {int(end_value):,} incidents"

        ax.text(0.02, 0.98, stats_text,
                transform=ax.transAxes,
                fontsize=11,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()

# Save separate chart
separate_path = figures_dir / 'shoplifting_over_5000_separate.png'
plt.savefig(separate_path, dpi=300, bbox_inches='tight')
print(f"✓ Separate chart saved to: {separate_path}")
plt.close()

print("\n" + "=" * 80)
print("✓ ANALYSIS COMPLETE")
print("=" * 80)

print(f"\n📁 Generated files:")
print(f"   • {comparison_path}")
print(f"   • {separate_path}")
print(f"   • {raw_data_path}")

print(f"\n📊 Summary Statistics:")
print(f"\nShoplifting Under $5,000:")
print(under_5k_yearly.to_string(index=False))
print(f"\nShoplifting Over $5,000:")
print(over_5k_yearly.to_string(index=False))
