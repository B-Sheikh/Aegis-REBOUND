# Evaluate Aegis REBOUND

## Launch

**Hosted dashboard:** https://aegis-rebound.onrender.com/ . On the free hosting plan, the first visit after inactivity may take about a minute to load.

For a local installation:

1. On Windows, double-click `START_WINDOWS.bat`. Python 3.11+ is required. The first launch installs NumPy into a local environment; subsequent runs work offline.
2. Open the printed address, normally `http://127.0.0.1:8766`. Other platforms can use the installation commands in [README.md](README.md).

## Five-minute product tour

1. Start with **R-065 at 10:00**. Inspect the personal EHR, observed respiratory trace, competing hypotheses and next-observation scores.
2. Click **Simulate peak flow**. Airway weight changes from 81.2% to 97.1%; the event estimate changes from 70.3% to 75.6%. The budget drops to one remaining observation and cooldown makes the next action wait.
3. Move the replay timeline forward. The observed prefix, filter states and forecast update. Moving backward clears optional measurements.
4. Select **Ordinary activity** and **Ambiguous rise** to compare different evidence patterns. The measurement choice and hypothesis weights depend on the case.
5. Toggle **Reveal withheld future** for retrospective forecast inspection. The overlay does not feed inference.
6. Select **Sensor gap**. The app withholds inference because the input freshness/completeness requirements are not met.
7. Open **Inside RECAP** for the algorithm and **Experiments** for ablations, measurement-policy comparisons and the shifted-cohort test. Export a case or the complete experiment JSON.

All observations in this tour are synthetic. Hypothesis weights are model explanations rather than clinical diagnoses.

## Submission materials

- [Watch the complete demonstration on YouTube](https://youtu.be/ILm7Eiy5NiM) — silent uploaded edition.

- [20:30 project walkthrough](submission/Aegis_REBOUND_Demo.mp4) — complete narrated presentation and prototype overview.
- [15:00 silent product demo](submission/Aegis_REBOUND_15min_Overview.mp4) — captioned interaction sequences, edited and paced for reading.
- [Project presentation](submission/Project_Presentation.pdf), [architecture](submission/Architecture.pdf), and [technical report](submission/Technical_Report.pdf).
- [Deliverables index](submission/DELIVERABLES.md), [algorithm](docs/ALGORITHM.md), and [measured results](docs/RESULTS.md).
