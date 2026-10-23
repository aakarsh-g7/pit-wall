# Pit Wall

Compare two F1 pit-stop choices: change tires before lap 31 or wait until lap 34. Adjust tire assumptions and see which choice is faster over laps 31–40.

The case study uses Max Verstappen's 2024 Bahrain Grand Prix data from OpenF1. I built the data cleaning, regression analysis, simulation, and Streamlit app.

**Tools:** Python, Streamlit, pandas, Matplotlib, and requests.

## How it works

[explore.py](explore.py) downloads lap times and tire stints. It removes missing times, the opening lap, pit-out laps, and laps just before tire changes.

It fits a straight-line model to the first 12 cleaned laps in the selected hard-tire stint. It tests predictions on the remaining laps against a baseline that always predicts the training median. The script reports mean absolute error for both.

[app.py](app.py) uses the saved model to estimate lap times before the stop. After the stop, it uses your slider settings. Both strategies include one fixed **22-second pit loss**.

## What the sliders mean

| Slider | Range and default | What it changes |
| --- | --- | --- |
| **Starting lap time** | 94–97 seconds; default 95 | First lap time on replacement tires, before adding the pit loss. Lower is faster and favors an earlier stop. |
| **Slowdown per lap** | 0–0.20 seconds; default 0.05 | Time added for each extra lap on the replacement tires. Higher values make older tires slower and favor waiting. |

For example, a starting time of 95 seconds and slowdown of 0.05 give replacement-tire lap times of **95.00, 95.05, 95.10 seconds**, and so on. The pit lap also includes the 22-second loss.

The same slider settings apply to both strategies. The pit laps stay fixed at 31 and 34.

## Reading the results

- **Estimated time:** total time over the ten laps for each strategy. Lower is better.
- **Time difference chart:** lap-34 total minus lap-31 total so far. Above zero favors lap 31; below zero favors lap 34.
- **Chart jumps:** each strategy adds its pit loss on its pit lap.

With the default settings and committed model, pitting on lap 31 takes **974.25 seconds**. Pitting on lap 34 takes **975.33 seconds**. Lap 31 is **1.08 seconds faster** in this simulation.

## Run the app

Install Python, then run these commands from a terminal on macOS or Linux:

```bash
git clone https://github.com/aakarsh-g7/pit-wall.git
cd pit-wall

python3 -m venv .venv
source .venv/bin/activate
python -m pip install streamlit
python -m streamlit run app.py
```

On Windows, create the environment with `py -m venv .venv` and activate it with `.\.venv\Scripts\Activate.ps1` in PowerShell. Then run the same install and launch commands.

Open the local URL printed in the terminal. Press **Ctrl+C** in the terminal to stop the app.

[model_parameters.json](model_parameters.json) is included, so running the app does not require downloading race data.

## Rerun the analysis

From the repository folder, with the environment active:

```bash
python -m pip install requests pandas matplotlib
python explore.py
```

This needs an internet connection. It downloads the OpenF1 data, prints stint summaries and prediction errors, replaces `model_parameters.json`, and opens a plot of lap times by tire stint.

## Limits

This is a ten-lap comparison for one driver and race. Replacement-tire pace, slowdown, and pit loss are assumptions. It excludes traffic, tire warmup, safety cars, and laps after lap 40.
