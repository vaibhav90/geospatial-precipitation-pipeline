import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Define the input and output directories
input_directory = "parquet_chunks"
output_file = "total_precipitation_2022_combined.parquet"

def combine_parquet_files(input_directory, output_file, batch_size=10):
    parquet_files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith(".parquet")]

    writer = None

    for i in range(0, len(parquet_files), batch_size):
        batch_files = parquet_files[i:i + batch_size]
        print(f"Processing files {i + 1} to {min(i + batch_size, len(parquet_files))} out of {len(parquet_files)}...")

        dataframes = [pd.read_parquet(file) for file in batch_files]
        combined_df = pd.concat(dataframes, ignore_index=True)

        table = pa.Table.from_pandas(combined_df)

        if writer is None:
            writer = pq.ParquetWriter(output_file, table.schema)

        writer.write_table(table)

        del dataframes, combined_df, table

    if writer is not None:
        writer.close()

    print(f"Combined Parquet file saved as {output_file}")

if __name__ == "__main__":
    combine_parquet_files(input_directory, output_file, batch_size=10)