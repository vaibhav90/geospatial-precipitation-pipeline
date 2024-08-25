# Total Precipitation Data Processing and Query Pipeline

This project aims to process and query global precipitation data using a geospatial indexing method (H3) for efficient queries based on both time and location.

## 1. Machine Configuration

This project is running on the following machine configuration. The choice of this setup was primarily based on availability and to explore the challenges of handling large-scale data processing in a resource-constrained environment:

- **Operating System**: Ubuntu Linux 24.04 LTS
- **Virtual Machine Type**: Standard D16ads v5
- **vCPUs**: 16
- **Memory**: 64 GiB
- **Disk Space**: 128 GB

## 2. Python Version and Code Style Guidelines

For this project, the following Python version and guidelines are being used:

- **Python Version**: Python 3.12.2
- **Code Style Guide**: [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- **Git Commit Conventions**: [Conventional Commits Specification](https://www.conventionalcommits.org/en/v1.0.0/)

By adhering to these guidelines, the project aims to maintain readability, consistency, and a standardized commit history for easier collaboration and tracking of changes.

## 3. Installing Project Dependencies

Given the above choices and the dataset location, the following system-level prerequisites and Python packages are required to run the project:

1. **Update System Packages and Install Python 3, Pip3 and Google Cloud SDK**:
   ```bash
   sudo apt update && sudo apt upgrade -y 
   sudo apt install python3 python3-pip -y
   sudo apt-get install apt-transport-https ca-certificates gnupg
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   sudo apt-get install google-cloud-sdk
    ```
2. **Install Git**:
    ```bash
    sudo apt install git -y
    ```
3. Create python requirements
    ```bash
    touch requirements.txt
    echo "xarray==0.19.0" >> requirements.txt
    echo "pandas==1.3.3" >> requirements.txt
    echo "h3==3.7.3" >> requirements.txt
    echo "dask==2021.9.1" >> requirements.txt
    echo "gcsfs==2021.10.0" >> requirements.txt
    echo "gsutil==4.68" >> requirements.txt
    echo "pyarrow==5.0.0" >> requirements.txt
    ```
4. **Install Python Dependencies**:
    ```bash
    pip3 install -r requirements.txt
    ```


## 4. Exploring the Dataset and Narrowing Down the Scope

### 4.1 Understanding the Data Repository

The source data for this project is hosted in the ARCO ERA5 dataset, which is a comprehensive collection of climate and Iather data. The data repository is structured hierarchically and contains various atmospheric variables across multiple years, stored in NetCDF format.

The ERA5 dataset is massive and includes different types of meteorological data, like temperature, humidity, wind speed, and more. For this project, I are only concerned with total precipitation data for the year 2022. The specific path within the repository containing the data I need is:

```bash
gs://gcp-public-data-arco-era5/raw/date-variable-single_level/2022/
```

Within this path, the data is organized by date, variable, and spatial level. For example:

```bash
gs://gcp-public-data-arco-era5/raw/date-variable-single_level/2022/01/01/total_precipitation/surface.nc
```

This structure indicates:

- **Year**: 2022
- **Month**: 01 (January)
- **Day**: 01
- **Variable**: total_precipitation
- **Level**: surface

Given that the repository contains data for all days of the year, the total size of the dataset is significant. To avoid overwhelming our processing capabilities, I focused on downloading only the data I require.

### 4.2 Deciding What to Download

After inspecting the dataset's structure, I made the following decisions:

- **Variable Selection**: I narroId down to `total_precipitation` as the variable of interest.
- **Temporal Range**: I decided to download the data for the entire year 2022.
- **Spatial Resolution**: I kept the default surface level, as it gives a global perspective of total precipitation.

### 4.3 Steps Taken to Download the Data

I used `gsutil`, a command-line tool for accessing Google Cloud Storage, to download the required files. 
The key challenge was managing the large number of files (365 days of data), where each file contains hourly data for that day. 
To avoid overwriting files (since each file is named `surface.nc`), I wrote a Python script to handle downloading and renaming each file based on the date.

The following command illustrates how I initially tested downloading the data:

```bash
gsutil cp gs://gcp-public-data-arco-era5/raw/date-variable-single_level/2022/*/*/total_precipitation/surface.nc .
```

However, due to potential overwriting, I switched to using a Python script (`src/download_raw_datasets.py`) to:

1. Download each file.
2. Rename each file based on the date.
3. Organize them into a directory (`/total_precipitation_2022`) for further processing.

Each NetCDF file is approximately 48 MB in size:

```bash
vkulkarn@mymachine:~/geopipe$ ls -lh total_precipitation_2022/total_precipitation_2022_01_01.nc
-rw-rw-r-- 1 vkulkarn vkulkarn 48M Aug 23 17:41 total_precipitation_2022/total_precipitation_2022_01_01.nc
vkulkarn@mymachine:~/geopipe$ ls -lh total_precipitation_2022/
total 17G
```

## 5. Examining the Structure of the Downloaded Data

Before proceeding with data processing, it is essential to understand how the NetCDF files are structured and what kind of information they contain. This allows us to better plan the data transformation pipeline.
I used a Python script (`src/eda_nc_file.py`) to inspect the structure of the NetCDF files and examine the dataset’s contents. The goal was to identify the available dimensions, coordinates, and variables in the dataset.

```bash
<xarray.Dataset> Size: 199MB
Dimensions:    (longitude: 1440, latitude: 721, time: 24)
Coordinates:
  * longitude  (longitude) float32 6kB 0.0 0.25 0.5 0.75 ... 359.2 359.5 359.8
  * latitude   (latitude) float32 3kB 90.0 89.75 89.5 ... -89.5 -89.75 -90.0
  * time       (time) datetime64[ns] 192B 2022-03-26 ... 2022-03-26T23:00:00
Data variables:
    tp         (time, latitude, longitude) float64 199MB ...
Attributes:
    Conventions:  CF-1.6
    history:      2022-10-11 18:00:20 GMT by grib_to_netcdf-2.25.1: /opt/ecmw...

Dimensions:
 FrozenMappingWarningOnValuesAccess({'longitude': 1440, 'latitude': 721, 'time': 24})

Coordinates:
 Coordinates:
  * longitude  (longitude) float32 6kB 0.0 0.25 0.5 0.75 ... 359.2 359.5 359.8
  * latitude   (latitude) float32 3kB 90.0 89.75 89.5 ... -89.5 -89.75 -90.0
  * time       (time) datetime64[ns] 192B 2022-03-26 ... 2022-03-26T23:00:00

Variables:
 Frozen({'longitude': <xarray.IndexVariable 'longitude' (longitude: 1440)> Size: 6kB
array([0.0000e+00, 2.5000e-01, 5.0000e-01, ..., 3.5925e+02, 3.5950e+02,
       3.5975e+02], dtype=float32)
Attributes:
    units:      degrees_east
    long_name:  longitude, 'latitude': <xarray.IndexVariable 'latitude' (latitude: 721)> Size: 3kB
array([ 90.  ,  89.75,  89.5 , ..., -89.5 , -89.75, -90.  ], dtype=float32)
Attributes:
    units:      degrees_north
    long_name:  latitude, 'time': <xarray.IndexVariable 'time' (time: 24)> Size: 192B
array(['2022-03-26T00:00:00.000000000', '2022-03-26T01:00:00.000000000',
       '2022-03-26T02:00:00.000000000', '2022-03-26T03:00:00.000000000',
       '2022-03-26T04:00:00.000000000', '2022-03-26T05:00:00.000000000',
       '2022-03-26T06:00:00.000000000', '2022-03-26T07:00:00.000000000',
       '2022-03-26T08:00:00.000000000', '2022-03-26T09:00:00.000000000',
       '2022-03-26T10:00:00.000000000', '2022-03-26T11:00:00.000000000',
       '2022-03-26T12:00:00.000000000', '2022-03-26T13:00:00.000000000',
       '2022-03-26T14:00:00.000000000', '2022-03-26T15:00:00.000000000',
       '2022-03-26T16:00:00.000000000', '2022-03-26T17:00:00.000000000',
       '2022-03-26T18:00:00.000000000', '2022-03-26T19:00:00.000000000',
       '2022-03-26T20:00:00.000000000', '2022-03-26T21:00:00.000000000',
       '2022-03-26T22:00:00.000000000', '2022-03-26T23:00:00.000000000'],
      dtype='datetime64[ns]')
Attributes:
    long_name:  time, 'tp': <xarray.Variable (time: 24, latitude: 721, longitude: 1440)> Size: 199MB
[24917760 values with dtype=float64]
Attributes:
    units:      m
    long_name:  Total precipitation})

Latitude shape: (721,)
Longitude shape: (1440,)
Precipitation shape: (24, 721, 1440)
```