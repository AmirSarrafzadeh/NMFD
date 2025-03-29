# Import the necessary libraries and modules
import os
import json
import logging
import pandas as pd
from sqlalchemy import create_engine
import warnings

warnings.filterwarnings("ignore")

# Display settings
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)

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
        schema = config["database"]["schema"]
        table_name = config["database"]["table_name"]
        zone_filename = config["input_data"]["zone_filename"]
        zone_column = config["input_data"]["zone_column"]
        time_interval = config["operation"]["time_interval"]
        vehicle_id_column = config["operation"]["vehicle_id_column"]
        zone_id_column = config["operation"]["zone_id_column"]
        fid_column = config["operation"]["fid_column"]
        vehicle_class_column = config["operation"]["vehicle_class_column"]
        vehicle_type = config["operation"]["vehicle_type"]
        velocity_column = config["operation"]["velocity_column"]
        output_filename = config["output_data"]["output_filename"]
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

    data_path = os.path.join("data", zone_filename)
    links = pd.read_csv(os.path.join("data", "links.csv"))
    zones = pd.read_csv(data_path)
    zone_ids = zones[zone_column].tolist()

    # Create SQLAlchemy engine
    engine = create_engine(
        f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}")

    final_data = {}
    flat_rows = []  # To store flattened rows

    for i in range(1, 31):
        table_name = config["database"]["table_name"]
        selected_date = "-".join(table_name.split("_")[1:])
        if i < 10:
            selected_date = f"{selected_date}-0{i}"
            table_name = f"{table_name}_0{i}"
        else:
            selected_date = f"{selected_date}-{i}"
            table_name = f"{table_name}_{i}"

        query = f"""
                        SELECT dt, {zone_id_column}, {fid_column}
                        FROM {schema}."{table_name}"
                        WHERE {vehicle_class_column} = '{vehicle_type}' AND {zone_id_column} in {tuple(zone_ids)}
                        ORDER BY dt;
                    """
        df = pd.read_sql(query, engine)
        df["dt"] = pd.to_datetime(df["dt"])
        top_zids = df['zone_id'].value_counts().head().to_dict()

        # Collect flattened rows
        for zid, count in top_zids.items():
            flat_rows.append({
                "date": selected_date,
                "zone_id": zid,
                "count": count
            })

    # Convert the flat list of records to a DataFrame and save as CSV
    df_flat = pd.DataFrame(flat_rows)
    df_flat.to_csv("data/dense_zones.csv", index=False)
    logging.info("CSV file saved successfully as 'data/dense_zones_links.csv'.")
