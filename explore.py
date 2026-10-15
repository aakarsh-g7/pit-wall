import requests
import pandas as pd
import matplotlib.pyplot as plt

# Find the 2024 Bahrain race.
response = requests.get(
    "https://api.openf1.org/v1/sessions",
    params={
        "year": 2024,
        "country_name": "Bahrain",
        "session_name": "Race"
    },
    timeout=30
)

# Stop here if the download failed.
response.raise_for_status()

sessions = response.json()

if not sessions:
    raise SystemExit("No matching race was found.")

# Each session has a unique ID.
session_key = sessions[0]["session_key"]
print("Race ID:", session_key)

# Download Max Verstappen's laps. His driver number was 1.
response = requests.get(
    "https://api.openf1.org/v1/laps",
    params={
        "session_key": session_key,
        "driver_number": 1
    },
    timeout=30
)

response.raise_for_status()

# Turn the downloaded records into a table.
laps = pd.DataFrame(response.json())

if laps.empty:
    raise SystemExit("No lap data was returned.")

# Show the columns we need first.
laps = laps[
    ["driver_number", "lap_number", "lap_duration", "is_pit_out_lap"]
]

laps = laps.sort_values("lap_number")

print(laps.head(10).to_string(index=False))

# Create the chart.
plt.figure(figsize=(10, 5))

# Plot race lap against lap time.
plt.plot(
    laps["lap_number"],
    laps["lap_duration"],
    marker="o",
    markersize=3,
    linewidth=1
)

# Add labels.
plt.title("Verstappen's Lap Times — Bahrain 2024")
plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")

# Make the chart easier to read.
plt.grid(alpha=0.3)
plt.tight_layout()

# Display the chart.
plt.show()