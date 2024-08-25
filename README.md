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