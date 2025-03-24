import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.cm as cm
import seaborn as sns
import numpy as np

plots_folder = "plots"
if not os.path.exists(plots_folder):
    os.makedirs(plots_folder)
# Load the data from the text file
data = pd.read_csv(r"data/dates.txt", sep="\t", header=None, names=["Date", "Value"])

# Convert date column to datetime format
data["Date"] = pd.to_datetime(data["Date"])

# Extract day names from dates
data["Day"] = data["Date"].dt.day_name()

# Sort data by date
data = data.sort_values(by="Date")

# Get unique days and assign different colors
unique_days = data["Day"].unique()
color_palette = sns.color_palette("husl", len(unique_days))  # Colorful & professional palette
color_map = {day: color for day, color in zip(unique_days, color_palette)}
bar_colors = data["Day"].map(color_map)

# Plot
plt.figure(figsize=(12, 6))
plt.bar(data["Day"], data["Value"], color=bar_colors, edgecolor="black", alpha=0.9)

# Formatting
plt.xlabel("Day of the Week", fontsize=14, fontweight="bold")
plt.ylabel("Value", fontsize=14, fontweight="bold")
plt.title("Bar Chart of Values Over Days", fontsize=16, fontweight="bold", color="darkblue")
plt.xticks(rotation=45, ha="right", fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.5)

# Save plot instead of showing
plt.tight_layout()
plt.savefig(f"{plots_folder}/bar_chart.png", dpi=300, bbox_inches="tight")

# Extract day names and corresponding day numbers
data["Day Name"] = data["Date"].dt.day_name()
data["Day Number"] = data["Date"].dt.day

# Sort data by date
data = data.sort_values(by="Date")

# Combine day number and day name for x-axis labels
data["Day Label"] = data["Day Number"].astype(str) + " - " + data["Day Name"]

# Normalize values for color mapping
norm = plt.Normalize(data["Value"].min(), data["Value"].max())
colors = cm.Reds(norm(data["Value"]))  # Use Reds colormap for dynamic coloring

# Plot
plt.figure(figsize=(15, 7))
plt.bar(data["Day Label"], data["Value"], color=colors, edgecolor="black", alpha=0.9)

# Formatting
plt.xlabel("September 2019", fontsize=14, fontweight="bold")
plt.ylabel("Records", fontsize=14, fontweight="bold")
plt.title("Bar Chart of Records for Each Day in September 2019", fontsize=16, fontweight="bold", color="darkred")
plt.xticks(rotation=90, ha="center", fontsize=12)
plt.yticks(fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.5)

# Show plot
plt.tight_layout()
plt.savefig(f"{plots_folder}/Records_bar_chart_sep_2019.png")

# Data for the pie chart
labels = ['A', 'C']
sizes = [36109191, 13677533]
colors = ['#1f77b4', '#ff7f0e']
explode = (0.1, 0)

# Create the pie chart
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
       colors=colors, explode=explode, shadow=True,
       wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})

# Add a title
ax.set_title("Distribution of Vehicle Classes", fontsize=14, fontweight='bold')

plt.savefig(f"{plots_folder}/vehicle_classes.png", dpi=300, bbox_inches="tight")


# Data for the pie chart
labels = ['1', '2', '0']
sizes = [44264547, 2917733, 2604444]
colors = ['red', 'green', 'blue']

# Create the pie chart
fig, ax = plt.subplots(figsize=(8, 8))
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140,
       colors=colors, shadow=True,
       wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})

# Add a title
ax.set_title("Distribution of Status", fontsize=14, fontweight='bold')

plt.savefig(f"{plots_folder}/status_distribution.png", dpi=300, bbox_inches="tight")

# Data
categories = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '11']
values = [34403827, 11211556, 3746303, 419925, 4571, 277, 250, 6, 7, 2]
x_labels = ['0-42', '43-84', '85-127', '128-169', '170-211', '212-251', '255-267', '304-333', '346-365', '424-424']

# Create the bar chart
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(categories, values, color='#1f77b4', edgecolor='black', linewidth=1.5)

# Add value labels on top of bars
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:,}', ha='center', va='bottom', fontsize=10, rotation=90)

# Formatting the chart
ax.set_xlabel("Velocity (Min - Max)", fontsize=12, fontweight='bold')
ax.set_ylabel("Records", fontsize=12, fontweight='bold')
ax.set_title("Distribution of Velocity in 10 bins", fontsize=14, fontweight='bold')
ax.set_xticks(np.arange(len(categories)))
ax.set_xticklabels(x_labels, rotation=45, ha="right")

# Show gridlines
ax.yaxis.grid(True, linestyle='--', alpha=0.7)

# Display the chart
plt.tight_layout()

plt.savefig(f"{plots_folder}/Velocity_distribution.png", dpi=300, bbox_inches="tight")



