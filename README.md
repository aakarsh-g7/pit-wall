# Pit Wall

Pit Wall explores how tire performance and pit timing affect the race. Built with python and streamlit. Uses historical F1 data with a ML prediction model to compare 2 pit stop decisions. Uses Max Verstappen’s 2024 Bahrain Grand Prix as a case study. Users can adjust replacement-tire pace and slowdown to see when each strategy becomes faster.

## Features

- Compare pitting before lap 31 versus lap 34.
- Adjust tire assumptions and see results update immediately.
- Explore preset scenarios.
- Track the cumulative time gap.
- Inspect the assumptions and lap-by-lap calculations.

## How?

Uses a linear regression model to estimate lap times on existing tires. Assumptions estimate performance after the tire change. The simulator adds a fixed pit stop loss and compares total time over laps 31–40

## Why?

Combining interest in F1 with data science and product thinking. Turned an analysis into an interactive tool that makes a decision and its tradeoffs easier to understand.

## Limitations

Excludes traffic, tire warmup, safety cars, and remaining laps. Results depend on the selected assumptions.

Built using python, streamlit, pandas, matplotlib, openf1 🏎️
