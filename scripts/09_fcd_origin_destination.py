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

    df_list = []
    all_df = []

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
                        SELECT *
                        FROM {schema}."{table_name}"
                        WHERE {vehicle_class_column} = '{vehicle_type}' AND {zone_id_column} in {tuple(zone_ids)}
                        ORDER BY dt;
                    """
        df = pd.read_sql(query, engine)
        df["dt"] = pd.to_datetime(df["dt"])

        # Sort by vehicle and time
        df = df.sort_values(by=['vehicle_id', 'dt'])

        # Compute time difference in seconds
        df['prev_time'] = df.groupby('vehicle_id')['dt'].shift()
        df['time_diff'] = (df['dt'] - df['prev_time']).dt.total_seconds()

        # Flag new trips when time difference > 600 seconds (10 minutes)
        df['is_new_trip'] = (df['time_diff'] > 600) | (df['time_diff'].isna())

        # Assign trip IDs using cumulative sum
        df['trip_id'] = df.groupby('vehicle_id')['is_new_trip'].cumsum()

        # Step 1: Detect changes in either vehicle_id or trip_id
        changes = (df['vehicle_id'] != df['vehicle_id'].shift()) | (df['trip_id'] != df['trip_id'].shift())

        # Step 2: Create trip numbers using a cumulative sum
        df['trips'] = changes.cumsum()

        df = df.groupby('trips').filter(lambda group: len(group) > 1)

        all_df.append(df)

        # Step 1: Get the first and last index per trip
        first_last_idx = df.groupby('trips').agg(
            first_idx=('x', lambda x: x.index[0]),
            last_idx=('x', lambda x: x.index[-1])
        )

        # Step 2: Select those rows
        first_rows = df.loc[first_last_idx['first_idx']].copy()
        last_rows = df.loc[first_last_idx['last_idx']].copy()

        # Step 3: Merge origin and destination info into one DataFrame
        first_rows['x1'] = first_rows['x']
        first_rows['y1'] = first_rows['y']
        first_rows['x2'] = last_rows['x'].values
        first_rows['y2'] = last_rows['y'].values
        first_rows['origin_zone'] = first_rows['zone_id']
        first_rows['destination_zone'] = last_rows['zone_id'].values

        # Reset index for cleanliness09_fcd_origin_destination.py
        temp_df = first_rows.copy().reset_index(drop=True)

        df_list.append(temp_df)

    final_df = pd.concat(df_list, ignore_index=True)

    final_all_df = pd.concat(all_df, ignore_index=True)

    final_all_df.drop(columns=['time_diff', 'is_new_trip', 'prev_time', 'trip_id'], inplace=True)

    trip_changes = (final_all_df['trips'] != final_all_df['trips'].shift())

    # Step 2: Create trip numbers using a cumulative sum
    final_all_df['trip_id'] = trip_changes.cumsum()

    final_all_df = final_all_df[[
        'gid', 'x', 'y', 'direction', 'velocity', 'dt', 'status', 'vehicle_id', 'vehicle_class', 'zone_id', 'trip_id', 'fid',
        'ts_insert'
    ]]

    final_df = final_df[[
        'gid', 'direction', 'velocity', 'dt', 'status', 'vehicle_id', 'vehicle_class', 'zone_id', 'fid',
        'trips', 'x1', 'y1', 'x2', 'y2',
        'origin_zone', 'destination_zone'
    ]]

    # Step 1: Detect changes in either vehicle_id or trip_id
    changes = (final_df['trips'] != final_df['trips'].shift())

    # Step 2: Create trip numbers using a cumulative sum
    final_df['trip_id'] = changes.cumsum()

    final_df.drop(columns=['trips'], inplace=True)
    final_df.to_csv(f"data/origin_destination.csv", index=False)

    final_all_df.to_csv(f"data/final_all_df.csv", index=False)
