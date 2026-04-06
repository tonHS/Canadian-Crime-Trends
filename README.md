# Canadian Crime Trends

An interactive data visualization webpage analyzing crime statistics in Canada from 1998 to 2024, with live data sourced directly from Statistics Canada.

Cautionary disclaimer: Don't rely on these numbers for anything material. Do your own research and check with experts. This is an exploratory dashboard project only.

## Overview

This project presents a comprehensive analysis of Canadian crime trends across multiple dimensions. While overall crime severity has declined significantly since the turn of the century (-34.5% from 1998 to 2024), the data reveals concerning growth in specific categories including organized crime (+207.8% since 2016), cybercrime (+509.6% since 2014), and violent crime severity (steadily increasing since 2014).

## What the Webpage Includes

The analysis is organized into six key sections:

1. **Crime Severity Index (1998-2024)** - Overall trends showing long-term decline in crime severity
2. **Organized Crime Trends (2016-2024)** - Tracking criminal organization violations including fraud, motor vehicle theft, and drug trafficking
3. **Cybercrime Trends (2014-2024)** - Analysis of rapidly growing digital criminal activity
4. **Top 10 Crime Types by Rate (2024)** - Most common crimes per 100,000 population with 2024 vs. 2014 comparisons
5. **Shoplifting Crime Rates (2000-2024)** - Detailed examination of retail theft trends under and over $5,000
6. **Organized Retail Crime** - Shoplifting attributed to criminal organizations

Each section includes visualizations (PNG charts) and contextual analysis with percentage changes and key insights.

## Methodology

- **Data Source**: Live data pulled directly from Statistics Canada tables (35-10-0062-01, 35-10-0001-01, 35-10-0177-01, 35-10-0026-01)
- **Validation**: 19/19 ground truth tests passed to ensure data accuracy
- **Tools**: Built using Python and HTML/CSS in a Jupyter Notebook (Colab)
- **Generation**: Automated report generation with timestamp tracking
- **Development**: AI tools were used to design, code, and evaluate this webpage, with comprehensive validation efforts to ensure data integrity

## Disclaimer

This analysis was created with the assistance of AI tools. While comprehensive and reasonable efforts have been made to understand and validate the data analysis, **anyone relying on these statistics for material purposes should conduct their own independent analysis**. The program code is available in this repository for replicability and verification purposes.

The data reflects Statistics Canada's official crime statistics, but interpretation and presentation choices are those of the project creator. Users should consult the original Statistics Canada sources for authoritative information and understand the methodological notes regarding crime reporting (e.g., aggregate vs. incident-based surveys).

## Repository Structure

- `index.html` - Main webpage with visualizations and analysis
- `notebooks/MVP5_CustomText.ipynb` - Python notebook for data extraction and processing
- `*.png` - Generated chart visualizations
- `figures/` - Directory for additional figures

## Usage

Open `index.html` in a web browser to view the complete analysis and visualizations.
