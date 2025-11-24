# Google Colab Instructions for Canadian Crime Metrics

## Quick Start

1. **Open Google Colab**: Go to [colab.research.google.com](https://colab.research.google.com)

2. **Create a new notebook**: Click `File` → `New notebook`

3. **Copy the script**: Copy the entire contents of `colab_canadian_crime_metrics.py`

4. **Paste into Colab**: Paste the script into a code cell

5. **Run the script**: Click the play button (▶️) or press `Shift+Enter`

6. **Download results**: After execution, all PNG files will be available in the Files panel on the left side of Colab

## Outputs Generated

The script generates **7 PNG files**:

### Tables (4 files)
1. **01_top10_violent_crimes_by_rate.png**
   - Top 10 violent Criminal Code violations in 2024 by crime rate
   - Includes growth metrics from 2019 and 2014

2. **02_top10_property_crimes_by_rate.png**
   - Top 10 property Criminal Code violations in 2024 by crime rate
   - Includes growth metrics from 2019 and 2014

3. **03_top10_other_crimes_by_rate.png**
   - Top 10 other Criminal Code violations in 2024 by crime rate
   - Includes growth metrics from 2019 and 2014

4. **04_shoplifting_actual_numbers.png**
   - Shoplifting data for 2024 by actual numbers (not crime rate)
   - Includes three categories:
     - Shoplifting under $5,000
     - Shoplifting over $5,000
     - Shoplifting TOTAL
   - Includes growth metrics from 2019 and 2014

### Line Graphs (3 files)
5. **05_shoplifting_under_5000_line_graph.png**
   - Criminal Code shoplifting under $5,000 from 2000 to 2024

6. **06_shoplifting_over_5000_line_graph.png**
   - Criminal Code shoplifting over $5,000 from 2000 to 2024

7. **07_shoplifting_total_line_graph.png**
   - Criminal Code shoplifting sum total from 2000 to 2024

## Data Source

All data is fetched live from **Statistics Canada Table 35-10-0177-01** (Incident-based crime statistics).

## Requirements

The script uses standard Python libraries that are pre-installed in Google Colab:
- pandas
- numpy
- matplotlib
- requests

No additional installation is required!

## Execution Time

The script typically takes **2-5 minutes** to run, depending on:
- Network speed (downloading data from Statistics Canada)
- Colab server performance

## Troubleshooting

### If the script fails to fetch data:
1. Check your internet connection
2. Verify that Statistics Canada's website is accessible
3. Try running the script again (sometimes network issues are temporary)

### If you need to re-run:
Simply click the play button again. The script will re-fetch the data and regenerate all outputs.

### If a specific output is missing:
Check the console output for error messages. The script will indicate which step failed and why.

## Customization

You can modify the following parameters in the script:

- **Years**: Change `years = list(range(2000, 2025))` to adjust the time range for line graphs
- **Top N**: Change `head(10)` to `head(20)` to get top 20 instead of top 10
- **Figure size**: Modify `figsize=(14, 8)` to adjust chart dimensions
- **Colors**: Change the color codes (e.g., `'#2E86AB'`) to customize chart colors

## Support

For issues or questions:
- Open an issue on the [GitHub repository](https://github.com/tonHS/Canadian-Crime-Trends)
- Contact: tonHS

---

**Generated**: 2025-11-24
**Author**: tonHS
**Data Source**: Statistics Canada Table 35-10-0177-01
