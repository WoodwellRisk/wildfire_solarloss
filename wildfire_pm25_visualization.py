#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wildfire PM2.5 Visualization

This script creates publication-quality visualizations of the processed PM2.5 and 
solar potential change data from wildfire_pm25_processing.py.

Visualizations include:
1. Global maps of solar potential change in %
2. Regional totals in bar charts
3. Annotated figures for improved clarity and interpretation
4. Raw PM2.5 pollution maps in micrograms/m3

Usage:
    python wildfire_pm25_visualization.py [output_dir]

    If output_dir is not provided, figures will be saved to ./figures
"""

import os
import sys

# Try to import dependencies, but don't fail if they're not available
try:
    import numpy as np
    import pandas as pd
    import xarray as xr
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib.ticker import ScalarFormatter, MultipleLocator
    import seaborn as sns
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Warning: Some dependencies are not available. Visualization functions will not work.")

try:
    import wildfire_pm25_processing as wpp
except ImportError:
    print("Warning: wildfire_pm25_processing module not found.")

# Default output directory for saving figures
DEFAULT_OUTPUT_DIR = './figures'

# Global variable for output directory
output_dir = DEFAULT_OUTPUT_DIR

# Define regions for regional analysis
regions = {
    'North America': {'lat_min': 15, 'lat_max': 70, 'lon_min': -170, 'lon_max': -50},
    'South America': {'lat_min': -55, 'lat_max': 15, 'lon_min': -80, 'lon_max': -35},
    'Europe': {'lat_min': 35, 'lat_max': 70, 'lon_min': -10, 'lon_max': 40},
    'Africa': {'lat_min': -35, 'lat_max': 35, 'lon_min': -20, 'lon_max': 55},
    'Asia': {'lat_min': 0, 'lat_max': 55, 'lon_min': 60, 'lon_max': 150},
    'Australia': {'lat_min': -45, 'lat_max': -10, 'lon_min': 110, 'lon_max': 155}
}

# Function to set up visualization environment
def setup_visualization_env(out_dir=DEFAULT_OUTPUT_DIR):
    """
    Set up the visualization environment by creating output directory
    and setting matplotlib/seaborn styles.
    
    Parameters:
        out_dir (str): Directory to save figures
    
    Returns:
        str: Path to output directory
    """
    # Create output directory if it doesn't exist
    os.makedirs(out_dir, exist_ok=True)
    
    # Set Seaborn style for publication-quality figures
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.titlesize'] = 16
    
    return out_dir

# Function to create a global map of solar potential change
def create_solar_potential_map(data, title, filename, vmin=None, vmax=None, cmap='RdBu_r', 
                              projection=ccrs.Robinson(), figsize=(12, 8)):
    """
    Create a publication-quality global map of solar potential change.
    
    Parameters:
        data (xarray.DataArray): Solar potential change data
        title (str): Title for the map
        filename (str): Filename to save the figure
        vmin (float, optional): Minimum value for colorbar
        vmax (float, optional): Maximum value for colorbar
        cmap (str or colormap, optional): Colormap to use
        projection (cartopy.crs, optional): Map projection
        figsize (tuple, optional): Figure size
    """
    fig = plt.figure(figsize=figsize, facecolor='white')
    ax = plt.axes(projection=projection)
    
    # Set global extent
    ax.set_global()
    
    # Add map features with improved styling
    ax.coastlines(linewidth=1.0, color='#333333')
    ax.add_feature(cfeature.BORDERS, linestyle='-', edgecolor='#777777', linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='#EFEFEF', alpha=0.5)
    ax.add_feature(cfeature.OCEAN, facecolor='#EAEAFF', alpha=0.5)
    
    # Add gridlines for better geographic reference
    gl = ax.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    
    # Create a custom colormap with white for near-zero values
    if cmap == 'RdBu_r' or cmap == 'RdBu':
        # For diverging data (positive and negative changes)
        if vmin is None:
            vmin = -max(abs(data.min().values), abs(data.max().values))
        if vmax is None:
            vmax = max(abs(data.min().values), abs(data.max().values))
        
        # Create a custom colormap with white at center
        colors_rb = plt.cm.RdBu_r(np.linspace(0, 1, 256))
        # Make values near zero white (center of the colormap)
        white_threshold = 0.02  # 2% of the range
        center_idx = 128  # Center of the colormap
        threshold_idx = int(256 * white_threshold)
        for i in range(center_idx - threshold_idx, center_idx + threshold_idx):
            if i >= 0 and i < 256:  # Ensure index is valid
                colors_rb[i] = [1, 1, 1, 1]  # White with full alpha
        
        custom_cmap = mcolors.LinearSegmentedColormap.from_list('RdBu_r_white_center', colors_rb)
        
        # Create a centered norm for diverging data
        norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        cmap = custom_cmap
        
        # Add explanatory annotation for diverging data
        plt.annotate('Red = Increased Solar Potential Loss, Blue = Decreased Solar Potential Loss, White = Near-Zero Change', 
                    xy=(0.99, 0.01), xycoords='figure fraction', 
                    fontsize=9, ha='right', va='bottom', style='italic', color='darkred')
    else:
        # For sequential data (Reds_r for solar potential loss)
        if vmin is None:
            vmin = data.min().values
        if vmax is None:
            vmax = data.max().values
        
        # Create a custom colormap with white for near-zero values
        colors_seq = plt.cm.get_cmap(cmap)(np.linspace(0, 1, 256))
        # Make values near zero white (for sequential colormap, near-zero is at the end)
        white_threshold = 0.05  # 5% of the range
        threshold_idx = int(256 * white_threshold)
        for i in range(256 - threshold_idx, 256):
            colors_seq[i] = [1, 1, 1, 1]  # White with full alpha
        
        custom_cmap = mcolors.LinearSegmentedColormap.from_list(f'{cmap}_white_low', colors_seq)
        
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
        cmap = custom_cmap
        
        # Add explanatory annotation for sequential data
        plt.annotate('Darker Red = Greater Solar Potential Loss, White = Near-Zero Values', 
                    xy=(0.99, 0.01), xycoords='figure fraction', 
                    fontsize=9, ha='right', va='bottom', style='italic', color='darkred')
    
    # Plot the data with slightly dimmed colors (alpha=0.8)
    im = ax.pcolormesh(
        data.lon, data.lat, data, 
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        norm=norm,
        alpha=0.8,  # Dim the colors slightly
        edgecolor='face',
        linewidth=0.1
    )
    
    # Add colorbar with improved styling
    cbar = plt.colorbar(im, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar.set_label('Solar Potential Change (%)', fontweight='bold', fontsize=12)
    cbar.ax.tick_params(labelsize=10)
    
    # Add zero line to colorbar if using diverging data
    if cmap == 'RdBu_r' or cmap == 'RdBu':
        cbar.ax.axvline(x=0, color='k', linestyle='-', linewidth=0.8, alpha=0.6)
    
    # Add title with improved styling
    plt.title(title, fontweight='bold', pad=20, fontsize=14)
    
    # Add data source annotation
    plt.annotate('Data Source: CESM Climate Model', xy=(0.01, 0.01), xycoords='figure fraction', 
                fontsize=9, ha='left', va='bottom', style='italic')
    
    # Save figure
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure to {os.path.join(output_dir, filename)}")

# Function to create a map of PM2.5 concentration
def create_pm25_map(data, title, filename, vmin=None, vmax=None, cmap='YlOrBr', 
                   projection=ccrs.Robinson(), figsize=(12, 8)):
    """
    Create a publication-quality global map of PM2.5 concentration.
    
    Parameters:
        data (xarray.DataArray): PM2.5 concentration data in μg/m³
        title (str): Title for the map
        filename (str): Filename to save the figure
        vmin (float, optional): Minimum value for colorbar
        vmax (float, optional): Maximum value for colorbar
        cmap (str or colormap, optional): Colormap to use
        projection (cartopy.crs, optional): Map projection
        figsize (tuple, optional): Figure size
    """
    fig = plt.figure(figsize=figsize, facecolor='white')
    ax = plt.axes(projection=projection)
    
    # Set global extent
    ax.set_global()
    
    # Add map features with improved styling
    ax.coastlines(linewidth=1.0, color='#333333')
    ax.add_feature(cfeature.BORDERS, linestyle='-', edgecolor='#777777', linewidth=0.5)
    ax.add_feature(cfeature.LAND, facecolor='#EFEFEF', alpha=0.5)
    ax.add_feature(cfeature.OCEAN, facecolor='#EAEAFF', alpha=0.5)
    
    # Add gridlines for better geographic reference
    gl = ax.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    
    # For PM2.5 data, use a sequential colormap
    if vmin is None:
        vmin = 0  # PM2.5 concentration can't be negative
    if vmax is None:
        vmax = data.max().values
    
    # Create a custom colormap with white for near-zero values
    colors_seq = plt.cm.get_cmap(cmap)(np.linspace(0, 1, 256))
    # Make values near zero white
    white_threshold = 0.05  # 5% of the range
    threshold_idx = int(256 * white_threshold)
    for i in range(threshold_idx):
        colors_seq[i] = [1, 1, 1, 1]  # White with full alpha
    
    custom_cmap = mcolors.LinearSegmentedColormap.from_list(f'{cmap}_white_low', colors_seq)
    cmap = custom_cmap
    
    # Create a norm for the colormap
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    
    # Plot the data with slightly dimmed colors (alpha=0.8)
    im = ax.pcolormesh(
        data.lon, data.lat, data, 
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        norm=norm,
        alpha=0.8,  # Dim the colors slightly
        edgecolor='face',
        linewidth=0.1
    )
    
    # Add colorbar with improved styling
    cbar = plt.colorbar(im, orientation='horizontal', pad=0.05, shrink=0.8)
    cbar.set_label('PM2.5 Concentration (μg/m³)', fontweight='bold', fontsize=12)
    cbar.ax.tick_params(labelsize=10)
    
    # Add title with improved styling
    plt.title(title, fontweight='bold', pad=20, fontsize=14)
    
    # Add data source annotation
    plt.annotate('Data Source: CESM Climate Model', xy=(0.01, 0.01), xycoords='figure fraction', 
                fontsize=9, ha='left', va='bottom', style='italic')
    
    # Add explanatory annotation
    plt.annotate('Higher values indicate greater wildfire PM2.5 pollution', 
                xy=(0.99, 0.01), xycoords='figure fraction', 
                fontsize=9, ha='right', va='bottom', style='italic', color='darkred')
    
    # Save figure
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure to {os.path.join(output_dir, filename)}")

# Function to calculate regional means
def calculate_regional_means(data_dict):
    """
    Calculate regional means for each dataset in the dictionary.
    
    Parameters:
        data_dict (dict): Dictionary of xarray.DataArray objects
        
    Returns:
        pandas.DataFrame: DataFrame of regional means
    """
    regional_means = {}
    
    for region_name, region_bounds in regions.items():
        regional_means[region_name] = {}
        
        for data_name, data in data_dict.items():
            # Select region
            region_data = data.sel(
                lat=slice(region_bounds['lat_min'], region_bounds['lat_max']),
                lon=slice(region_bounds['lon_min'], region_bounds['lon_max'])
            )
            
            # Create weights based on grid cell area (proportional to cosine of latitude)
            # This accounts for the fact that grid cells near the equator are larger than those near the poles
            weights = np.cos(np.deg2rad(region_data.lat))
            
            # Use xarray's weighted mean functionality
            # First create a DataArray of the same shape as region_data with the weights
            # We need to broadcast the weights to match the shape of region_data
            weight_factors = xr.ones_like(region_data) * weights
            
            # Calculate the weighted mean
            weighted_sum = (region_data * weight_factors).sum(dim=['lat', 'lon'])
            sum_of_weights = weight_factors.sum(dim=['lat', 'lon'])
            weighted_mean = weighted_sum / sum_of_weights
            
            # Store the mean
            regional_means[region_name][data_name] = float(weighted_mean.values)
    
    # Convert to DataFrame
    df = pd.DataFrame(regional_means)
    
    return df

# Function to create regional bar charts
def create_regional_bar_chart(data_df, title, filename, figsize=(14, 8), color_palette='coolwarm_r'):
    """
    Create a publication-quality bar chart of regional means.
    
    Parameters:
        data_df (pandas.DataFrame): DataFrame of regional means
        title (str): Title for the chart
        filename (str): Filename to save the figure
        figsize (tuple, optional): Figure size
        color_palette (str, optional): Color palette to use
    """
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    
    # Create a color palette - using coolwarm_r for better visual distinction
    # This creates a gradient from cool to warm colors
    reversed_palette = 'coolwarm'
    colors = sns.color_palette(reversed_palette, len(data_df))
    
    # Plot the data with improved spacing
    data_df.T.plot(kind='bar', ax=ax, color=colors, width=0.7, edgecolor='black', linewidth=0.5)
    
    # Add title and labels with improved styling
    plt.title(title, fontweight='bold', pad=20, fontsize=16)
    plt.ylabel('Solar Potential Change (%)', fontweight='bold', fontsize=14)
    plt.xlabel('Region', fontweight='bold', fontsize=14)
    
    # Improve x-tick labels
    plt.xticks(rotation=45, ha='right', fontweight='bold')
    
    # Improve legend
    legend = plt.legend(title='Scenario', title_fontsize=12, fontsize=10, 
                      loc='upper right', frameon=True, framealpha=0.9, edgecolor='black')
    legend.get_frame().set_linewidth(0.8)
    
    # Add grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.5, color='gray')
    
    # Add horizontal line at y=0
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.7)
    
    # Add value labels on top of bars with improved formatting
    for container in ax.containers:
        ax.bar_label(container, fmt='%.1f', fontsize=9, padding=3, fontweight='bold')
    
    # Add annotations
    plt.annotate('Data Source: CESM Climate Model', xy=(0.01, 0.01), xycoords='figure fraction', 
                fontsize=9, ha='left', va='bottom', style='italic')
    
    # Add explanatory annotation
    if "Changes" in title:
        plt.annotate('Negative values indicate increased solar potential loss', 
                    xy=(0.99, 0.01), xycoords='figure fraction', 
                    fontsize=9, ha='right', va='bottom', style='italic', color='darkred')
    else:
        plt.annotate('All values represent reduction in solar potential', 
                    xy=(0.99, 0.01), xycoords='figure fraction', 
                    fontsize=9, ha='right', va='bottom', style='italic', color='darkred')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure to {os.path.join(output_dir, filename)}")

# Function to create a comparison figure of multiple scenarios
def create_scenario_comparison_map(data_dict, title, filename, vmin=None, vmax=None, 
                                  cmap='RdBu_r', figsize=(16, 12)):
    """
    Create a multi-panel figure comparing different scenarios.
    
    Parameters:
        data_dict (dict): Dictionary of (title, data) pairs
        title (str): Main title for the figure
        filename (str): Filename to save the figure
        vmin (float, optional): Minimum value for colorbar
        vmax (float, optional): Maximum value for colorbar
        cmap (str or colormap, optional): Colormap to use
        figsize (tuple, optional): Figure size
    """
    # Determine the grid layout based on number of panels
    n_panels = len(data_dict)
    if n_panels <= 3:
        n_rows, n_cols = 1, n_panels
    elif n_panels <= 6:
        n_rows, n_cols = 2, int(np.ceil(n_panels / 2))
    else:
        n_rows, n_cols = 3, int(np.ceil(n_panels / 3))
    
    fig = plt.figure(figsize=figsize, facecolor='white')
    
    # Find global min/max if not provided
    if vmin is None or vmax is None:
        all_min = min([data.min().values for _, data in data_dict.items()])
        all_max = max([data.max().values for _, data in data_dict.items()])
        
        if cmap == 'RdBu_r' or cmap == 'RdBu':
            # For diverging data
            abs_max = max(abs(all_min), abs(all_max))
            vmin = -abs_max if vmin is None else vmin
            vmax = abs_max if vmax is None else vmax
        else:
            # For sequential data
            vmin = all_min if vmin is None else vmin
            vmax = all_max if vmax is None else vmax
    
    # Create a custom colormap with white for near-zero values
    if cmap == 'RdBu_r' or cmap == 'RdBu':
        # Create a custom colormap with white at center
        colors_rb = plt.cm.RdBu_r(np.linspace(0, 1, 256))
        # Make values near zero white (center of the colormap)
        white_threshold = 0.02  # 2% of the range
        center_idx = 128  # Center of the colormap
        threshold_idx = int(256 * white_threshold)
        for i in range(center_idx - threshold_idx, center_idx + threshold_idx):
            if i >= 0 and i < 256:  # Ensure index is valid
                colors_rb[i] = [1, 1, 1, 1]  # White with full alpha
        
        custom_cmap = mcolors.LinearSegmentedColormap.from_list('RdBu_r_white_center', colors_rb)
        cmap = custom_cmap
        norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    else:
        # Create a custom colormap with white for near-zero values
        colors_seq = plt.cm.get_cmap(cmap)(np.linspace(0, 1, 256))
        # Make values near zero white (for sequential colormap, near-zero is at the end)
        white_threshold = 0.05  # 5% of the range
        threshold_idx = int(256 * white_threshold)
        for i in range(256 - threshold_idx, 256):
            colors_seq[i] = [1, 1, 1, 1]  # White with full alpha
        
        custom_cmap = mcolors.LinearSegmentedColormap.from_list(f'{cmap}_white_low', colors_seq)
        cmap = custom_cmap
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    
    # Create each panel
    for i, (panel_title, data) in enumerate(data_dict.items()):
        ax = fig.add_subplot(n_rows, n_cols, i+1, projection=ccrs.Robinson())
        
        # Set global extent
        ax.set_global()
        
        # Add map features with improved styling
        ax.coastlines(linewidth=1.0, color='#333333')
        ax.add_feature(cfeature.BORDERS, linestyle='-', edgecolor='#777777', linewidth=0.5)
        ax.add_feature(cfeature.LAND, facecolor='#EFEFEF', alpha=0.5)
        ax.add_feature(cfeature.OCEAN, facecolor='#EAEAFF', alpha=0.5)
        
        # Add gridlines for better geographic reference
        gl = ax.gridlines(draw_labels=False, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        
        # Plot the data with slightly dimmed colors (alpha=0.8)
        im = ax.pcolormesh(
            data.lon, data.lat, data, 
            transform=ccrs.PlateCarree(),
            cmap=cmap,
            norm=norm,
            alpha=0.8,  # Dim the colors slightly
            edgecolor='face',
            linewidth=0.1
        )
        
        # Add panel title with improved styling
        ax.set_title(panel_title, fontweight='bold', fontsize=12)
    
    # Add a common colorbar with improved styling
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.02])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Solar Potential Change (%)', fontweight='bold', fontsize=12)
    cbar.ax.tick_params(labelsize=10)
    
    # Add zero line to colorbar if using diverging data
    if cmap == 'RdBu_r' or cmap == 'RdBu':
        cbar.ax.axvline(x=0, color='k', linestyle='-', linewidth=0.8, alpha=0.6)
    
    # Add main title with improved styling
    fig.suptitle(title, fontweight='bold', fontsize=16, y=0.98)
    
    # Add annotations
    plt.annotate('Data Source: CESM Climate Model', xy=(0.01, 0.01), xycoords='figure fraction', 
                fontsize=9, ha='left', va='bottom', style='italic')
    
    # Add explanatory annotation
    if cmap == 'RdBu_r' or cmap == 'RdBu':
        plt.annotate('Red = Increased Solar Potential Loss, Blue = Decreased Solar Potential Loss', 
                    xy=(0.99, 0.01), xycoords='figure fraction', 
                    fontsize=9, ha='right', va='bottom', style='italic', color='darkred')
    else:
        plt.annotate('Darker Red = Greater Solar Potential Loss due to Wildfire PM2.5', 
                    xy=(0.99, 0.01), xycoords='figure fraction', 
                    fontsize=9, ha='right', va='bottom', style='italic', color='darkred')
    
    # Adjust layout
    plt.subplots_adjust(top=0.9, bottom=0.15, wspace=0.05, hspace=0.1)
    
    # Save figure
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved figure to {os.path.join(output_dir, filename)}")

# Function to set output directory
def set_output_directory(out_dir=DEFAULT_OUTPUT_DIR):
    """
    Set the output directory for saving figures.
    
    Parameters:
        out_dir (str): Directory to save figures
    
    Returns:
        str: Path to output directory
    """
    global output_dir
    output_dir = out_dir
    return setup_visualization_env(output_dir)
