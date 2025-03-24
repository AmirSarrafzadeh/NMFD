# Import the necessary libraries and modules
import os
import json
import logging
import pandas as pd
from sqlalchemy import create_engine

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
    zones = pd.read_csv(data_path)
    zone_ids = zones[zone_column].tolist()

    # Create SQLAlchemy engine
    engine = create_engine(
        f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}")

    for i in range(1, 31):
        # Set the full 5-minute bins for a 24-hour period
        table_name = config["database"]["table_name"]
        selected_date = "-".join(table_name.split("_")[1:])
        if i < 10:
            selected_date = f"{selected_date}-0{i}"
            table_name = f"{table_name}_0{i}"
        else:
            selected_date = f"{selected_date}-{i}"
            table_name = f"{table_name}_{i}"

        full_time_range = pd.date_range(start=f"{selected_date} 00:00:00", end=f"{selected_date} 23:55:00", freq=time_interval)
        final_df = pd.DataFrame({"dt": full_time_range})

        # Create a dictionary to store DataFrames for each zone before merging
        zone_dfs = []

        # Process each zone separately
        for zone_id in zone_ids:
            query = f"""
                SELECT dt, {vehicle_id_column}, {velocity_column}
                FROM {schema}."{table_name}"
                WHERE {zone_id_column} = {zone_id} AND {vehicle_class_column} = '{vehicle_type}';
            """

            # Load data for this zone
            df = pd.read_sql(query, engine)

            # Convert 'dt' column to datetime
            df["dt"] = pd.to_datetime(df["dt"])

            # Ensure vehicle_id is treated as a string
            df[vehicle_id_column] = df[vehicle_id_column].astype(str)

            # Compute vehicle count, IDs, and mean speed per 5-minute bin
            grouped = df.groupby(pd.Grouper(key="dt", freq=time_interval)).agg(
                vehicle_numbers=(vehicle_id_column, "nunique"),
                mean_speed=(velocity_column, "mean")
            ).reset_index()

            # Merge with full time bins to ensure all 288 rows exist
            grouped = full_time_range.to_frame(name="dt").merge(grouped, on="dt", how="left").fillna(
                {"vehicle_numbers": 0, "mean_speed": 0})

            # Convert vehicle_numbers to integer
            grouped["vehicle_numbers"] = grouped["vehicle_numbers"].astype(int)

            # Rename columns dynamically
            grouped = grouped.rename(columns={
                "vehicle_numbers": f"V_{zone_id}",
                "mean_speed": f"MS_{zone_id}"
            })

            length_list = float(zones[zones['Zone ID'] == zone_id]['Length(Sum)'].values[0])
            grouped['Length'] = length_list
            grouped[f"V_{zone_id}"] = grouped[f"V_{zone_id}"] * 20
            grouped[f'Density_{zone_id}'] = grouped[f"V_{zone_id}"] / grouped['Length']
            grouped[f'Flow_{zone_id}'] = grouped[f"MS_{zone_id}"] * grouped[f'Density_{zone_id}']

            grouped = grouped.drop(columns=["dt"])
            # Store the processed DataFrame for later concatenation
            zone_dfs.append(grouped)

        # Merge all zone data into final_df efficiently
        final_df = pd.concat([final_df] + zone_dfs, axis=1)

        # Save the final DataFrame
        selected_date_output_filename = f"{selected_date}_{output_filename}.csv"
        output_file_path = os.path.join("data", selected_date_output_filename)
        final_df.to_csv(output_file_path, index=False)

        logging.info(f"CSV file '{output_filename}' has been created with {len(final_df)} rows, including mean speed values.")
