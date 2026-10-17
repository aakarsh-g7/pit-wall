# Pit Wall
### An interactive F1 pit stop strategy simulator

**Pit now or stay out?** Pit Wall explores how tire performance and pit timing affect race strategy. Built with Python and Streamlit, it combines historical Formula 1 lap data with a simple prediction model to compare two pit stop decisions.

The project uses Max Verstappen’s 2024 Bahrain Grand Prix as a case study. Users can adjust replacement-tire pace and slowdown to see when each strategy becomes faster.

## Features

- Compare pitting before lap 31 versus lap 34.
- Adjust tire assumptions and see results update immediately.
- Explore preset scenarios.
- Track the cumulative time gap between strategies.
- Inspect the assumptions and lap-by-lap calculations.

## How it works

A simple linear regression estimates lap times on the existing tires. User-defined assumptions estimate performance after the tire change. The simulator adds a fixed pit stop loss and compares total time over laps 31–40.

## Why I built it

I wanted to combine my interest in F1 with data science and product thinking: turning an analysis into an interactive tool that makes a decision and its tradeoffs easier to understand.

## Limitations

This is an educational simulation. It excludes traffic, tire warmup, safety cars, and the remaining race laps. Results depend on the selected assumptions.

**Built with:** Python · Streamlit · pandas · Matplotlib · OpenF1
