from pathlib import Path

import streamlit as st

from simulation import compare_strategies, comparison_csv, load_model

st.set_page_config(page_title="Pit Wall", layout="centered")

project_folder = Path(__file__).parent
st.html(f"<style>{(project_folder / 'styles.css').read_text()}</style>")

try:
    model_parameters = load_model()
except (OSError, ValueError, KeyError, TypeError):
    st.error("The saved model is missing or invalid. Run python explore.py to rebuild it.")
    st.stop()


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

    rows = compare_strategies(starting_pace, slowdown, model_parameters)
    final = rows[-1]
    difference = final["gap_s"]

    st.divider()
    st.html(f"""
        <section aria-label="Estimated total time over laps 31 to 40">
            <h2 class="section-title">Estimated time <span>laps 31–40</span></h2>
            <dl class="results">
                <div><dt>Pit on lap 31</dt><dd>{format_time(final['pit_31_total_s'])}</dd></div>
                <div><dt>Pit on lap 34</dt><dd>{format_time(final['pit_34_total_s'])}</dd></div>
            </dl>
        </section>
    """)
    if abs(difference) < 0.005:
        outcome = "Both strategies finish less than 0.005 s apart."
    else:
        quicker_lap = 31 if difference > 0 else 34
        outcome = f"Lap {quicker_lap} is {abs(difference):.2f} s quicker with these assumptions."
    st.html(f'<p class="outcome" role="status">{outcome}</p>')

    st.markdown("### Time difference")
    gap = [0.0] + [row["gap_s"] for row in rows]
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
        "first 12 cleaned laps in the hard-tire stint. Replacement-tire times use your two assumptions."
    )
    st.write(
        "Each strategy changes tires before its chosen lap and adds the same "
        "22-second pit loss once. The chart includes that loss, which causes the "
        "jumps on laps 31 and 34. Totals cover laps 31–40."
    )
    st.write(
        "The fitted trend reflects overall race pace, including fuel load and driving "
        "conditions. It does not measure tire wear on its own. The identical pit losses "
        "cancel in the final comparison once both stops are complete."
    )
    st.caption(
        "Historical data from OpenF1. This educational model excludes traffic, "
        "tire warmup, safety cars, and the remaining race laps."
    )

with st.expander("Lap-by-lap estimates"):
    st.caption("Seconds, including the pit loss on each strategy’s pit lap. Gap = lap 34 total minus lap 31 total.")
    st.dataframe(rows, hide_index=True, column_config={
        "lap": "Lap",
        "pit_31_lap_s": "Lap 31 stop: lap (s)",
        "pit_34_lap_s": "Lap 34 stop: lap (s)",
        "pit_31_total_s": "Lap 31 stop: total (s)",
        "pit_34_total_s": "Lap 34 stop: total (s)",
        "gap_s": "Gap (s)",
    })
    st.download_button(
        "Download estimates (CSV)", comparison_csv(rows),
        file_name="pit-wall-estimates.csv", mime="text/csv",
    )
