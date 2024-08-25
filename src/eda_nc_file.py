import xarray as xr
import os

# Define the path to one of the NetCDF files
file_path = "total_precipitation_2022/total_precipitation_2022_03_26.nc"

# Load the NetCDF file using xarray
ds = xr.open_dataset(file_path)

# Print the structure of the dataset
print(ds)

# Print the dimensions and coordinates
print("\nDimensions:\n", ds.dims)
print("\nCoordinates:\n", ds.coords)

# Print the variables available in the dataset
print("\nVariables:\n", ds.variables)

# Check the shapes of latitude, longitude, and precipitation data
print("\nLatitude shape:", ds['latitude'].shape)
print("Longitude shape:", ds['longitude'].shape)
print("Precipitation shape:", ds['tp'].shape)
