# Total Precipitation Data Processing and Query Pipeline

This project aims to process and query global precipitation data (Year 2022) from ARCO ERA5 using a geospatial indexing method (H3) for efficient queries based on both time and location.
The project will show share how one can productionize such a data processing pipeline and make it scalable for large-scale data processing on a resource-constrained environment.

## 1. Machine Configuration

I have the following Linux-box setup for this project.
The choice of this setup was primarily based on availability and to explore the challenges of handling large-scale data processing in a resource-constrained environment. 
The machine configuration is as follows:

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

## 3. Installing Project Dependencies

Given the above choices and the dataset, the following system-level prerequisites and Python packages are required to run the project, based on my preliminary analysis of the dataset and the processing requirements.

1. **Update System Packages and Install Python3, Pip3, GCloud SDK and GIT**:
   ```bash
   sudo apt update && sudo apt upgrade -y 
   sudo apt install python3 python3-pip -y
   sudo apt-get install apt-transport-https ca-certificates gnupg
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   sudo apt-get install google-cloud-sdk
   sudo apt-get install git
    ```
2. Create python requirements file and install the required packages:
    ```bash
    touch requirements.txt
    echo "xarray==0.19.0" >> requirements.txt
    echo "pandas==1.3.3" >> requirements.txt
    echo "h3==3.7.3" >> requirements.txt
    echo "dask==2021.9.1" >> requirements.txt
    echo "gcsfs==2021.10.0" >> requirements.txt
    echo "gsutil==4.68" >> requirements.txt
    echo "pyarrow==5.0.0" >> requirements.txt
    pip3 install -r requirements.txt
    ```

## 4. Exploring the Dataset

### 4.1 Understanding the Data Repository

The source data for this project is hosted in the ARCO ERA5 dataset, The data repository is structured hierarchically and contains various atmospheric variables across multiple years, stored in NetCDF format.
The ERA5 dataset is massive and includes different types of meteorological data, like temperature, humidity, wind speed, and more. 
For this project, I am only concerned with total precipitation data for the year 2022. The specific path within the repository containing the data I need is:
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

### 4.2 Steps Taken to Download the Data

I used `gsutil`, a command-line tool for accessing Google Cloud Storage, to download the required files.  
To avoid overwriting files (since each file is named `surface.nc`), I wrote a Python script to handle downloading and renaming each file based on the date.
The following command illustrates how I initially tested downloading the data:

```bash
gsutil cp gs://gcp-public-data-arco-era5/raw/date-variable-single_level/2022/*/*/total_precipitation/surface.nc .
```

I switched to using a Python script (`src/download_raw_datasets.py`) to have more control over the download process. The script performs the following steps:

1. Download each file.
2. Rename each file based on the date.
3. Organize them into a directory (`/total_precipitation_2022`) for further processing.

Each NetCDF file is approximately 48 MB in size:

```bash
vkulkarn@mymachine:~/geopipe$ ls -lh total_precipitation_2022/total_precipitation_2022_01_01.nc
-rw-rw-r-- 1 vkulkarn vkulkarn 48M total_precipitation_2022/total_precipitation_2022_01_01.nc
vkulkarn@mymachine:~/geopipe$ ls -lh total_precipitation_2022/
total 17G
```

## 5. Examining the Structure of the Downloaded Data

I used a Python script (`src/eda_nc_file.py`) to inspect the structure of the NetCDF files and examine the dataset’s contents. 
I wanted to identify the available dimensions, coordinates, and variables in the dataset.

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

## 6. Deciding on the Data Processing Strategy: All-at-Once vs. Sequential Processing

Given the size of the dataset and the memory limitations of the available machine, one of the key challenges was deciding whether to process all the raw NetCDF files into Parquet format in a single step or to break down the process into sequential stages. 
The following considerations were taken into account:

### 6.1 Processing All Files at Once

Initially, the idea was to load all the raw NetCDF files, apply the necessary transformations, create H3 geospatial indices, and then combine everything into a single Parquet dataset.
However, after estimating the memory requirements, it was clear that the machine would not be able to handle the entire dataset at once, especially when considering the intermediate steps of adding H3 indices and combining the data.
Obviously, this could have been achieved using a carefully curated batch processing strategy, but the memory constraints would have made it challenging to find the optimal batch size.
Furthermore, since I decided to use Python and my experience with python's garbage collection, I was not confident that the memory would be released efficiently after processing each file, which could lead to memory leaks and potential crashes.

### 6.2 Sequential Processing:

To address these limitations, I opted for a safer and more memory-efficient approach by breaking down the data processing into sequential stages. The process was divided into three main steps:

1. **Step 1: Convert Raw NetCDF Files to Parquet**:
   - Each NetCDF file was individually converted to Parquet format, ensuring that each day’s data was stored in a separate Parquet file.

2. **Step 2: Compute H3 Indices and Combine Data**:
   - After converting the raw data to Parquet, the next step was to compute the H3 geospatial indices for each latitude and longitude pair.
   - The data was then combined into a single Parquet file, which would be used for querying.

I wanted to be sure that I can execute the script in the night and wake up to see it completed successfully in the morning.

## 7. Considerations for Transforming NetCDF to Parquet

The NetCDF file structure cannot be directly transformed into a Parquet file without some intermediate steps for several key reasons:

### 7.1 Dimensional Structure

NetCDF files are multidimensional, with variables organized along dimensions like latitude, longitude, and time.
Parquet files, however, are columnar and tabular in nature, designed for flat data structures.
This difference in structure necessitates transforming the multidimensional NetCDF data into a flat, tabular format before converting it into Parquet.

### 7.2 Coordinate System

In the NetCDF file, latitude and longitude are separate 1-dimensional arrays, while the precipitation data is a 3-dimensional array (time, latitude, longitude).
To convert this into a tabular format suitable for Parquet, the structure needs to be "flattened" so that each combination of time, latitude, and longitude corresponds to a unique row in the corresponding Parquet file.

### 7.3 Data Alignment

To ensure the spatial and temporal relationships in the data are preserved during the transformation, the precipitation data needs to be aligned with the correct latitude and longitude values for each data point.
This involves creating a meshgrid of coordinates and then flattening both the coordinate arrays and the precipitation data.

### 7.4 H3 Index Computation

In addition to the basic transformation, I also compute the H3 index for each latitude-longitude pair.
The H3 index is computed using the `h3` library, with a specified resolution (in this case, resolution 5). This adds an additional column to our Parquet file, allowing for geospatial operations and queries based on the H3 hexagonal grid system.
The script to convert the NetCDF files to Parquet (`src/convert_nc_to_parquet.py`) performs these steps, including H3 index computation, and ensures that the data is correctly transformed, aligned, with geospatial indexing before being saved in Parquet format.

I ensured that there is no data loss during the transformation process, and the addition of the H3 index provides enhanced capabilities for spatial analysis without altering the original meteorological data.

```bash
Columns:
Index(['timestamp', 'h3_index', 'latitude', 'longitude', 'precipitation'], dtype='object')

Data Types:
timestamp        datetime64[ns]
h3_index                 object
latitude                float32
longitude               float32
precipitation           float64
dtype: object

First few rows:
   timestamp         h3_index  latitude  longitude  precipitation
0 2022-03-26  85032623fffffff      90.0       0.00       0.000012
1 2022-03-26  85032623fffffff      90.0       0.25       0.000012
2 2022-03-26  85032623fffffff      90.0       0.50       0.000012
3 2022-03-26  85032623fffffff      90.0       0.75       0.000012
4 2022-03-26  85032623fffffff      90.0       1.00       0.000012

Basic Statistics:
                           timestamp      latitude     longitude  precipitation
count                       24917760  2.491776e+07  2.491776e+07   2.491776e+07
mean   2022-03-26 11:30:00.000005632  0.000000e+00  1.798752e+02   9.758917e-05
min              2022-03-26 00:00:00 -9.000000e+01  0.000000e+00   0.000000e+00
25%              2022-03-26 05:45:00 -4.500000e+01  8.993750e+01   0.000000e+00
50%              2022-03-26 11:30:00  0.000000e+00  1.798750e+02   3.719058e-06
75%              2022-03-26 17:15:00  4.500000e+01  2.698125e+02   3.905011e-05
max              2022-03-26 23:00:00  9.000000e+01  3.597500e+02   3.046513e-02
std                              NaN  5.203364e+01  1.039230e+02   4.158916e-04

DataFrame Info:
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 24917760 entries, 0 to 24917759
Data columns (total 5 columns):
 #   Column         Dtype         
---  ------         -----         
 0   timestamp      datetime64[ns]
 1   h3_index       object        
 2   latitude       float32       
 3   longitude      float32       
 4   precipitation  float64       
dtypes: datetime64[ns](1), float32(2), float64(1), object(1)
memory usage: 760.4+ MB
```

## 8. Combining Parquet Files into a Single Dataset

After transforming each of the NetCDF files into Parquet format, the next step was to combine these individual Parquet files into a single consolidated dataset. 
The script (`src/consolidate_parquet_to_query_dataset`) reads all the Parquet files in the directory, concatenates them into a single DataFrame, and then saves the combined dataset as a single Parquet file.

To verify the integrity and structure of our final combined Parquet file, I implemented a sanity check script using Dask, a library for parallel computing in Python.
This scripted tests the Data Loading Verification, Schema Validation, Data Sampling, H3 Index Verification. The below was the output of the sanity check script:

```bash
Columns in the dataset: Index(['timestamp', 'h3_index', 'latitude', 'longitude', 'precipitation'], dtype='object')
   timestamp         h3_index  latitude  longitude  precipitation
0 2022-08-04  860326237ffffff      90.0       0.00       0.000042
1 2022-08-04  860326237ffffff      90.0       0.25       0.000042
2 2022-08-04  860326237ffffff      90.0       0.50       0.000042
3 2022-08-04  860326237ffffff      90.0       0.75       0.000042
4 2022-08-04  860326237ffffff      90.0       1.00       0.000042
0    860326b5fffffff
1    8600cdaefffffff
2    8600cdb9fffffff
3    8600cd04fffffff
4    860321c07ffffff
5    860334017ffffff
6    860333a87ffffff
7    8600e8417ffffff
8    86030004fffffff
9    860301d87ffffff
Name: h3_index, dtype: string
```

## 8. Querying the Processed Data

After processing the raw NetCDF files into a combined Parquet file format,  validation that the data is both accessible and performant when querying in needed.
The below queries were implemented and tested (`src/example_queries`). 

1. **Query by Timestamp Range:**
   - This query filters the data based on a specified time range. It is useful for retrieving all precipitation data within a specific period, regardless of location. This query was selected to validate the temporal filtering of the dataset.

2. **Query by Timestamp and H3 Geospatial Index:**
   - This query combines both time and location-based filtering. It retrieves data from a specific time range for a precise geographic location, represented by an H3 index. This query was chosen to test both spatial and temporal dimensions, ensuring the processed dataset can handle geospatial queries efficiently.

The results of the queries were as below:

```bash
Running Query 1: Filtering by Timestamp Range
Query by timestamp executed in 156.79 seconds.
   timestamp         h3_index  latitude  longitude  precipitation
0 2022-08-04  860326237ffffff      90.0       0.00       0.000042
1 2022-08-04  860326237ffffff      90.0       0.25       0.000042
2 2022-08-04  860326237ffffff      90.0       0.50       0.000042
3 2022-08-04  860326237ffffff      90.0       0.75       0.000042
4 2022-08-04  860326237ffffff      90.0       1.00       0.000042

Running Query 2: Filtering by Timestamp and H3 Index
Query by timestamp and H3 index executed in 176.15 seconds.
                  timestamp         h3_index  latitude  longitude  precipitation
342066  2022-08-04 00:00:00  864740407ffffff     30.75      196.5       0.000013
1380306 2022-08-04 01:00:00  864740407ffffff     30.75      196.5       0.000105
2418546 2022-08-04 02:00:00  864740407ffffff     30.75      196.5       0.000011
3456786 2022-08-04 03:00:00  864740407ffffff     30.75      196.5       0.000039
4495026 2022-08-04 04:00:00  864740407ffffff     30.75      196.5       0.000047
```

### 9. Results

The execution of these queries demonstrated that the data pipeline works effectively. Both queries returned valid results, confirming that the transformation and indexing processes were successful. This marks a significant step towards making this dataset queryable by users based on both time and geographic location.

These sample queries validate that the processed precipitation data is not only correctly indexed but also quickly accessible for both temporal and spatial analysis.


## 10. Timeframes & References

The entire project took me ~3 Hours of active time including the setup, exploration, and processing of the dataset. 
The project was completed in a single day, and the results were verified the next day. For scripting and testing, I used [Github Copilot](https://github.com/features/copilot). 
I also tested how Copilot compared with [Claude-Sonnet](https://www.anthropic.com/news/claude-3-5-sonnet) and now can see the potential of using Claude-Sonnet for such projects.

1. [ERA5 data](https://cloud.google.com/storage/docs/public-datasets/era5)
2. [Recipes for reproducing Analysis-Ready & Cloud Optimized (ARCO) ERA5 datasets](https://github.com/google-research/arco-era5)