# Canadian Crime Trends Analysis

## Overview

This analysis examines overall crime rate trends and retail crime in Canada using official Statistics Canada data. The analysis provides comprehensive insights into violent crimes, property crimes, and specific retail crime trends like shoplifting.

## Data Sources

### Primary Tables
1. **Table 35-10-0177-01**: Incident-based crime statistics
   - Police-reported crime by detailed violations
   - Coverage: Canada, provinces, territories, Census Metropolitan Areas
   - Frequency: Annual
   - URL: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3510017701

2. **Table 35-10-0062-01**: Police-reported crime for selected offences
   - Organized crime statistics
   - Criminal Code traffic violations by type of offence
   - Frequency: Annual
   - URL: https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3510006201

## Analysis Outputs

### 1. Top 10 Violent Criminal Code Violations (2024)
- **File**: `outputs/top_10_violent_crimes_2024.csv`
- **Metrics**:
  - Rank by 2024 incident count
  - 5-year growth rate (2019-2024)
  - 10-year growth rate (2014-2024)
- **Crime Types**: Homicide, assault, sexual offences, robbery, weapons offences, etc.

### 2. Top 10 Property Criminal Code Violations (2024)
- **File**: `outputs/top_10_property_crimes_2024.csv`
- **Metrics**:
  - Rank by 2024 incident count
  - 5-year growth rate (2019-2024)
  - 10-year growth rate (2014-2024)
- **Crime Types**: Theft, fraud, break and enter, shoplifting, motor vehicle theft, etc.

### 3. Shoplifting Trends Visualization
- **File**: `figures/shoplifting_trends_comparison.png`
- **Content**:
  - Side-by-side comparison of Criminal Code violations vs Organized Crime
  - Separate trend lines for shoplifting under $5,000 and over $5,000
  - Multi-year trends showing changes over time

## Usage

### Option 1: Run the Jupyter Notebook (Recommended)

The Jupyter notebook provides an interactive, step-by-step analysis:

```bash
# Open in Jupyter
jupyter notebook notebooks/Crime_Trends_Analysis.ipynb
```

Or **run in Google Colab** (no local setup required):
- Click the "Open in Colab" badge at the top of the notebook
- URL: https://colab.research.google.com/github/tonHS/Canadian-Crime-Trends/blob/main/notebooks/Crime_Trends_Analysis.ipynb

### Option 2: Run the Python Script

For automated analysis, use the standalone Python script:

```bash
# Install dependencies
pip install pandas matplotlib requests openpyxl

# Run the analysis
python analyze_crime_trends.py
```

## Project Structure

```
Canadian-Crime-Trends/
├── notebooks/
│   ├── Crime_Trends_Analysis.ipynb       # Main analysis notebook
│   ├── Crime_Stats_MVP.ipynb              # Organized crime analysis
│   └── Crime_Git_Setup_NewGitHub.ipynb   # Setup notebook
├── data/
│   ├── general_crime_raw.csv             # Raw data from table 35-10-0177-01
│   └── organized_crime_raw.csv           # Raw data from table 35-10-0062-01
├── outputs/
│   ├── top_10_violent_crimes_2024.csv    # Violent crimes analysis
│   └── top_10_property_crimes_2024.csv   # Property crimes analysis
├── figures/
│   └── shoplifting_trends_comparison.png # Shoplifting visualization
├── analyze_crime_trends.py               # Standalone analysis script
└── CRIME_ANALYSIS_README.md              # This file
```

## Key Findings

### Violent Crimes
The analysis identifies and ranks the top 10 violent Criminal Code violations in Canada for 2024, including:
- Homicide and attempted murder
- Various assault categories
- Sexual offences
- Weapons offences
- Robbery and extortion

### Property Crimes
The analysis identifies and ranks the top 10 property Criminal Code violations in Canada for 2024, including:
- Theft (various categories)
- Fraud and identity crimes
- Break and enter
- Motor vehicle theft
- Shoplifting (under and over $5,000)

### Shoplifting Trends
The visualization reveals:
- **Criminal Code violations**: Overall police-reported shoplifting incidents
- **Organized crime**: Shoplifting specifically linked to organized criminal activities
- **Threshold analysis**: Separate tracking for incidents under/over $5,000 threshold
- **Trend patterns**: Multi-year trends showing increases/decreases over time

## Methodology

### Data Collection
1. Data is fetched directly from Statistics Canada's API
2. ZIP files are downloaded and extracted automatically
3. CSV data is parsed and cleaned for analysis

### Data Processing
1. **Filtering**: Extract relevant violation categories using keyword matching
2. **Aggregation**: Sum incidents by violation type and year
3. **Ranking**: Sort by 2024 incident counts to identify top violations
4. **Growth Calculation**: Compute percentage changes over 5 and 10-year periods

### Visualization
- **Line charts**: Show temporal trends for shoplifting categories
- **Side-by-side comparison**: Criminal Code vs Organized Crime
- **Professional styling**: Color-coded, properly labeled with clear legends

## Technical Requirements

### Python Dependencies
```
pandas>=1.3.0
matplotlib>=3.3.0
requests>=2.25.0
openpyxl>=3.0.0
numpy>=1.20.0
```

### Environment
- Python 3.7 or higher
- Internet connection (for data fetching)
- Jupyter Notebook (optional, for interactive analysis)

## Data Limitations

1. **Reporting Bias**: Only includes crimes reported to police
2. **Geographic Scope**: Canada-wide aggregated data
3. **Temporal Coverage**: Depends on Statistics Canada data availability
4. **Classification Changes**: Crime categories may change over time

## Citations

### Data Source
Statistics Canada. Table 35-10-0177-01: Incident-based crime statistics, by detailed violations, Canada, provinces, territories, Census Metropolitan Areas and Canadian Forces Military Police. DOI: https://doi.org/10.25318/3510017701-eng

Statistics Canada. Table 35-10-0062-01: Police-reported crime for selected offences, Canada. DOI: https://doi.org/10.25318/3510006201-eng

### License
This analysis uses open data from Statistics Canada under the [Statistics Canada Open License](https://www.statcan.gc.ca/en/reference/licence).

## Author

**tonHS**
Date: 2025-11-21
GitHub: https://github.com/tonHS/Canadian-Crime-Trends

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Refer to the Statistics Canada documentation for data-related questions
- Check the notebook comments for detailed code explanations

---

## Quick Start Guide

### For First-Time Users

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tonHS/Canadian-Crime-Trends.git
   cd Canadian-Crime-Trends
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt  # or manually install packages listed above
   ```

3. **Run the analysis**:
   - **Option A (Jupyter)**: Open `notebooks/Crime_Trends_Analysis.ipynb`
   - **Option B (Python)**: Run `python analyze_crime_trends.py`

4. **View results**:
   - CSV tables in `outputs/` directory
   - Visualization in `figures/` directory

### For Google Colab Users

1. Open the notebook directly in Colab (click badge in notebook)
2. Run all cells sequentially
3. Download results from the file browser in Colab

---

**Last Updated**: 2025-11-21
