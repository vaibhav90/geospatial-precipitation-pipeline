FROM apache/airflow:2.6.0

# Install necessary packages
RUN pip install --user xarray pandas h3 pyarrow gcsfs

# Copy DAGs
COPY dags /opt/airflow/dags/
