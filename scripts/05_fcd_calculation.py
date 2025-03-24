# Import the necessary libraries and modules
import os
import json
import logging
import numpy as np
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

        # Process each zone separately
        for zone_id in zone_ids:
            query = f"""
                        SELECT dt, {vehicle_id_column}, {velocity_column}, {fid_column}
                        FROM {schema}."{table_name}"
                        WHERE {zone_id_column} = {zone_id} AND {vehicle_class_column} = '{vehicle_type}'
                        order by dt;
                    """

            # Load data for this zone
            df = pd.read_sql(query, engine)

            # Convert 'dt' column to datetime
            df["dt"] = pd.to_datetime(df["dt"])

            # Ensure vehicle_id is treated as a string
            df[vehicle_id_column] = df[vehicle_id_column].astype(str)

            df = df.merge(links[['ID', 'Length']], left_on='fid', right_on='ID', how='left')

            df['interval'] = df['dt'].dt.floor(time_interval)

            avg_speed_df = df.groupby(['interval', fid_column])[velocity_column].mean().reset_index()

            # Rename the velocity column to 'avg_speed' for clarity
            avg_speed_df.rename(columns={velocity_column: 'avg_speed'}, inplace=True)

            # Display the result
            avg_speed_df = avg_speed_df.merge(links[['ID', 'Length']], left_on=fid_column, right_on='ID', how='left')

            avg_speed_df.drop(columns=['ID'], inplace=True)

            weighted_avg_df = (
                avg_speed_df[['interval', 'avg_speed', 'Length']]
                .groupby('interval')
                .apply(lambda group: (group['avg_speed'] * group['Length']).sum() / group['Length'].sum())
                .reset_index(name='fcd_speed')
            )

            unique_vehicle_counts = df.groupby(['interval', 'fid'])['vehicle_id'].nunique().reset_index(
                name='unique_vehicle_count')

            unique_vehicle_counts = unique_vehicle_counts.merge(avg_speed_df, on=['interval', 'fid'], how='left')
            unique_vehicle_counts['Length'] = unique_vehicle_counts['Length'] / 1000

            unique_vehicle_counts['max'] = np.maximum(
                unique_vehicle_counts['unique_vehicle_count'] * unique_vehicle_counts['Length'],
                unique_vehicle_counts['avg_speed'] * (1/12)
            )

            # Using groupby to sum 'max' and 'Length' for each interval
            grouped = unique_vehicle_counts.groupby('interval').agg({'max': 'sum', 'Length': 'sum'}).reset_index()

            # Compute the ratio: sum of 'max' divided by sum of 'Length' for each interval
            grouped['fcd_flow'] = grouped['max'] / (grouped['Length'] * (1/12))

            final_df = grouped.merge(weighted_avg_df, on='interval', how='left')

            final_df['zone_id'] = zone_id

            final_df = final_df[['zone_id', 'interval', 'fcd_speed', 'fcd_flow']]
            final_df['fcd_density'] = final_df['fcd_flow'] / final_df['fcd_speed']

            # Replace inf values with 143
            final_df['fcd_density'].replace([np.inf, -np.inf], 143, inplace=True)

            if not os.path.exists("data/fcd"):
                os.makedirs("data/fcd")

            final_df.to_csv("data/fcd/fcd_" + str(zone_id) + "_" + selected_date + ".csv", index=False)



