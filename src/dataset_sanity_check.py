import dask.dataframe as dd

# Path to the generated Parquet file
parquet_file = 'final_parquet_dataset/total_precipitation_2022_combined_with_h3.parquet'

# Load the Parquet file with Dask
df = dd.read_parquet(parquet_file)

# Display the column names
print("Columns in the dataset:", df.columns)

# Show a sample of the data
print(df.head())


# Print a sample of unique H3 indices in the dataset
unique_h3_indices = df['h3_index'].unique().compute()
print(unique_h3_indices[:10])  # Show the first 10 unique H3 indices