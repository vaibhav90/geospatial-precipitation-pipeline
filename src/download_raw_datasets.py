import os
import gcsfs

# Init GCS filesystem
fs = gcsfs.GCSFileSystem()

# base path
base_path = 'gcp-public-data-arco-era5/raw/date-variable-single_level/2022'

# Create the target directory
output_directory = "total_precipitation_2022_raw"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Get the list of all directories for each month
months = fs.ls(base_path)

for month in months:
    # Get the list of directories for each day within the month
    days = fs.ls(month)

    for day in days:
        # Define the path to the total_precipitation directory
        tp_path = f"{day}/total_precipitation/surface.nc"

        # Check if the file exists
        if fs.exists(tp_path):
            # Extract the date information from the directory structure
            date_info = day.split('/')[-3:]  # Extracts [year, month, day]
            date_string = f"{date_info[0]}_{date_info[1]}_{date_info[2]}"  # Format: year_month_day

            # Define a unique file name using the date
            local_filename = os.path.join(output_directory, f"total_precipitation_{date_string}.nc")

            # Download the file
            with fs.open(tp_path, 'rb') as fsrc:
                with open(local_filename, 'wb') as fdst:
                    fdst.write(fsrc.read())

            print(f"Downloaded {local_filename}")

print("Download completed.")
