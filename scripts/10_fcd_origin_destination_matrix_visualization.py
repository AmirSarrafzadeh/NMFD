# Import the necessary libraries and modules
import os
import json
import logging
import pandas as pd
import matplotlib.pyplot as plt
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

    # Read the origin-destination matrix data
    df = pd.read_csv(f"data/origin_destination.csv")
    all_df = pd.read_csv(f"data/final_all_df.csv")

    # Create OD matrix
    od_matrix = df.groupby(['origin_zone', 'destination_zone']).size().unstack(fill_value=0)

    od_matrix = od_matrix.loc[(od_matrix != 0).any(axis=1), (od_matrix != 0).any(axis=0)]

    # Sum of incoming and outgoing trips per zone
    incoming = od_matrix.sum(axis=0)  # Destination
    outgoing = od_matrix.sum(axis=1)  # Origin

    # Total trips per zone
    total_trips = incoming.add(outgoing, fill_value=0)

    # Get top 10 most crowded zones
    top_10_zones = total_trips.sort_values(ascending=False).head(10)

    # Plot
    plt.figure(figsize=(10, 6))
    top_10_zones.plot(kind='barh', color='teal')
    plt.gca().invert_yaxis()  # Most crowded on top
    plt.xlabel('Number of Trips')
    plt.title('Top 10 Most Crowded Zones (In + Out)')
    plt.tight_layout()
    plt.grid(axis='x')
    plt.savefig('plots/top_10_most_crowded_zones.png')
    # plt.show()

    # Reuse the top 10 most crowded zones (from previous step)
    top_10_zone_ids = top_10_zones.index

    # Filter OD matrix for top 10 zones only
    od_top10 = od_matrix.loc[top_10_zone_ids, top_10_zone_ids]

    # Plot
    plt.figure(figsize=(8, 6))
    plt.imshow(od_top10, cmap='plasma', interpolation='nearest')
    plt.title('OD Matrix for Top 10 Most Crowded Zones')
    plt.xlabel('Destination Zone')
    plt.ylabel('Origin Zone')
    plt.colorbar(label='Number of Trips')
    plt.xticks(ticks=range(len(od_top10.columns)), labels=od_top10.columns, rotation=90)
    plt.yticks(ticks=range(len(od_top10.index)), labels=od_top10.index)
    plt.tight_layout()
    plt.grid(False)
    plt.savefig('plots/od_matrix_top_10_zones.png')
    # plt.show()

