"""
Author: Saeed Mansour
Date: 2025-02-21

Description:
This script reads a CSV file in chunks and inserts the data into a PostgreSQL database.
The script reads the database connection details and file path from a 'config.json' file.
The script also logs the process to a file in the 'logs' directory.
"""

# Import the necessary libraries and modules
import os
import sys
import json
import logging
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values

# Display settings
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 100)


# Function to safely convert values to BIGINT
def safe_bigint(value) -> int or None:
    """
    Safely convert a value to BIGINT
    :param value:
    :return:
    """
    try:
        return int(value) if pd.notna(value) and value != "" else None
    except ValueError:
        return None  # Ensures very large values don't cause issues


# Function to process and insert chunks
def process_and_insert_chunk(chunk) -> int:
    """
    Process and insert a chunk of data into the database
    :param chunk:
    :return:
    """
    chunk = chunk.copy()  # Avoid SettingWithCopyWarning

    # Drop rows with missing essential values
    chunk.dropna(subset=["x", "y", "dir", "vel", "dt", "stato",  "id_veicolo", "classe_veicolo", "mm_id_zona", "mm_fid"], inplace=True)

    # Convert `dt` column to datetime format
    chunk["dt"] = pd.to_datetime(chunk["dt"], errors='coerce')

    # Convert `zone_id (mm_id_zona)` and `fid (mm_fid)` to BIGINT safely
    chunk["mm_id_zona"] = chunk["mm_id_zona"].apply(safe_bigint)
    chunk["mm_fid"] = chunk["mm_fid"].apply(safe_bigint)

    # Replace NaN values with None for PostgreSQL compatibility
    chunk = chunk.where(pd.notna(chunk), None)

    # Insert data into database
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO data.data (gid, x, y, direction, velocity, dt, status, vehicle_id, vehicle_class, zone_id, fid, ts_insert)
        VALUES %s
        """

        values = [
            (
                safe_bigint(row["gid"]),
                float(row["x"]),
                float(row["y"]),
                row["dir"],
                float(row["vel"]),
                row["dt"],
                row["stato"],
                safe_bigint(row["id_veicolo"]),
                row["classe_veicolo"],
                safe_bigint(row["mm_id_zona"]),
                safe_bigint(row["mm_fid"]),
                row["ts_insert"]
            )
            for _, row in chunk.iterrows()
        ]

        execute_values(cursor, insert_query, values)
        conn.commit()

        return len(values)

    except Exception as e:
        print(f"Error processing chunk: {e}")
        return 0

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":

    log_folder = "logs"
    log_name = os.path.basename(__file__)
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # Configure logging
    logging.basicConfig(
        filename=f"logs/{log_name}.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    try:
        with open("config.json", "r") as file:
            config = json.load(file)

        dbname = config["database"]["dbname"]
        user = config["database"]["user"]
        password = config["database"]["password"]
        host = config["database"]["host"]
        port = config["database"]["port"]
        file_path = config["input_data"]["data_name"]
        chunk_size = config["input_data"]["chunk_size"]
        logging.info("Config file loaded successfully.")
    except FileNotFoundError:
        logging.error("Config file not found. Please ensure a 'config.json' file exists in the root directory.")

    # Database connection details
    DB_PARAMS = {
        "dbname": dbname,
        "user": user,
        "password": password,
        "host": host,
        "port": port
    }

    logging.info("Starting data import process.")

    # Process the file in chunks
    total_inserted = 0
    total_chunks = 0

    try:
        # Read and insert data in chunks
        data_path = os.path.join("data", file_path)
        for item in pd.read_csv(data_path, chunksize=chunk_size):
            total_chunks += 1
            records_inserted = process_and_insert_chunk(item)
            total_inserted += records_inserted
            logging.info(f"Chunk {total_chunks}: Inserted {records_inserted} records")

        logging.info(f"Completed importing data: {total_inserted} total records inserted in {total_chunks} chunks")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)
