import json
import streamlit as st

# Read the model saved by explore.py
with open("model_parameters.json") as file:
    model_parameters = json.load(file)

st.title("Pit Wall")
st.write("Bahrain 2024 · Max Verstappen · End of lap 30")

st.write(
    "Would you change tires before lap 31 or wait until lap 34? "
    "Compare the estimated time over laps 31–40."
)

st.caption(
    "Old-tire pace comes from the historical model. "
    "Replacement-tire performance uses the assumptions below."
)

new_tire_pace = st.slider(
    "Replacement-tire starting lap time (seconds)",
    min_value=94.0,
    max_value=97.0,
    value=95.0,
    step=0.1
)

new_tire_slowdown = st.slider(
    "Additional seconds per lap of replacement-tire use",
    min_value=0.0,
    max_value=0.2,
    value=0.05,
    step=0.01
)

pit_time_loss = 22.0


def simulate_strategy(pit_lap):
    total_time = 0

    for lap in range(31, 41):

        if lap < pit_lap:
            lap_time = (
                model_parameters["intercept"]
                + model_parameters["slope"] * lap
            )

        else:
            laps_since_change = lap - pit_lap

            lap_time = (
                new_tire_pace
                + new_tire_slowdown * laps_since_change
            )

        if lap == pit_lap:
            lap_time = lap_time + pit_time_loss

        total_time = total_time + lap_time

    return total_time


if st.button("Compare strategies"):
    pit_now_time = simulate_strategy(31)
    pit_later_time = simulate_strategy(34)

    left, right = st.columns(2)

    left.metric("Pit before lap 31", f"{pit_now_time:.2f} seconds")
    right.metric("Pit before lap 34", f"{pit_later_time:.2f} seconds")

    difference = pit_later_time - pit_now_time

    if difference > 0:
        st.success(
            f"In this scenario, pitting now is "
            f"{difference:.2f} seconds quicker."
        )
    elif difference < 0:
        st.success(
            f"In this scenario, waiting is "
            f"{abs(difference):.2f} seconds quicker."
        )
    else:
        st.info("Both strategies take the same time.")

st.caption(
    "Both strategies assume one identical 22-second pit loss. "
    "This simplified simulation excludes traffic and tire warmup."
)