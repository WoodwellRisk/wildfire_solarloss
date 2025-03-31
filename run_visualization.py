#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run Wildfire PM2.5 Visualization

This script runs the visualization process for wildfire PM2.5 data and solar potential change data.
It uses the functions from wildfire_pm25_visualization.py to create publication-quality figures.

Usage:
    python run_visualization.py [output_dir]

    If output_dir is not provided, figures will be saved to ./figures
"""

import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import wildfire_pm25_processing as wpp
import wildfire_pm25_visualization as viz

# Default output directory for saving figures
DEFAULT_OUTPUT_DIR = './figures'

def main(out_dir=DEFAULT_OUTPUT_DIR):
    """
    Main function to run the visualization process.
    
    Parameters:
        out_dir (str): Directory to save figures
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    print("Starting wildfire PM2.5 visualization process...")
    
    # Set up visualization environment
    output_dir = viz.set_output_directory(out_dir)
    print(f"Figures will be saved to: {os.path.abspath(output_dir)}")
    
    try:
        # Process data using wildfire_pm25_processing.py
        print("\nProcessing PM2.5 data...")
        processed_data = wpp.main()
        
        # Extract key datasets for visualization
        print("\nExtracting key datasets for visualization...")
        
        # PM2.5 concentration datasets
        wildfire_pm25_2000 = processed_data["wildfire_pm25_2000"]
        wildfire_pm25_2050_45 = processed_data["wildfire_pm25_2050_45"]
        wildfire_pm25_2050_85 = processed_data["wildfire_pm25_2050_85"]
        wildfire_pm25_2100_45 = processed_data["wildfire_pm25_2100_45"]
        wildfire_pm25_2100_85 = processed_data["wildfire_pm25_2100_85"]
        
        # PM2.5 change datasets
        change_2000_to_2050_45 = processed_data["change_2000_to_2050_45"]
        change_2000_to_2050_85 = processed_data["change_2000_to_2050_85"]
        change_2050_to_2100_45 = processed_data["change_2050_to_2100_45"]
        change_2050_to_2100_85 = processed_data["change_2050_to_2100_85"]
        change_2000_to_2100_45 = processed_data["change_2000_to_2100_45"]
        change_2000_to_2100_85 = processed_data["change_2000_to_2100_85"]
        
        # Solar potential change datasets
        solar_change_2000 = processed_data["solar_change_2000"]
        solar_change_2050_45 = processed_data["solar_change_2050_45"]
        solar_change_2050_85 = processed_data["solar_change_2050_85"]
        solar_change_2100_45 = processed_data["solar_change_2100_45"]
        solar_change_2100_85 = processed_data["solar_change_2100_85"]
        
        # Solar potential change over time datasets
        solar_diff_2000_to_2050_45 = processed_data["solar_diff_2000_to_2050_45"]
        solar_diff_2000_to_2050_85 = processed_data["solar_diff_2000_to_2050_85"]
        solar_diff_2050_to_2100_45 = processed_data["solar_diff_2050_to_2100_45"]
        solar_diff_2050_to_2100_85 = processed_data["solar_diff_2050_to_2100_85"]
        solar_diff_2000_to_2100_45 = processed_data["solar_diff_2000_to_2100_45"]
        solar_diff_2000_to_2100_85 = processed_data["solar_diff_2000_to_2100_85"]
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        
        # 1. Create PM2.5 concentration maps
        print("\n1. Creating PM2.5 concentration maps...")
        
        # Individual PM2.5 maps
        viz.create_pm25_map(
            wildfire_pm25_2000,
            "Wildfire PM2.5 Concentration (2000 Baseline)",
            "wildfire_pm25_2000.png"
        )
        
        viz.create_pm25_map(
            wildfire_pm25_2050_45,
            "Wildfire PM2.5 Concentration (2050 RCP 4.5)",
            "wildfire_pm25_2050_rcp45.png"
        )
        
        viz.create_pm25_map(
            wildfire_pm25_2050_85,
            "Wildfire PM2.5 Concentration (2050 RCP 8.5)",
            "wildfire_pm25_2050_rcp85.png"
        )
        
        viz.create_pm25_map(
            wildfire_pm25_2100_45,
            "Wildfire PM2.5 Concentration (2100 RCP 4.5)",
            "wildfire_pm25_2100_rcp45.png"
        )
        
        viz.create_pm25_map(
            wildfire_pm25_2100_85,
            "Wildfire PM2.5 Concentration (2100 RCP 8.5)",
            "wildfire_pm25_2100_rcp85.png"
        )
        
        # PM2.5 scenario comparison
        pm25_scenario_dict = {
            "2000 Baseline": wildfire_pm25_2000,
            "2050 RCP 4.5": wildfire_pm25_2050_45,
            "2050 RCP 8.5": wildfire_pm25_2050_85,
            "2100 RCP 4.5": wildfire_pm25_2100_45,
            "2100 RCP 8.5": wildfire_pm25_2100_85
        }
        
        viz.create_scenario_comparison_map(
            pm25_scenario_dict,
            "Wildfire PM2.5 Concentration Across Scenarios",
            "wildfire_pm25_scenario_comparison.png",
            cmap="YlOrBr"
        )
        
        # PM2.5 changes over time
        pm25_changes_dict = {
            "2000 to 2050 (RCP 4.5)": change_2000_to_2050_45,
            "2000 to 2050 (RCP 8.5)": change_2000_to_2050_85,
            "2050 to 2100 (RCP 4.5)": change_2050_to_2100_45,
            "2050 to 2100 (RCP 8.5)": change_2050_to_2100_85
        }
        
        viz.create_scenario_comparison_map(
            pm25_changes_dict,
            "Changes in Wildfire PM2.5 Concentration Over Time",
            "wildfire_pm25_changes.png"
        )
        
        # 2. Create solar potential change maps
        print("\n2. Creating solar potential change maps...")
        
        # Individual solar potential maps
        viz.create_solar_potential_map(
            solar_change_2000,
            "Solar Potential Loss Due to Wildfire PM2.5 (2000 Baseline)",
            "solar_potential_loss_2000.png",
            cmap="Reds_r"
        )
        
        viz.create_solar_potential_map(
            solar_change_2050_45,
            "Solar Potential Loss Due to Wildfire PM2.5 (2050 RCP 4.5)",
            "solar_potential_loss_2050_rcp45.png",
            cmap="Reds_r"
        )
        
        viz.create_solar_potential_map(
            solar_change_2050_85,
            "Solar Potential Loss Due to Wildfire PM2.5 (2050 RCP 8.5)",
            "solar_potential_loss_2050_rcp85.png",
            cmap="Reds_r"
        )
        
        viz.create_solar_potential_map(
            solar_change_2100_45,
            "Solar Potential Loss Due to Wildfire PM2.5 (2100 RCP 4.5)",
            "solar_potential_loss_2100_rcp45.png",
            cmap="Reds_r"
        )
        
        viz.create_solar_potential_map(
            solar_change_2100_85,
            "Solar Potential Loss Due to Wildfire PM2.5 (2100 RCP 8.5)",
            "solar_potential_loss_2100_rcp85.png",
            cmap="Reds_r"
        )
        
        # Solar potential scenario comparison
        solar_scenario_dict = {
            "2000 Baseline": solar_change_2000,
            "2050 RCP 4.5": solar_change_2050_45,
            "2050 RCP 8.5": solar_change_2050_85,
            "2100 RCP 4.5": solar_change_2100_45,
            "2100 RCP 8.5": solar_change_2100_85
        }
        
        viz.create_scenario_comparison_map(
            solar_scenario_dict,
            "Solar Potential Loss Due to Wildfire PM2.5 Across Scenarios",
            "solar_potential_loss_scenario_comparison.png",
            cmap="Reds_r"
        )
        
        # Solar potential changes over time
        solar_changes_dict = {
            "2000 to 2050 (RCP 4.5)": solar_diff_2000_to_2050_45,
            "2000 to 2050 (RCP 8.5)": solar_diff_2000_to_2050_85,
            "2050 to 2100 (RCP 4.5)": solar_diff_2050_to_2100_45,
            "2050 to 2100 (RCP 8.5)": solar_diff_2050_to_2100_85
        }
        
        viz.create_scenario_comparison_map(
            solar_changes_dict,
            "Changes in Solar Potential Loss Over Time",
            "solar_potential_loss_changes.png"
        )
        
        # 3. Create regional analysis visualizations
        print("\n3. Creating regional analysis visualizations...")
        
        # Calculate regional means for PM2.5
        pm25_regional_means = viz.calculate_regional_means(pm25_scenario_dict)
        
        # Create regional bar chart for PM2.5
        viz.create_regional_bar_chart(
            pm25_regional_means,
            "Regional Wildfire PM2.5 Concentration Across Scenarios",
            "regional_wildfire_pm25.png"
        )
        
        # Calculate regional means for solar potential loss
        solar_regional_means = viz.calculate_regional_means(solar_scenario_dict)
        
        # Create regional bar chart for solar potential loss
        viz.create_regional_bar_chart(
            solar_regional_means,
            "Regional Solar Potential Loss Due to Wildfire PM2.5",
            "regional_solar_potential_loss.png"
        )
        
        # Calculate regional means for changes in solar potential
        solar_changes_regional_means = viz.calculate_regional_means(solar_changes_dict)
        
        # Create regional bar chart for changes in solar potential
        viz.create_regional_bar_chart(
            solar_changes_regional_means,
            "Regional Changes in Solar Potential Loss Over Time",
            "regional_solar_potential_loss_changes.png"
        )
        
        print("\nVisualization process completed successfully!")
        print(f"All figures saved to: {os.path.abspath(output_dir)}")
        
    except Exception as e:
        print(f"Error during visualization process: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        output_dir = DEFAULT_OUTPUT_DIR
    
    # Run the main function
    exit_code = main(output_dir)
    sys.exit(exit_code)
