# Recruiter-readiness audit

Reviewed 24 October 2026 against main commit `31f4ad9cc4cdc3dca6ddb9b7c7df9801cf56b632`.

The README already explained the decision, slider meanings, default result, and core limitations. The largest gaps were reproducibility, inspectable evidence, and clear model boundaries.

| Priority | Finding | Change in this PR |
| --- | --- | --- |
| High | Setup installed packages individually, without versions or a Python requirement. | Added pinned direct dependencies, Python 3.11+ guidance, and complete macOS/Linux and Windows commands. |
| High | No saved chart or calculation table was visible in the repository. | Added a reproducible default chart and CSV derived from the existing coefficients; linked both near the top of the README. |
| High | App and analysis duplicated the strategy calculation. | Moved it to simulation.py and used it in the app, analysis, and export script. |
| High | Analysis only printed evaluation metrics and opened a chart. The committed coefficients had no saved source or test evidence. | Future runs save downloaded tables, cleaned data, predictions, split details, coefficients, both MAEs, and a chart. No historical MAE is added without rerunning the source data. |
| High | A fitted lap-time trend could be mistaken for isolated tire degradation or a validated optimal strategy. | Explained fuel and race-condition confounding, assumed replacement-tire pace, the small same-stint test set, and the fixed horizon. |
| Medium | Hard-tire lap bounds were hardcoded. | Select the first hard stint from source metadata; stop if there are too few laps to train and test. |
| Medium | The UI had no inspectable calculation output. | Added an expandable table and CSV download while preserving the two-slider main view. |
| Medium | check_connection.py used an unrelated FastF1 dependency. | Changed it to check the same OpenF1 source as the analysis. |
| Medium | No calculation or UI regression checks. | Added standard-library tests and Streamlit AppTest coverage, with a GitHub Actions workflow. |

## Verified evidence

The existing coefficients are slope 0.049479020979021515 and intercept 94.17568065268064. With 95 s starting pace, 0.05 s slowdown, and one 22 s pit loss, the shared calculation produces 974.250000 s for lap 31 and 975.327028 s for lap 34. The difference is 1.077028 s.

The saved chart was rendered and visually inspected. Five calculation checks passed locally on Python 3.14.7. Local Streamlit execution and a fresh OpenF1 download could not be completed: Streamlit and requests were absent, and the shell could not reach external hosts. The GitHub workflow is intended to verify dependency installation and the real Streamlit app on Python 3.12 and 3.14. Check its results on this PR before merging.

## Highest-value remaining work

1. **Save one complete real-data evaluation.** Run explore.py with OpenF1 access and review the source tables, train/test laps, coefficients, and predictions. Commit an appropriately attributed snapshot and its evaluation together. The current default example only verifies the simulation using the committed coefficients.
2. **Add a live demo and actual UI screenshot.** The repository has no homepage URL. A recruiter can now inspect a chart immediately, but still needs a local installation to interact. Do not label the generated simulation chart as a screenshot.
3. **Test generalization before making stronger modeling claims.** Evaluate across more races and drivers with chronological splits. Address fuel effects and quantify uncertainty. The current same-stint holdout does not support a broad forecast-accuracy claim.
4. **Make GitHub's About section specific.** The current description is “ML prediction model and simulation on Max Verstappen’s 2024 Bahrain Grand Prix” and there are no topics. Suggested description: “F1 pit-stop simulator with a linear pace model, baseline evaluation, and Streamlit UI.” Suggested topics: python, streamlit, simulation, formula-1, linear-regression. Repository metadata was not changed in this PR.

For quant and fintech applications, present this as evidence of chronological evaluation, baseline comparison, sensitivity analysis, and a usable decision interface. The repository contains no financial model, trading strategy, or financial performance evidence.
