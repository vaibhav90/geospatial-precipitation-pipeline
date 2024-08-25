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

   

   
