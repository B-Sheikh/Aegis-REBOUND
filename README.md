# Aegis REBOUND

**A respiratory digital twin that asks which observation would resolve its uncertainty next.**

Team Aegis — **Abhishek Bharathi and Aadithya Ram** — **Amrita Vishwa Vidyapeetham, Coimbatore**. No incubator affiliation. Built for Digital Twin Challenge 2026.

## The project

An adult with asthma finishes ordinary daily walking, but their respiratory rate remains elevated. Is that an ordinary recovery tail, developing airway deterioration, or a drifting wearable? A conventional risk score can conceal that ambiguity. REBOUND maintains competing virtual explanations and estimates which optional observation would be most informative under a small daily measurement budget.

The working prototype fuses a synthetic historical EHR with an advancing stream of respiratory rate, heart rate, activity, exposure and occasional peak flow. It predicts **three consecutive future five-minute peak-flow values below 80% of personal best within the next 120 minutes**. This is an invented engineering endpoint, includes already-low states, and is **not a clinically adjudicated asthma attack**. The twin also estimates latent recovery debt and sensor bias, displays competing explanations, and can assimilate an additional simulated measurement.

**No deliberate exercise or exposure challenge. No treatment advice. No real-patient use.** Routine activity is observed passively in this synthetic sandbox. The measurement button generates an observation inside the simulator; it does not instruct a real person to perform a test or wait for care.

## Proposed algorithm: RECAP

**Recovery-conditioned Ensemble with Cost-Aware Probing** is a proposed engineering composition implemented here:

1. Use personal EHR baselines and history to condition initial hypotheses and observation models.
2. Maintain nine small state estimators: three explanations × three activity-recovery retention values.
3. Update obstruction proxy, trend, activity-recovery debt and wearable bias using causal Kalman updates. Tempered evidence, forgetting and a small reset mixture allow hypotheses to regain weight.
4. Forecast a mixture of future peak-flow states, holding current exposure constant and assuming no new activity.
5. Estimate the information from a possible peak-flow or independent respiratory-rate measurement with deterministic Gaussian quadrature.
6. Subtract an explicit assumed measurement burden and enforce two optional probes per day, a two-hour cooldown, and a wait option.
7. Assimilate the selected simulated observation and visibly revise the state and hypotheses.

The planner approximates expected information by changing hypothesis weights while holding per-component future risk indices fixed. It does not compute exact full-state clinical value of information. Hypothesis weights are not diagnoses. The latent obstruction proxy and debt half-life are model states, not measured biological quantities.

**Novelty boundary:** Kalman filters, Bayesian hypothesis banks, recovery dynamics, active sensing and expected information gain already exist. Asthma twins and recovery-based warning also have prior art. The contribution proposed here is this specific recovery-conditioned hypothesis bank plus budgeted ambiguity-resolution workflow and its reproducible experiments. A new name does not establish research novelty, patentability, clinical utility or a first-in-the-world invention. See [prior art](docs/PRIOR_ART.md) and [algorithm specification](docs/ALGORITHM.md).

## Run

Requires Python 3.11+ and NumPy. No GPU, paid service, API key, external account or CDN. Calibration artifacts and eight demo streams are bundled. The full synthetic cohort can be regenerated.

**Windows:** double-click `START_WINDOWS.bat`. It creates a local virtual environment and installs NumPy if necessary. The dashboard opens at `http://127.0.0.1:8766`.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Use `python app.py --port 8767` if the default port is occupied. Ctrl+C stops the local server. This standard-library development server is not a production medical server.

## Demonstration

1. Inspect R-065 and the three explanation weights. These are competing models, not established clinical causes.
2. Scrub through the day or play five-minute replay steps. EHR remains fixed; sensor history and estimated state update.
3. Compare **Ordinary activity** and **Ambiguous rise**. The selected scenarios are scripted demonstrations, not representative accuracy samples.
4. Read candidate information gains, assumed burdens and remaining probe budget.
5. When the algorithm selects an optional measurement, click **Simulate…**. The new current-time observation changes the state and hypothesis weights. When the planner chooses wait, the button is disabled.
6. Reveal the withheld future for retrospective comparison. It never feeds the predictor.
7. Click **Sensor gap** to demonstrate abstention. Sensor readings are not backward-filled from future observations.
8. Open **Inside RECAP** for the objective and limitations, and **Experiments** for actual ablations and budget comparisons.
9. Export a synthetic case and the complete experiment JSON.

Moving backward clears optional probes. A snapshot replays the past and any explicitly selected probes at their original timestamps. In the current single-day prototype, at most two additional observations can be used in that replay. The regular four-hourly peak-flow observations are part of every policy’s normal stream.

## Reproduce

```bash
python -m rebound.benchmark
python -m unittest discover -s tests -v
```

The benchmark generates 48 training, 16 calibration and 24 held-out test patients, each with 24 hours at five-minute cadence. Snapshot fusion and wearable/context classifiers fit on training patients. Hand-specified filter models receive only a scalar logistic risk mapping from the calibration patients. Test data never fit a parameter. Every thirty minutes after three hours of history, the benchmark scores a 120-minute future window.

Experiments include a single recovery setting, removal of personal EHR baselines, a snapshot fusion classifier, wearable/context-only classification, an RR threshold, and passive/fixed/adaptive probe policies. Fixed and adaptive policies have the same maximum two optional probes. Fixed probes occur at 09:00 and 17:00, away from regular four-hourly peak-flow timestamps. A paired patient bootstrap assesses adaptive-minus-fixed Brier differences. Another seed and changed simulator settings form a stress test, not external validation.

Canonical measured results: [artifacts/metrics.json](artifacts/metrics.json). Raw passive test predictions: [artifacts/test_predictions.csv](artifacts/test_predictions.csv). The dashboard reads those actual results. Do not advertise an advantage for a component unless the experiment supports it. One simulator family and one primary population seed cannot establish clinical generalization.

## Technical stack

Python, NumPy, standard-library HTTP server; responsive HTML/CSS/JavaScript and local SVG plots. No model API or LLM generates the forecast. All algorithm equations, simulator coefficients, calibration parameters and source are inspectable. Numeric artifacts use JSON, not executable object deserialization.

The synthetic generator is nonlinear and differs from the filter transition equations, but both are authored by this project and share assumptions. Its four concealed scenario families are ordinary recovery, airway deterioration, sensor drift and mixed disturbance. Scenario labels, hidden states and future target arrays are excluded from the inference input. They are used only to score experiments or generate explicitly requested synthetic observations.

## Submission materials

- [15-minute complete project overview](submission/Aegis_REBOUND_15min_Overview.mp4) — requested shorter edition, with [chapter timings](submission/OVERVIEW_15MIN.md).
- [20:30 computer-narrated local walkthrough](submission/Aegis_REBOUND_Demo.mp4) — slides and verified application captures; review before uploading.
- [Start here](START_HERE.md) and [jury questions](submission/JURY_QA.md).

- [Architecture PDF](submission/Architecture.pdf)
- [Project presentation PDF](submission/Project_Presentation.pdf)
- [Technical report](submission/Technical_Report.pdf)
- [Demo narration and recording guide](submission/DEMO_SCRIPT.md)
- [Checklist](submission/SUBMISSION_CHECKLIST.md)
- [Prior-art map](docs/PRIOR_ART.md), [algorithm](docs/ALGORITHM.md), [model/data cards](docs/MODEL_DATA_CARD.md)

**Public GitHub repository:** https://github.com/B-Sheikh/Aegis-REBOUND

**Unlisted YouTube demo:** add the actual reviewed video URL after upload. Any included local walkthrough must be reviewed before submission; a local path is not a reachable YouTube link.

The 15-minute edition provides a complete overview of the problem, RECAP, the working state update, experiments, limitations and reproduction at approximately 150 narrated words per minute. Both editions disclose the computer-generated voice and use recorded application states. The 20:30 edition is retained because the supplied challenge brief also specifies a minimum 20-minute video; use that edition for the stricter requirement.

**Team leader:** designate before registration. The brief requires the registering person to be leader; both members must confirm their details. Submit the leader’s actual name, phone, email and public repository URL on the organizer’s platform. Do not put private contact details in the public README unnecessarily.

## Relationship to previous projects

This replaces the generic glucose direction as the recommended entry. The earlier glucose prototype is a separate baseline artifact, not this submission. Aegis Health inspired the clinician-first interface; Molecular-cell-Simulator inspired inspectable evolving simulation. This is a separate original implementation, preserving the supplied projects. The previous archive’s private reports, billing materials, credentials and 3D assets are not included. No source from the unlicensed molecular repository is redistributed.

## License and limitations

MIT for this new source, synthetic data and original diagrams. The data are entirely invented, are not Synthea/MIMIC/AAMOS records, and do not represent India’s population or any particular device. An adult asthma use case is relevant to the challenge’s chronic-condition scope; the efficacy of these markers and this algorithm has not been shown on Indian patients.

The endpoint is not a validated attack label, probabilities are calibrated only on a toy population, bands are uncalibrated mixture moments, hypotheses may be wrong, and informative measurements may fail to improve prediction. No medication dosing, diagnosis, autonomous treatment, real-patient ingestion or clinical deployment is implemented.
