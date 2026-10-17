import requests
import pandas as pd
import matplotlib.pyplot as plt
from statistics import linear_regression
import json

# 2024 Bahrain race data from openF1
response = requests.get(
    "https://api.openf1.org/v1/sessions",
    params={
        "year": 2024,
        "country_name": "Bahrain",
        "session_name": "Race"
    },
    timeout=30
)

# If download fails
response.raise_for_status()

sessions = response.json()

if not sessions:
    raise SystemExit("No matching race was found.")

# Session's unique ID
session_key = sessions[0]["session_key"]
print("Race ID:", session_key)

# Max Verstappen's laps (driver 1)
response = requests.get(
    "https://api.openf1.org/v1/laps",
    params={"session_key": session_key, "driver_number": 1},
    timeout=30
)

response.raise_for_status()

# Turn downloaded records into a table
laps = pd.DataFrame(response.json())

if laps.empty:
    raise SystemExit("No lap data was returned.")

# Keep columns we need
laps = laps[["driver_number", "lap_number", "lap_duration", "is_pit_out_lap"]]

laps = laps.sort_values("lap_number")

print(laps.head(10).to_string(index=False))

# Download Verstappen's tire stints
response = requests.get(
    "https://api.openf1.org/v1/stints",
    params={"session_key": session_key, "driver_number": 1},
    timeout=30
)

response.raise_for_status()

# Turn stint records into a table
stints = pd.DataFrame(response.json())

# Keep columns needed
stints = stints[["stint_number", "lap_start", "lap_end", "compound", "tyre_age_at_start"]]
stints = stints.sort_values("stint_number")

print("\nTire stints:")
print(stints.to_string(index=False))

# Laps with a recorded time
clean_laps = laps.dropna(subset=["lap_duration"]).copy()

# Remove opening lap because it includes the race start
clean_laps = clean_laps[clean_laps["lap_number"] > 1]

# Remove laps where driver exited pits
clean_laps = clean_laps[clean_laps["is_pit_out_lap"] == False]

# Exclude the last lap before each tire change
# Final stint ends at the finish, leave that one alone
for lap_number in stints["lap_end"].iloc[:-1]:
    clean_laps = clean_laps[clean_laps["lap_number"] != lap_number]

# Build one summary row for each stint
summary_rows = []

for index, stint in stints.iterrows():

    stint_laps = clean_laps[
        (clean_laps["lap_number"] >= stint["lap_start"])
        & (clean_laps["lap_number"] <= stint["lap_end"])
    ]

    summary_rows.append({
        "Stint": int(stint["stint_number"]),
        "Tire": stint["compound"],
        "Laps analyzed": len(stint_laps),
        "Median time (s)": stint_laps["lap_duration"].median(),
        "Standard deviation (s)": stint_laps["lap_duration"].std()
    })

# Convert our list of summary rows into a table.
summary = pd.DataFrame(summary_rows)

print("\nStint comparison:")
print(summary.round(3).to_string(index=False))

# Select the cleaned laps from the hard-tire stint
hard_laps = clean_laps[
    (clean_laps["lap_number"] >= 18)
    & (clean_laps["lap_number"] <= 37)
].sort_values("lap_number")

# Learn from first 12 laps. Test on remaining laps
train = hard_laps.iloc[:12]
test = hard_laps.iloc[12:]

# Fit a straight line
# Predicted lap time = intercept + slope * lap number
model = linear_regression(
    train["lap_number"].tolist(),
    train["lap_duration"].tolist()
)

# Save model for app.py
# Two numbers define the regression line
with open("model_parameters.json", "w") as file:
    json.dump({
        "slope": float(model.slope),
        "intercept": float(model.intercept)
    }, file, indent=2)

print("\nSaved model_parameters.json for the Streamlit app.")

# Make predictions for the test laps
results = test[["lap_number", "lap_duration"]].copy()

results["prediction"] = (
    model.intercept + model.slope * results["lap_number"]
)

# Baseline predicts the training median for every test lap
results["baseline"] = train["lap_duration"].median()

# Calculate mean absolute error: average miss size
model_mae = (results["lap_duration"] - results["prediction"]).abs().mean()

baseline_mae = (results["lap_duration"] - results["baseline"]).abs().mean()

print("\nPrediction results:")
print(results.round(3).to_string(index=False))

print(f"\nTrend model MAE: {model_mae:.3f} seconds")
print(f"Median baseline MAE: {baseline_mae:.3f} seconds")

# Example assumptions, not measured Bahrain values
new_tire_pace = 95.0       # First lap on replacement tires (seconds)
new_tire_slowdown = 0.05   # Additional seconds per lap of tire use
pit_time_loss = 22.0       # Total extra time lost through pit lane


def simulate_strategy(pit_lap):
    total_time = 0

    # Simulate laps 31 through 40
    for lap in range(31, 41):

        if lap < pit_lap:
            # Continue on old tires using existing model
            lap_time = model.intercept + model.slope * lap

        else:
            # Replacement tires get older with each lap
            laps_since_change = lap - pit_lap

            lap_time = (
                new_tire_pace
                + new_tire_slowdown * laps_since_change
            )

        # Add pit loss once, when tires are changed
        if lap == pit_lap:
            lap_time = lap_time + pit_time_loss

        total_time = total_time + lap_time

    return total_time


# Compare two choices
pit_now_time = simulate_strategy(31)
pit_later_time = simulate_strategy(34)

print("\nStrategy simulation — laps 31–40:")
print(f"Pit now:   {pit_now_time:.3f} seconds")
print(f"Pit later: {pit_later_time:.3f} seconds")

difference = pit_later_time - pit_now_time

if difference > 0:
    print(f"Pitting now is quicker by {difference:.3f} seconds.")
elif difference < 0:
    print(f"Pitting later is quicker by {abs(difference):.3f} seconds.")
else:
    print("Both strategies take the same time.")

# Color for each tire compound
colors = {
    "SOFT": "red",
    "MEDIUM": "gold",
    "HARD": "gray"
}

plt.figure(figsize=(10, 5))

# Go through stint table one row at a time
for index, stint in stints.iterrows():

    # Select laps belonging to this stint
    stint_laps = clean_laps[
        (clean_laps["lap_number"] >= stint["lap_start"])
        & (clean_laps["lap_number"] <= stint["lap_end"])
    ]

    # Plot this stint as its own line
    plt.plot(
        stint_laps["lap_number"],
        stint_laps["lap_duration"],
        color=colors[stint["compound"]],
        marker="o",
        markersize=3,
        label=f"Stint {stint['stint_number']}: {stint['compound']}"
    )

plt.title("Verstappen's Race Pace by Tire Stint — Bahrain 2024")
plt.xlabel("Lap Number")
plt.ylabel("Lap Time (seconds)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()