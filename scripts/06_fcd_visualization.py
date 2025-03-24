import os
import json
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

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

    data_path = os.path.join("data", zone_filename)
    links = pd.read_csv(os.path.join("data", "links.csv"))
    zones = pd.read_csv(data_path)
    zone_ids = zones[zone_column].tolist()

    for zone in zone_ids:
        fcd_list = []
        for root, dirs, files in os.walk("data/fcd"):
            for file in files:
                if file.startswith(f"fcd_{zone}_"):
                    fcd = pd.read_csv(os.path.join(root, file))
                    fcd = fcd[fcd['fcd_density'] <= 150]
                    fcd = fcd[fcd['fcd_flow'] <= 3600]
                    fcd_list.append(fcd)

        fcd_data = pd.concat(fcd_list)

        # Scatter plot of flow vs. density
        plt.figure(figsize=(14, 9))
        sns.scatterplot(data=fcd_data, x='fcd_density', y='fcd_flow', alpha=0.6)

        # Fit a polynomial (e.g., degree 2 or 3)
        degree = 2  # or try 3 for more curvature
        x = fcd_data['fcd_density']
        y = fcd_data['fcd_flow']
        coeffs = np.polyfit(x, y, degree)
        poly_eq = np.poly1d(coeffs)

        # Generate x values and compute predicted y values
        x_vals = np.linspace(x.min(), x.max(), 500)
        y_vals = poly_eq(x_vals)

        # Plot the polynomial trend line
        plt.plot(x_vals, y_vals, color='orange', linewidth=2, label='Polynomial Trend (Degree 2)')

        # Title and labels
        plt.title('Flow-Density Diagram for Zone ' + str(zone))
        plt.xlabel('Density (veh/km)')
        plt.ylabel('Flow (veh/hour)')
        plt.grid(True)
        plt.legend()

        # Save the plot
        if not os.path.exists("plots/fcd/flow_density"):
            os.makedirs("plots/fcd/flow_density")

        plt.tight_layout()
        plt.savefig(f"plots/fcd/flow_density/Zone_{zone}.png")
        # plt.show()

        # Scatter plot of speed vs. flow
        plt.figure(figsize=(14, 9))
        sns.scatterplot(data=fcd_data, x='fcd_flow', y='fcd_speed', alpha=0.6)

        # Title and labels
        plt.title('Flow-Speed Diagram for Zone ' + str(zone))
        plt.xlabel('Flow (veh/hour)')
        plt.ylabel('Speed (km/h)')
        plt.grid(True)
        plt.legend()

        # Save the plot
        if not os.path.exists("plots/fcd/flow_speed"):
            os.makedirs("plots/fcd/flow_speed")

        plt.tight_layout()
        plt.savefig(f"plots/fcd/flow_speed/Zone_{zone}.png")
        # plt.show()

        logging.info("Flow-Density and Flow-Speed plots generated successfully.")

        # Scatter plot of speed vs. density
        plt.figure(figsize=(14, 9))

        sns.scatterplot(data=fcd_data, x='fcd_density', y='fcd_speed', alpha=0.6)

        # Fit a linear regression model
        x = fcd_data['fcd_density']
        y = fcd_data['fcd_speed']

        coeffs = np.polyfit(x, y, 1)
        poly_eq = np.poly1d(coeffs)

        # Generate x values and compute predicted y values
        x_vals = np.linspace(x.min(), x.max(), 500)
        y_vals = poly_eq(x_vals)

        # Plot the linear trend line
        plt.plot(x_vals, y_vals, color='red', linewidth=2, label='Linear Trend')

        # Title and labels
        plt.title('Density-Speed Diagram for Zone ' + str(zone))
        plt.xlabel('Density (veh/km)')
        plt.ylabel('Speed (km/h)')
        plt.grid(True)
        plt.legend()

        # Save the plot
        if not os.path.exists("plots/fcd/density_speed"):
            os.makedirs("plots/fcd/density_speed")

        plt.tight_layout()
        plt.savefig(f"plots/fcd/density_speed/Zone_{zone}.png")