from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import xarray as xr
import h3
import requests

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'daily_precipitation_pipeline',
    default_args=default_args,
    description='Pipeline to fetch and process daily precipitation data',
    schedule_interval=timedelta(days=1),
    catchup=False,
)


# Task 1: Download the NetCDF file
def download_daily_data(execution_date, **kwargs):
    date_str = execution_date.strftime('%Y-%m-%d')
    file_url = f"gs://gcp-public-data-arco-era5/raw/date-variable-single_level/{execution_date.year}/{execution_date.month:02}/{execution_date.day:02}/total_precipitation/surface.nc"
    local_file_path = f"/tmp/total_precipitation_{date_str}.nc"

    os.system(f"gsutil cp {file_url} {local_file_path}")

    return local_file_path


# Task 2: Process NetCDF file and compute H3 index
def process_and_compute_h3(local_file_path, **kwargs):
    ds = xr.open_dataset(local_file_path)
    df_list = []

    for time_idx in range(len(ds.time)):
        time = pd.to_datetime(str(ds.time[time_idx].values))
        latitudes = ds['latitude'].values
        longitudes = ds['longitude'].values
        precipitation = ds['tp'][time_idx, :, :].values

        lat_grid, lon_grid = np.meshgrid(latitudes, longitudes, indexing='ij')
        h3_indices = [h3.geo_to_h3(lat, lon, 6) for lat, lon in zip(lat_grid.flatten(), lon_grid.flatten())]

        df = pd.DataFrame({
            'timestamp': time,
            'latitude': lat_grid.flatten(),
            'longitude': lon_grid.flatten(),
            'precipitation': precipitation.flatten(),
            'h3_index': h3_indices
        })

        df_list.append(df)

    combined_df = pd.concat(df_list, ignore_index=True)
    parquet_file_path = local_file_path.replace('.nc', '.parquet')

    table = pa.Table.from_pandas(combined_df)
    pq.write_table(table, parquet_file_path)

    return parquet_file_path


# Task 3: Append data to the combined Parquet file
def append_to_combined_parquet(parquet_file_path, **kwargs):
    combined_parquet = 'total_precipitation_2022_combined_with_h3.parquet'

    new_data = pd.read_parquet(parquet_file_path)
    combined_data = pd.read_parquet(combined_parquet)

    final_data = pd.concat([combined_data, new_data], ignore_index=True)
    table = pa.Table.from_pandas(final_data)
    pq.write_table(table, combined_parquet)

    os.remove(parquet_file_path)


# Define tasks
download_task = PythonOperator(
    task_id='download_daily_data',
    python_callable=download_daily_data,
    provide_context=True,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_and_compute_h3',
    python_callable=process_and_compute_h3,
    provide_context=True,
    dag=dag,
)

append_task = PythonOperator(
    task_id='append_to_combined_parquet',
    python_callable=append_to_combined_parquet,
    provide_context=True,
    dag=dag,
)

# Define task dependencies
download_task >> process_task >> append_task
