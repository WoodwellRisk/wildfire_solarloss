#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wildfire PM2.5 Data Processing

This script focuses solely on processing PM2.5 data from wildfire smoke by subtracting 
no-fire scenarios from standard scenarios for different years and climate projections 
(RCP 4.5 and RCP 8.5).

Steps:
1. Load PM2.5 data for multiple years and scenarios
2. Calculate wildfire contributions by subtracting no-fire from standard scenarios
3. Calculate impacts on solar power potential
4. Store results in clearly named variables for further analysis
"""

# Import required libraries
import xarray as xr
import numpy as np
import os
from pathlib import Path

# Define directories for data
data_dir = './data'

# List available data files to verify they exist
pm25_files = [f for f in os.listdir(data_dir) if f.startswith('CESM') and f.endswith('.nc')]
pm25_files.sort()
print("Available PM2.5 files:", pm25_files)

# Utility Functions
def fix_lon(ds):
    """Adjust longitude values to ensure they are within (-180, 180) range.
    
    Parameters:
        ds (xarray.Dataset or xarray.DataArray): Dataset with longitude coordinates
        
    Returns:
        xarray.Dataset or xarray.DataArray: Dataset with adjusted longitude coordinates
    """
    lon_name = 'lon'  # whatever name is in the data

    # Make a copy to avoid modifying the original
    ds_copy = ds.copy()
    
    # Adjust lon values to make sure they are within (-180, 180)
    ds_copy['_longitude_adjusted'] = xr.where(
        ds_copy[lon_name] > 180,
        ds_copy[lon_name] - 360,
        ds_copy[lon_name])

    # reassign the new coords to as the main lon coords
    # and sort DataArray using new coordinate values
    ds_copy = (
        ds_copy
        .swap_dims({lon_name: '_longitude_adjusted'})
        .sortby('_longitude_adjusted')  # Use sortby instead of sel with sorted
        .drop_vars(lon_name))

    ds_copy = ds_copy.rename({'_longitude_adjusted': lon_name})
    return ds_copy

# Function to process a specific year and scenario
def process_scenario_data(year, scenario):
    """Load and process data for a specific year and scenario.
    
    Parameters:
        year (int): Year to process
        scenario (str): RCP scenario ("45" or "85")
    
    Returns:
        tuple: (wildfire_pm25, baseline_pm25, nofire_pm25) - DataArrays for each component
    """
    print(f"Processing {year} RCP {scenario[0]}.{scenario[1]} scenario")
    
    # Define file paths
    baseline_path = os.path.join(data_dir, f'CESM_09x125_PM25_{year}_RCP{scenario}.nc')
    nofire_path = os.path.join(data_dir, f'CESM_09x125_PM25_{year}_RCP{scenario}_NoFire.nc')
    
    # Load datasets
    baseline_ds = xr.open_dataset(baseline_path)
    nofire_ds = xr.open_dataset(nofire_path)
    
    # Extract PM2.5 and process
    baseline_pm25 = baseline_ds['pm25']
    nofire_pm25 = nofire_ds['pm25']
    
    # Take time average if needed
    if 'time' in baseline_pm25.dims:
        baseline_pm25 = baseline_pm25.mean(dim='time')
    if 'time' in nofire_pm25.dims:
        nofire_pm25 = nofire_pm25.mean(dim='time')
    
    # Fix longitude coordinates
    baseline_pm25 = fix_lon(baseline_pm25)
    nofire_pm25 = fix_lon(nofire_pm25)
    
    # Calculate wildfire contribution
    wildfire_pm25 = baseline_pm25 - nofire_pm25
    
    # Basic statistics of wildfire PM2.5
    print(f"Wildfire PM2.5 ({year} RCP {scenario[0]}.{scenario[1]}) - "
          f"Min: {wildfire_pm25.min().values:.2f}, "
          f"Max: {wildfire_pm25.max().values:.2f}, "
          f"Mean: {wildfire_pm25.mean().values:.2f} μg/m³")
    
    return wildfire_pm25, baseline_pm25, nofire_pm25

# Function to calculate solar power potential change based on PM2.5 concentration
def calculate_solar_potential_change(pm25_data):
    """
    Calculate the percentage change in solar power potential due to PM2.5 concentration.
    
    Parameters:
        pm25_data (xarray.DataArray): PM2.5 concentration in μg/m³
        
    Returns:
        xarray.DataArray: Percentage change in solar power potential
    """
    # Apply the equation: potential change (%) = -0.48 * pm2.5 / 17.71 * 100
    # with a hard cap at -100% (complete loss of solar potential)
    uncapped_change = -0.48 * pm25_data / 17.71 * 100
    
    # Apply the cap at -100% (complete loss of solar potential)
    solar_potential_change = xr.where(uncapped_change < -100, -100, uncapped_change)
    
    # Add attributes for clarity
    solar_potential_change.attrs['units'] = '%'
    solar_potential_change.attrs['long_name'] = 'Solar Power Potential Change'
    solar_potential_change.attrs['description'] = 'Percentage change in solar power potential due to PM2.5 concentration (capped at -100%)'
    
    return solar_potential_change

# Main processing function
def main():
    print("Starting PM2.5 data processing...")
    
    # Load and Process 2000 Baseline Data
    print("\n--- Processing 2000 Baseline Data ---")
    baseline_2000_path = os.path.join(data_dir, 'CESM_09x125_PM25_2000_Baseline.nc')
    nofire_2000_path = os.path.join(data_dir, 'CESM_09x125_PM25_2000_BaseLine_NoFire.nc')

    # Load data
    baseline_2000_ds = xr.open_dataset(baseline_2000_path)
    nofire_2000_ds = xr.open_dataset(nofire_2000_path)

    # Examine data structure
    print("Baseline 2000 Dataset:")
    print(baseline_2000_ds)
    print("\nNo-Fire 2000 Dataset:")
    print(nofire_2000_ds)

    # Extract PM2.5 variables
    baseline_pm25_2000 = baseline_2000_ds['pm25']
    nofire_pm25_2000 = nofire_2000_ds['pm25']

    # Take time average if needed
    if 'time' in baseline_pm25_2000.dims:
        baseline_pm25_2000 = baseline_pm25_2000.mean(dim='time')
    if 'time' in nofire_pm25_2000.dims:
        nofire_pm25_2000 = nofire_pm25_2000.mean(dim='time')

    # Fix longitude coordinates
    baseline_pm25_2000 = fix_lon(baseline_pm25_2000)
    nofire_pm25_2000 = fix_lon(nofire_pm25_2000)

    # Show dimensions after processing
    print("Processed baseline PM2.5 dims:", baseline_pm25_2000.dims)
    print("Processed no-fire PM2.5 dims:", nofire_pm25_2000.dims)

    # Calculate wildfire contribution for 2000 by subtraction
    wildfire_pm25_2000 = baseline_pm25_2000 - nofire_pm25_2000

    # Basic statistics of wildfire PM2.5
    print(f"Wildfire PM2.5 (2000) - Min: {wildfire_pm25_2000.min().values:.2f}, "
          f"Max: {wildfire_pm25_2000.max().values:.2f}, "
          f"Mean: {wildfire_pm25_2000.mean().values:.2f} μg/m³")
    
    # Process 2050 Data (RCP 4.5 and RCP 8.5)
    print("\n--- Processing 2050 Data ---")
    wildfire_pm25_2050_45, baseline_pm25_2050_45, nofire_pm25_2050_45 = process_scenario_data(2050, "45")
    wildfire_pm25_2050_85, baseline_pm25_2050_85, nofire_pm25_2050_85 = process_scenario_data(2050, "85")
    
    # Process 2100 Data (RCP 4.5 and RCP 8.5)
    print("\n--- Processing 2100 Data ---")
    wildfire_pm25_2100_45, baseline_pm25_2100_45, nofire_pm25_2100_45 = process_scenario_data(2100, "45")
    wildfire_pm25_2100_85, baseline_pm25_2100_85, nofire_pm25_2100_85 = process_scenario_data(2100, "85")
    
    # Calculate Temporal Changes in Wildfire PM2.5
    print("\n--- Calculating Temporal Changes in Wildfire PM2.5 ---")
    change_2000_to_2050_45 = wildfire_pm25_2050_45 - wildfire_pm25_2000
    change_2000_to_2050_85 = wildfire_pm25_2050_85 - wildfire_pm25_2000
    change_2050_to_2100_45 = wildfire_pm25_2100_45 - wildfire_pm25_2050_45
    change_2050_to_2100_85 = wildfire_pm25_2100_85 - wildfire_pm25_2050_85
    change_2000_to_2100_45 = wildfire_pm25_2100_45 - wildfire_pm25_2000
    change_2000_to_2100_85 = wildfire_pm25_2100_85 - wildfire_pm25_2000

    # Print statistics for RCP 4.5 changes
    print("Change from 2000 to 2050 (RCP 4.5):")
    print(f"Min: {change_2000_to_2050_45.min().values:.2f}, "
          f"Max: {change_2000_to_2050_45.max().values:.2f}, "
          f"Mean: {change_2000_to_2050_45.mean().values:.2f} μg/m³")

    print("\nChange from 2050 to 2100 (RCP 4.5):")
    print(f"Min: {change_2050_to_2100_45.min().values:.2f}, "
          f"Max: {change_2050_to_2100_45.max().values:.2f}, "
          f"Mean: {change_2050_to_2100_45.mean().values:.2f} μg/m³")

    print("\nChange from 2000 to 2100 (RCP 4.5):")
    print(f"Min: {change_2000_to_2100_45.min().values:.2f}, "
          f"Max: {change_2000_to_2100_45.max().values:.2f}, "
          f"Mean: {change_2000_to_2100_45.mean().values:.2f} μg/m³")

    # Print statistics for RCP 8.5 changes
    print("\nChange from 2000 to 2050 (RCP 8.5):")
    print(f"Min: {change_2000_to_2050_85.min().values:.2f}, "
          f"Max: {change_2000_to_2050_85.max().values:.2f}, "
          f"Mean: {change_2000_to_2050_85.mean().values:.2f} μg/m³")

    print("\nChange from 2050 to 2100 (RCP 8.5):")
    print(f"Min: {change_2050_to_2100_85.min().values:.2f}, "
          f"Max: {change_2050_to_2100_85.max().values:.2f}, "
          f"Mean: {change_2050_to_2100_85.mean().values:.2f} μg/m³")

    print("\nChange from 2000 to 2100 (RCP 8.5):")
    print(f"Min: {change_2000_to_2100_85.min().values:.2f}, "
          f"Max: {change_2000_to_2100_85.max().values:.2f}, "
          f"Mean: {change_2000_to_2100_85.mean().values:.2f} μg/m³")
    
    # Calculate Solar Power Potential Changes
    print("\n--- Calculating Solar Power Potential Changes ---")
    solar_change_2000 = calculate_solar_potential_change(wildfire_pm25_2000)
    solar_change_2050_45 = calculate_solar_potential_change(wildfire_pm25_2050_45)
    solar_change_2050_85 = calculate_solar_potential_change(wildfire_pm25_2050_85)
    solar_change_2100_45 = calculate_solar_potential_change(wildfire_pm25_2100_45)
    solar_change_2100_85 = calculate_solar_potential_change(wildfire_pm25_2100_85)

    # Print statistics for solar power potential changes
    print("Solar Power Potential Change (2000):")
    print(f"Min: {solar_change_2000.min().values:.2f}%, "
          f"Max: {solar_change_2000.max().values:.2f}%, "
          f"Mean: {solar_change_2000.mean().values:.2f}%")

    print("\nSolar Power Potential Change (2050 RCP 4.5):")
    print(f"Min: {solar_change_2050_45.min().values:.2f}%, "
          f"Max: {solar_change_2050_45.max().values:.2f}%, "
          f"Mean: {solar_change_2050_45.mean().values:.2f}%")

    print("\nSolar Power Potential Change (2050 RCP 8.5):")
    print(f"Min: {solar_change_2050_85.min().values:.2f}%, "
          f"Max: {solar_change_2050_85.max().values:.2f}%, "
          f"Mean: {solar_change_2050_85.mean().values:.2f}%")

    print("\nSolar Power Potential Change (2100 RCP 4.5):")
    print(f"Min: {solar_change_2100_45.min().values:.2f}%, "
          f"Max: {solar_change_2100_45.max().values:.2f}%, "
          f"Mean: {solar_change_2100_45.mean().values:.2f}%")

    print("\nSolar Power Potential Change (2100 RCP 8.5):")
    print(f"Min: {solar_change_2100_85.min().values:.2f}%, "
          f"Max: {solar_change_2100_85.max().values:.2f}%, "
          f"Mean: {solar_change_2100_85.mean().values:.2f}%")
    
    # Calculate Changes in Solar Power Potential Over Time
    print("\n--- Calculating Changes in Solar Power Potential Over Time ---")
    solar_diff_2000_to_2050_45 = solar_change_2050_45 - solar_change_2000
    solar_diff_2000_to_2050_85 = solar_change_2050_85 - solar_change_2000
    solar_diff_2050_to_2100_45 = solar_change_2100_45 - solar_change_2050_45
    solar_diff_2050_to_2100_85 = solar_change_2100_85 - solar_change_2050_85
    solar_diff_2000_to_2100_45 = solar_change_2100_45 - solar_change_2000
    solar_diff_2000_to_2100_85 = solar_change_2100_85 - solar_change_2000

    # Print statistics for changes in solar power potential
    print("Change in Solar Power Potential from 2000 to 2050 (RCP 4.5):")
    print(f"Min: {solar_diff_2000_to_2050_45.min().values:.2f}%, "
          f"Max: {solar_diff_2000_to_2050_45.max().values:.2f}%, "
          f"Mean: {solar_diff_2000_to_2050_45.mean().values:.2f}%")

    print("\nChange in Solar Power Potential from 2000 to 2050 (RCP 8.5):")
    print(f"Min: {solar_diff_2000_to_2050_85.min().values:.2f}%, "
          f"Max: {solar_diff_2000_to_2050_85.max().values:.2f}%, "
          f"Mean: {solar_diff_2000_to_2050_85.mean().values:.2f}%")

    print("\nChange in Solar Power Potential from 2050 to 2100 (RCP 4.5):")
    print(f"Min: {solar_diff_2050_to_2100_45.min().values:.2f}%, "
          f"Max: {solar_diff_2050_to_2100_45.max().values:.2f}%, "
          f"Mean: {solar_diff_2050_to_2100_45.mean().values:.2f}%")

    print("\nChange in Solar Power Potential from 2050 to 2100 (RCP 8.5):")
    print(f"Min: {solar_diff_2050_to_2100_85.min().values:.2f}%, "
          f"Max: {solar_diff_2050_to_2100_85.max().values:.2f}%, "
          f"Mean: {solar_diff_2050_to_2100_85.mean().values:.2f}%")

    print("\nChange in Solar Power Potential from 2000 to 2100 (RCP 4.5):")
    print(f"Min: {solar_diff_2000_to_2100_45.min().values:.2f}%, "
          f"Max: {solar_diff_2000_to_2100_45.max().values:.2f}%, "
          f"Mean: {solar_diff_2000_to_2100_45.mean().values:.2f}%")

    print("\nChange in Solar Power Potential from 2000 to 2100 (RCP 8.5):")
    print(f"Min: {solar_diff_2000_to_2100_85.min().values:.2f}%, "
          f"Max: {solar_diff_2000_to_2100_85.max().values:.2f}%, "
          f"Mean: {solar_diff_2000_to_2100_85.mean().values:.2f}%")
    
    print("\n--- Processing Complete ---")
    print("The following variables are now available for further analysis:")
    
    # List of all processed variables
    variables = {
        "Baseline PM2.5": [
            "baseline_pm25_2000", "baseline_pm25_2050_45", "baseline_pm25_2050_85", 
            "baseline_pm25_2100_45", "baseline_pm25_2100_85"
        ],
        "No-Fire PM2.5": [
            "nofire_pm25_2000", "nofire_pm25_2050_45", "nofire_pm25_2050_85", 
            "nofire_pm25_2100_45", "nofire_pm25_2100_85"
        ],
        "Wildfire PM2.5": [
            "wildfire_pm25_2000", "wildfire_pm25_2050_45", "wildfire_pm25_2050_85", 
            "wildfire_pm25_2100_45", "wildfire_pm25_2100_85"
        ],
        "Temporal Changes in Wildfire PM2.5": [
            "change_2000_to_2050_45", "change_2000_to_2050_85", 
            "change_2050_to_2100_45", "change_2050_to_2100_85",
            "change_2000_to_2100_45", "change_2000_to_2100_85"
        ],
        "Solar Power Potential Changes": [
            "solar_change_2000", "solar_change_2050_45", "solar_change_2050_85", 
            "solar_change_2100_45", "solar_change_2100_85"
        ],
        "Changes in Solar Power Potential": [
            "solar_diff_2000_to_2050_45", "solar_diff_2000_to_2050_85", 
            "solar_diff_2050_to_2100_45", "solar_diff_2050_to_2100_85",
            "solar_diff_2000_to_2100_45", "solar_diff_2000_to_2100_85"
        ]
    }
    
    # Print variable categories and names
    for category, vars_list in variables.items():
        print(f"\n{category}:")
        for var in vars_list:
            print(f"  - {var}")
    
    # Return all processed variables for potential further use
    return {
        "baseline_pm25_2000": baseline_pm25_2000,
        "baseline_pm25_2050_45": baseline_pm25_2050_45,
        "baseline_pm25_2050_85": baseline_pm25_2050_85,
        "baseline_pm25_2100_45": baseline_pm25_2100_45,
        "baseline_pm25_2100_85": baseline_pm25_2100_85,
        "nofire_pm25_2000": nofire_pm25_2000,
        "nofire_pm25_2050_45": nofire_pm25_2050_45,
        "nofire_pm25_2050_85": nofire_pm25_2050_85,
        "nofire_pm25_2100_45": nofire_pm25_2100_45,
        "nofire_pm25_2100_85": nofire_pm25_2100_85,
        "wildfire_pm25_2000": wildfire_pm25_2000,
        "wildfire_pm25_2050_45": wildfire_pm25_2050_45,
        "wildfire_pm25_2050_85": wildfire_pm25_2050_85,
        "wildfire_pm25_2100_45": wildfire_pm25_2100_45,
        "wildfire_pm25_2100_85": wildfire_pm25_2100_85,
        "change_2000_to_2050_45": change_2000_to_2050_45,
        "change_2000_to_2050_85": change_2000_to_2050_85,
        "change_2050_to_2100_45": change_2050_to_2100_45,
        "change_2050_to_2100_85": change_2050_to_2100_85,
        "change_2000_to_2100_45": change_2000_to_2100_45,
        "change_2000_to_2100_85": change_2000_to_2100_85,
        "solar_change_2000": solar_change_2000,
        "solar_change_2050_45": solar_change_2050_45,
        "solar_change_2050_85": solar_change_2050_85,
        "solar_change_2100_45": solar_change_2100_45,
        "solar_change_2100_85": solar_change_2100_85,
        "solar_diff_2000_to_2050_45": solar_diff_2000_to_2050_45,
        "solar_diff_2000_to_2050_85": solar_diff_2000_to_2050_85,
        "solar_diff_2050_to_2100_45": solar_diff_2050_to_2100_45,
        "solar_diff_2050_to_2100_85": solar_diff_2050_to_2100_85,
        "solar_diff_2000_to_2100_45": solar_diff_2000_to_2100_45,
        "solar_diff_2000_to_2100_85": solar_diff_2000_to_2100_85
    }

# Run the main function if script is executed directly
if __name__ == "__main__":
    main()
