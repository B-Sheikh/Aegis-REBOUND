# Model and data card

## Intended use

Local competition research demo for adult asthma monitoring. No clinical validation, patient-care use, diagnosis, treatment recommendation, exposure challenge, deliberate exertion, or emergency assessment. The measurement controls reveal synthetic observations only.

## Data

`rebound/data.py` generates one day of five-minute samples per patient. Seed 71 is used for the primary 88-patient study, split 48/16/24. Twelve additional patients use seed 93 and changed parameters for a stress test. Eight held-out public demo streams are bundled; all other records are reproducible from the generator. These are not real EHRs or wearable records and are not Synthea, MIMIC or AAMOS data. No actual patient files are included.

EHR fields include age, asthma duration, prior attack count, personal-best PEF (L/min), resting respiratory rate (breaths/min), and resting HR (beats/min). Age and asthma duration are displayed but not used by RECAP; attack history sets initial priors. The supervised snapshot baseline also uses age. Dynamic records contain sample index, elapsed minutes, RR, HR, five-minute step count, PM2.5 (micrograms/m3) and optional scheduled PEF.

The four invented scenario families are balanced by patient index. All include ordinary walking. Some include increased exposure-driven obstruction, sensor bias or a mixed pattern. Concealed scenario names are never passed to inference. The nonlinear obstruction and activity-debt simulator uses different transition equations from the filter, but shares hand-authored relationships. This limits independence and makes the benchmark an engineering test rather than a clinical simulation.

Hidden states and dense PEF target arrays exist only inside evaluation or synthetic measurement generation. `public_patient()` removes them. The predictor can run identically on the public dictionary. A dedicated test verifies this and another modifies all future observations without changing an earlier prediction.

## Endpoint and metrics

Three consecutive five-minute future observed PEF fractions below 0.8 of personal best within the next 120 minutes. This includes ongoing low states and is not a clinically adjudicated attack. The simulator observes dense future PEF for scoring; normal input PEF is sparse every four hours. No claimed two-hour lead time follows from a two-hour horizon.

Benchmark issues every 30 minutes from t=36 through t=258. Last-hour HR/RR completeness must be at least 75%, latest paired readings no older than 15 minutes, and at least three hours of history must exist. Missing readings skip wearable updates; no future fill occurs. Values outside the invented model support and device artifacts beyond the synthetic scenarios have not been comprehensively validated.

AUROC, Brier, precision/recall at probability 0.5 and confusion counts describe overlapping issue windows. They are not independent events. PEF forecast MAE is measured as a fraction of personal best, not L/min. The paired policy Brier confidence interval resamples whole patients 1,000 times; it does not represent variation across possible simulator designs. Group differences are toy-scenario diagnostics, not demographic fairness evidence.

## Calibration and policy comparison

The `no_ehr_personalization` ablation removes personal resting HR/RR baselines and attack-history priors; it still retains personal-best PEF for units/normalization. Likewise, the `wearable_only` artifact name means the snapshot sensor/context feature set: its PEF ratio still depends on known personal-best PEF. It is not a pure no-EHR experiment. Labels in the interface use sensor/context wording; conclusions must keep this limitation explicit.

Snapshot classifiers fit on 48 training patients; normalization is training-only. Filters are hand specified, so no claim of learned physiology is made. Each ablation has its own one-input logistic risk mapping fitted on 16 calibration patients. The frozen passive mapping is reused for probe policies; post-probe calibration may differ and is a limitation. All final results use 24 test patients. Model changes during development are not a preregistered study; the fixed population is not a protected external clinical test.

All policies receive regular PEF every 48 samples. Fixed optional PEF probes occur at t=108 and 204 (09:00 and 17:00), avoiding normal measurement timestamps. Adaptive policy evaluates candidate information on the same 30-minute issue grid, caps optional probes at two and uses a two-hour cooldown. It can use fewer probes; the budget is a common maximum, not necessarily equal realized measurement count. Optional measurements are generated only at their request times. Fixed/adaptive outcomes share the same synthetic patients and target noise.

## Uncertainty and safety boundaries

Model-family weights are not probabilities of clinical diagnoses. Recovery debt is a mathematical memory of observed activity, not an established airway biomarker. Forecast bands are Gaussian-mixture moment approximations and have no validated 90% coverage. The risk index is only empirically calibrated on synthetic data. The planner may reduce model ambiguity without improving future-event prediction. Burden weights are assumed, not measured patient preferences.

No raw PPG, cough audio, pulse oximetry, real inhaler integration, validated PM sensor, personal spirometry device or hardware was connected. No India-specific training, prospective silent study, medication model, fairness analysis, regulatory assessment or production security validation was completed.
