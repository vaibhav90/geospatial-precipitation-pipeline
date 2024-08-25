import os
import xarray as xr
import pandas as pd
import numpy as np
import h3
import gc

# Define the input and output directories
input_directory = "total_precipitation_2022"
output_directory = "parquet_chunks"

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Resolution of H3 index (Adjust as needed)
h3_resolution = 5


def process_single_file(file_path, output_directory, index):
    try:
        # Load the NetCDF file using xarray
        ds = xr.open_dataset(file_path)

        # Extract the relevant data: time, latitude, longitude, and total precipitation
        times = pd.to_datetime(ds['time'].values)
        lats = ds['latitude'].values
        lons = ds['longitude'].values
        precipitation = ds['tp'].values  # (time, latitude, longitude)

        # Create a meshgrid for latitude and longitude to align with precipitation data
        lats_grid, lons_grid = np.meshgrid(lats, lons, indexing='ij')

        # Flatten the latitude and longitude grids
        lats_flat = lats_grid.flatten()
        lons_flat = lons_grid.flatten()

        # Compute H3 indices for all lat-lon pairs
        h3_indices = [h3.geo_to_h3(lat, lon, h3_resolution) for lat, lon in zip(lats_flat, lons_flat)]

        data_frames = []
        # Loop through each time step to extract the data and build the DataFrame
        for time_idx, time in enumerate(times):
            precip_flat = precipitation[time_idx, :, :].flatten()

            # Create a DataFrame
            df = pd.DataFrame({
                'timestamp': [time] * len(lats_flat),
                'h3_index': h3_indices,
                'latitude': lats_flat,
                'longitude': lons_flat,
                'precipitation': precip_flat
            })

            data_frames.append(df)

        # Concatenate the data for this file
        result = pd.concat(data_frames, ignore_index=True)

        # Save as a Parquet file
        output_file = os.path.join(output_directory, f"chunk_{index}.parquet")
        result.to_parquet(output_file, engine='pyarrow', compression='snappy')

        print(f"Processed and saved {output_file}")

        # Clean up intermediate variables to free memory
        del ds, times, lats, lons, precipitation, lats_grid, lons_grid, lats_flat, lons_flat, data_frames, result
        gc.collect()  # Force garbage collection

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


if __name__ == "__main__":
    # Get a list of all NetCDF files to process
    nc_files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith(".nc")]

    # Process each file individually
    for index, file_path in enumerate(nc_files):
        print(f"Processing file {index + 1}/{len(nc_files)}: {file_path}...")
        process_single_file(file_path, output_directory, index)

    print("All files have been processed and saved as individual Parquet files.")
