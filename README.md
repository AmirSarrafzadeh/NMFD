# Welcome to My FCD Repository
<img src="https://c.pxhere.com/photos/f1/94/aerial_architecture_buildings_cars_city_cityscape_crossroads_downtown-1523341.jpg!d" alt="Photo">

# FCD Project
This repository contains a comprehensive pipeline for processing, analyzing, and visualizing vehicle traffic data, focusing on vehicle positions, speeds, and flow characteristics over time and across spatial zones. The project is organized in modular scripts that read, transform, analyze, and visualize the data collected from traffic monitoring systems.

## 🧠 Functionality Overview

### 1. `01_read_and_insert_data_into_database.py`
Reads vehicle trajectory data from a CSV file in chunks and inserts it into a PostgreSQL database.  
Configurations like database credentials and file paths are handled via `config.json`.

---

### 2. `02_unique_vehicle_id_time_intervals.py`
Generates time-series data (e.g., every 5 minutes) for each traffic zone to calculate:
- Unique vehicle counts  
- Mean speeds  
- Density and flow metrics  

---

### 3. `03_data_visualization.py`
Creates various visualizations including:
- 📊 Daily record distribution  
- 🚗 Vehicle class distribution  
- ⚙️ Status distribution  
- 🌀 Velocity binning  

---

### 4. `04_extract_links_id.py`
Parses a GeoJSON road network file (`grafo.json`) and extracts essential link attributes such as:
- `fid_12`
- `meters`  
Results are saved to a CSV file.

---

### 5. `05_fcd_calculation.py`
Computes traffic metrics using Floating Car Data (FCD), including:
- Average speed
- Flow
- Density  
Results are saved in zone-wise CSV files inside the `data/fcd` directory.

---

### 6. `06_fcd_visualization.py`
Generates scatter plots for each zone:
- 📈 Flow vs. Density  
- 📈 Flow vs. Speed  
- 📈 Speed vs. Density  
Each with fitted trend lines (polynomial or linear).

---

### 7. `07_fcd_dense_links.py`
Identifies the **top 5 most congested links** (by frequency) for each zone and each day.  
Results are stored in `data/dense_links.csv`.

---

### 8. `08_fcd_dense_zones.py`
Detects the **most congested zones per day** based on vehicle presence.  
Results are stored in `data/dense_zones.csv`.

---

### 9. `09_fcd_origin_destination.py`
Extracts detailed trip-level information by analyzing vehicle movement:
- Origin and destination zones  
- Coordinates of start and end  
- Trip segmentation based on time gaps  

Outputs:
- `data/origin_destination.csv`
- `data/final_all_df.csv`

---

### 10. `10_fcd_origin_destination_matrix_visualization.py`
Creates insightful visualizations including:
- 📊 Bar chart of top 10 most crowded zones (sum of in/out trips)  
- 🔥 Heatmap of OD matrix for the top 10 zones  

All plots are saved in the `plots/` directory.


## ✨ Features

- ✅ **Read large CSV files in chunks** for efficient memory usage and processing.
- 🧹 **Cleans and formats raw data** before inserting into the database.
- 🛠️ **Uses `psycopg2`** for efficient PostgreSQL database operations.
- 📜 **Logs all operations** for easy debugging and monitoring (saved in the `logs/` directory).


## 🛠️ Requirements

Ensure you have the following dependencies installed:

```
greenlet==3.1.1  
numpy==2.2.3  
pandas==2.2.3  
psycopg2==2.9.10  
python-dateutil==2.9.0.post0  
pytz==2025.1  
six==1.17.0  
SQLAlchemy==2.0.38  
typing_extensions==4.12.2  
tzdata==2025.1
```

You can install them using:

```bash
pip install -r requirements.txt
```
> *(Make sure to create a `requirements.txt` file with the above contents if you haven't already.)*

## 📁 Project Structure

```
.
├── data/             # Contains input/output CSVs and raw data files
├── logs/             # Log files generated during processing
├── notes/            # Documentation, observations, or project notes
├── plots/            # Output charts and visualizations
├── scripts/          # Python scripts for data processing and analysis
├── .gitignore        # Git ignored files and directories
├── README.md         # Project overview and documentation
└── requirements.txt  # Python dependencies
```

## Configuration
Create a config.json file in the root directory with the following structure:

```
{
  "input_data": {
    "data_name": "fcdmm201909.csv",
    "chunk_size": 10000000,
    "zone_filename": "zone_data.csv",
    "zone_column": "Zone ID"
  },
  "database": {
    "dbname": "NMFD",
    "schema": "data",
    "table_name": "data_2019_09",
    "user": "postgres",
    "password": "admin",
    "host": "localhost",
    "port": 5432
  },
  "operation": {
    "time_interval": "5min",
    "dt_column": "datetime",
    "vehicle_id_column": "vehicle_id",
    "zone_id_column": "zone_id",
    "fid_column": "fid",
    "vehicle_class_column": "vehicle_class",
    "vehicle_type": "A",
    "velocity_column": "velocity"
  },
  "output_data": {
    "output_filename": "vehicles"
  }
}
```

## Usage
Place all your CSV files inside the data/ directory.

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

### 👨‍💻 Developed By Amir
