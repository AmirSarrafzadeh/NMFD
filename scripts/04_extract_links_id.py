data_path = r"C:\AMIR\Python\NMFD\data\grafo.json"


import json
import pandas as pd

# Load the GeoJSON data from a file or string
with open(data_path, "r", encoding="utf-8") as file:
    geojson_data = json.load(file)

# Extract required fields
extracted_data = [
    {"fid_12": feature["properties"]["fid_12"], "meters": feature["properties"]["meters"]}
    for feature in geojson_data["features"]
]

# Convert to DataFrame
df = pd.DataFrame(extracted_data)

# Save to CSV
csv_filename = "extracted_data.csv"
df.to_csv(csv_filename, index=False)

print(f"CSV file saved as {csv_filename}")
