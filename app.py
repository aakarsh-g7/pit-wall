import json
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="Pit Wall", layout="centered")

project_folder = Path(__file__).parent
st.html(f"<style>{(project_folder / 'styles.css').read_text()}</style>")

model_path = project_folder / "model_parameters.json"
if not model_path.exists():
    st.error("Run explore.py to create model_parameters.json, then reload this page.")
    st.stop()

with model_path.open() as file:
    model_parameters = json.load(file)

PIT_LOSS = 22.0


def simulate_strategy(pit_lap, starting_pace, slowdown):
    """Keep a running total using the original simulation calculation."""
    total_time = 0.0
    totals = []
    for lap in range(31, 41):
        if lap < pit_lap:
            lap_time = model_parameters["intercept"] + model_parameters["slope"] * lap
        else:
            lap_time = starting_pace + slowdown * (lap - pit_lap)
        if lap == pit_lap:
            lap_time = lap_time + PIT_LOSS
        total_time = total_time + lap_time
        totals.append(total_time)
    return totals


def format_time(seconds):
    """Display elapsed time as minutes:seconds, rounded to two decimals."""
    hundredths = round(seconds * 100)
    minutes, remaining = divmod(hundredths, 6000)
    return f"{minutes}:{remaining / 100:05.2f}"


st.html("""
    <header class="page-heading">
        <h1>Pit Wall</h1>
        <p>Bahrain 2024 · Max Verstappen</p>
    </header>
""")
st.write("Pit before lap 31 or wait until lap 34? Compare the next ten laps.")

with st.container(key="simulation", border=True):
    st.markdown("### Replacement tires")
    pace_column, slowdown_column = st.columns(2, gap="large")
    starting_pace = pace_column.slider(
        "Starting lap time", min_value=94.0, max_value=97.0,
        value=95.0, step=0.1, format="%.2f s", key="pace",
        help="Assumed lap time on the new tires. Lower is faster.",
    )
    slowdown = slowdown_column.slider(
        "Slowdown per lap", min_value=0.0, max_value=0.2,
        value=0.05, step=0.01, format="%.2f s", key="slowdown",
        help="Time added with each lap of tire use. At 0.05 s, the next lap is 0.05 seconds slower.",
    )

    pit_now = simulate_strategy(31, starting_pace, slowdown)
    pit_later = simulate_strategy(34, starting_pace, slowdown)
    difference = pit_later[-1] - pit_now[-1]

    st.divider()
    st.html(f"""
        <section aria-label="Estimated total time over laps 31 to 40">
            <h2 class="section-title">Estimated time <span>laps 31–40</span></h2>
            <dl class="results">
                <div><dt>Pit on lap 31</dt><dd>{format_time(pit_now[-1])}</dd></div>
                <div><dt>Pit on lap 34</dt><dd>{format_time(pit_later[-1])}</dd></div>
            </dl>
        </section>
    """)
    if abs(difference) < 0.005:
        outcome = "Both strategies finish within 0.01 s."
    else:
        quicker_lap = 31 if difference > 0 else 34
        outcome = f"Lap {quicker_lap} is {abs(difference):.2f} s quicker with these assumptions."
    st.html(f'<p class="outcome" role="status">{outcome}</p>')

    st.markdown("### Time difference")
    gap = [0.0] + [later - now for now, later in zip(pit_now, pit_later)]
    st.line_chart(
        {"Lap": list(range(30, 41)), "Gap": gap},
        x="Lap", y="Gap", x_label="Lap", y_label="Gap (s)",
        color="#0071e3", height=210, width="stretch",
        alt="Cumulative time gap. Positive values favor lap 31; negative values favor lap 34.",
    )
    st.caption("Above zero: lap 31 ahead. Below zero: lap 34 ahead.")

with st.expander("How it works"):
    st.write(
        "Old-tire lap times follow a straight-line trend fitted to Verstappen’s "
        "cleaned hard-tire laps 19–30. Replacement-tire times use your two assumptions."
    )
    st.write(
        "Each strategy changes tires before its chosen lap and adds the same "
        "22-second pit loss once. The chart includes that loss, which causes the "
        "jumps on laps 31 and 34. Totals cover laps 31–40."
    )
    st.caption(
        "Historical data from OpenF1. This educational model excludes traffic, "
        "tire warmup, safety cars, and the remaining race laps."
    )
