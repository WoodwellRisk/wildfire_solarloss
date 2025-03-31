# Wildfire PM2.5 Visualization Package

This package provides tools for processing and visualizing wildfire PM2.5 data and its impact on solar energy potential. It uses climate model data from the Community Earth System Model (CESM) to analyze how wildfire-generated particulate matter affects solar radiation reaching the Earth's surface.

## Features

- Process PM2.5 data from wildfire smoke by subtracting no-fire scenarios from standard scenarios
- Calculate impacts on solar power potential using established relationships between PM2.5 and solar radiation
- Generate publication-quality visualizations including:
  - Global maps of PM2.5 concentration
  - Global maps of solar potential change
  - Regional analysis with weighted means
  - Temporal changes across different climate scenarios (RCP 4.5 and RCP 8.5)
  - Multi-panel comparison figures

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/wildfire_pm25_visualization.git
cd wildfire_pm25_visualization
```

2. Install required dependencies:
```bash
pip install numpy pandas xarray matplotlib seaborn cartopy
```

## Data Requirements

The package requires NetCDF files with PM2.5 concentration data. The expected files are:

- `CESM_09x125_PM25_2000_Baseline.nc` - Baseline scenario for year 2000
- `CESM_09x125_PM25_2000_BaseLine_NoFire.nc` - No-fire scenario for year 2000
- `CESM_09x125_PM25_2050_RCP45.nc` - RCP 4.5 scenario for year 2050
- `CESM_09x125_PM25_2050_RCP45_NoFire.nc` - RCP 4.5 no-fire scenario for year 2050
- `CESM_09x125_PM25_2050_RCP85.nc` - RCP 8.5 scenario for year 2050
- `CESM_09x125_PM25_2050_RCP85_NoFire.nc` - RCP 8.5 no-fire scenario for year 2050
- `CESM_09x125_PM25_2100_RCP45.nc` - RCP 4.5 scenario for year 2100
- `CESM_09x125_PM25_2100_RCP45_NoFire.nc` - RCP 4.5 no-fire scenario for year 2100
- `CESM_09x125_PM25_2100_RCP85.nc` - RCP 8.5 scenario for year 2100
- `CESM_09x125_PM25_2100_RCP85_NoFire.nc` - RCP 8.5 no-fire scenario for year 2100

Place these files in the `data/` directory.

## Usage

Run the visualization script:

```bash
python run_visualization.py
```

This will:
1. Process the PM2.5 data using functions from `wildfire_pm25_processing.py`
2. Generate visualizations using functions from `wildfire_pm25_visualization.py`
3. Save all figures to the `figures/` directory

You can specify a custom output directory:

```bash
python run_visualization.py /path/to/output/directory
```

## Output

The package generates several types of visualizations:

1. **PM2.5 Concentration Maps**:
   - Individual maps for each scenario
   - Scenario comparison
   - Temporal changes

2. **Solar Potential Loss Maps**:
   - Individual maps for each scenario
   - Scenario comparison
   - Temporal changes

3. **Regional Analysis**:
   - Regional PM2.5 concentration
   - Regional solar potential loss
   - Regional changes over time

## File Structure

- `wildfire_pm25_processing.py` - Core data processing functions
- `wildfire_pm25_visualization.py` - Visualization functions
- `run_visualization.py` - Main script to run the visualization process
- `data/` - Directory for input data files
- `figures/` - Directory for output figures

## Methodology

The package calculates wildfire contributions to PM2.5 by subtracting no-fire scenarios from standard scenarios. It then uses the relationship between PM2.5 concentration and solar radiation reduction to estimate the impact on solar power potential.

The solar potential change is calculated using the equation:
```
potential_change (%) = -0.48 * pm2.5 / 17.71 * 100
```

This relationship is based on research showing that PM2.5 particles scatter and absorb incoming solar radiation, reducing the amount that reaches solar panels.

## License

[MIT License](LICENSE)

## Citation

If you use this package in your research, please cite:

```
Author, A. (2025). Wildfire PM2.5 Visualization Package. GitHub repository. https://github.com/yourusername/wildfire_pm25_visualization
```

## Contact

For questions or feedback, please open an issue on GitHub or contact [your email].
