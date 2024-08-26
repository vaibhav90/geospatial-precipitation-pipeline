import dask.dataframe as dd
import h3
import pandas as pd
import time

# Path to the Parquet file
parquet_file = 'total_precipitation_2022_combined_with_h3.parquet'

# Load the Parquet file with Dask
df = dd.read_parquet(parquet_file)

# Function to query by timestamp range
def query_by_timestamp(start_date, end_date):
    start_time = pd.to_datetime(start_date)
    end_time = pd.to_datetime(end_date)

    start = time.time()
    filtered_df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)].compute()
    end = time.time()

    print(f"Query by timestamp executed in {end - start:.2f} seconds.")
    return filtered_df

# Function to query by timestamp and H3 index
def query_by_timestamp_and_h3(start_date, end_date, h3_index):
    start_time = pd.to_datetime(start_date)
    end_time = pd.to_datetime(end_date)

    start = time.time()
    filtered_df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time) & (df['h3_index'] == h3_index)].compute()
    end = time.time()

    print(f"Query by timestamp and H3 index executed in {end - start:.2f} seconds.")
    return filtered_df

if __name__ == '__main__':
    # Query 1: Filter by a specific time range
    print("Running Query 1: Filtering by Timestamp Range")
    result_1 = query_by_timestamp("2022-07-30", "2022-08-08")
    print(result_1.head())

    # Query 2: Filter by both timestamp and H3 index
    print("\nRunning Query 2: Filtering by Timestamp and H3 Index")
    # Example H3 index for the chosen coordinates
    chosen_h3_index = h3.geo_to_h3(30.75, 196.50, 6)

    result_2 = query_by_timestamp_and_h3("2022-07-30", "2022-08-08", chosen_h3_index)
    print(result_2.head())
