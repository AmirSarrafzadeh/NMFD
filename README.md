# Welcome to My Repository
<img src="https://media.wired.com/photos/5cc3664f4ef5ad318eea382e/master/w_2560%2Cc_limit/Car-hack-1144980326.jpg" alt="Photo">

# NMFD Project

## Overview
In this project the first script reads a CSV file in chunks and inserts the data into a PostgreSQL database. It processes data efficiently, handles missing values, converts necessary fields, and logs the process to a file in the `logs` directory. The script reads database connection details and file paths from a `config.json` file.

## Features
- Read large CSV files in chunks for efficient processing.
- Cleans and formats data before inserting into the database.
- Uses `psycopg2` for PostgreSQL database operations.
- Log all operations for debugging and monitoring.

## Requirements
Ensure you have the following dependencies installed:

```
pip install pandas psycopg2
```
## Project Structure

```
├── data/                                      # Directory for storing input CSV files
├── logs/                                      # Directory for storing log files
├── config.json                                # Configuration file with database credentials and file details
├── 01_read_and_insert_data_into_database.py   # Main script for processing and inserting CSV data into database
├── 02_unique_vehicle_id_time_intervals.py     # Preprocessing the data and calculating the flow and density
├── 03_data_visualization                      # Main script for data visualization
└── README.md                                  # Documentation file
```

## Configuration
Create a config.json file in the root directory with the following structure:

```
{
  "input_data": {
    "data_name": "csv file name",
    "chunk_size": 1000000,
    "zone_filename": "zone file name",
    "zone_column": "Zone ID"
  },
  "database": {
    "dbname": "database name",
    "schema": "schema name",
    "table_name": "dtable name",
    "user": "username",
    "password": "password",
    "host": "host",
    "port": port number
  },
  "operation": {
    "time_interval": "5min",
    "dt_column": "datetime",
    "vehicle_id_column": "vehicle_id",
    "zone_id_column": "zone_id",
    "vehicle_class_column": "vehicle_class",
    "vehicle_type": "A"
  },
  "output_data": {
    "vehicle_numbers_column": "vehicle_numbers",
    "vehicle_ids_column": "vehicle_ids",
    "output_filename": "output file name"
  }
}
```

## Usage
Place all your CSV file inside the data/ directory.

Ensure config.json is correctly configured with your database credentials and file details.

Run the script using:

```
python script names
```
The first script will process the file in chunks, inserting the data into the PostgreSQL database while logging the process.

## Logging
Logs are stored in the logs/ directory.
The log file is named after the script filename (import_data.py.log).
It records errors, successful inserts, and chunk-wise progress.

## Error Handling
If the config.json file is missing, an error message is logged.
If an error occurs during database insertion, it is caught and logged without stopping the entire process.

License
This project is licensed under the MIT License.
