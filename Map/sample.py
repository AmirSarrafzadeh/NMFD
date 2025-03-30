# import json
# import psycopg2
# from psycopg2.extras import execute_values
# from datetime import datetime
#
# # Database connection parameters (update these with your actual credentials)
# DB_NAME = "mmm_map"
# DB_USER = "postgres"
# DB_PASSWORD = "admin"
# DB_HOST = "localhost"
# DB_PORT = "5432"
#
# # Path to the GeoJSON file
# geojson_path = r"C:\Users\asarrafzadeh_wherete\Desktop\MY\Map\data.geojson"
#
# # Connect to PostgreSQL
# conn = psycopg2.connect(
#     dbname=DB_NAME,
#     user=DB_USER,
#     password=DB_PASSWORD,
#     host=DB_HOST,
#     port=DB_PORT
# )
# cursor = conn.cursor()
#
# # Read the GeoJSON file
# with open(geojson_path, "r", encoding="utf-8") as f:
#     geojson_data = json.load(f)
#
#
# corrected_data = {"type": "FeatureCollection"}
#
# for feature in geojson_data["features"]:
#     # Correct the `ts` field to a valid timestamp
#     feature["properties"]["ts"] = datetime.fromtimestamp(feature["properties"]["ts"] / 1000).isoformat()
#     corrected_data["features"].append(feature)
# # Prepare SQL INSERT query for `mmm` table
# insert_query = """
#     INSERT INTO data.data (
#         object_id, uid, x, y, z, ts, platform, trip, model, manufacturer, mode_id,
#         latitude, longitude, altitude, location_ts, location
#     )
#     VALUES %s
# """
#
# values = []
# for feature in geojson_data["features"]:
#     props = feature["properties"]
#     geom = feature["geometry"]["coordinates"]  # Longitude, Latitude from GeoJSON
#
#     # Create a tuple for batch insert
#     values.append((
#         props["OBJECTID"],
#         props["uid"],
#         props["x"],
#         props["y"],
#         props["z"],
#         props["ts"],
#         props["platform"],
#         props["trip"],
#         props["model"],
#         props["manufacturer"],
#         props["mode_id"],
#         props["latitude"],
#         props["longitude"],
#         props["altitude"],
#         props["location_ts"],
#         f"SRID=4326;POINT({geom[0]} {geom[1]})"  # PostGIS geometry format
#     ))
#
# # Bulk insert using `execute_values`
# execute_values(cursor, insert_query, values)
#
# # Commit and close connection
# conn.commit()
# cursor.close()
# conn.close()
#
# print(f"Inserted {len(values)} records successfully into the database.")

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

df = pd.read_csv('_data_.csv')

df["ts"] = df["ts"].str.replace(",", "").astype(int)

# Convert to datetime (milliseconds to timestamp)
df["ts"] = pd.to_datetime(df["ts"], unit="ms")

df = df.sort_values(by="ts", ascending=True)  # Use ascending=False for descending order

# Reset index if needed
df = df.reset_index(drop=True)

# Group by 'trip' and apply cumulative seconds increase
df["ts"] = df.groupby("trip").cumcount().mul(3).apply(pd.Timedelta, unit="s") + df["ts"]

df["location_ts"] = df["location_ts"].str.replace(",", "").astype(int)

# Convert to datetime (milliseconds to timestamp)
df["location_ts"] = pd.to_datetime(df["location_ts"], unit="ms")

# Group by 'trip' and apply cumulative seconds increase
df["location_ts"] = df.groupby("trip").cumcount().mul(3).apply(pd.Timedelta, unit="s") + df["location_ts"]

df.to_csv("new.csv", index=False)
