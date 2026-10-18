# RECAP algorithm specification

## State and hypotheses

For each component, x = [d, v, r, b] represents an obstruction proxy, its trend, activity-recovery debt, and wearable respiratory-rate bias. There are three hypothesized explanations (ordinary recovery, airway deterioration, sensor drift) crossed with recovery retention rho in {0.40, 0.64, 0.86}. This gives nine filters. These names describe model families, not ground-truth diagnoses.

The discrete step is five minutes. The transition is:

```
d_next = 0.995*d + v + exposure_drive(mode)
v_next = 0.93*v
r_next = rho*r + 0.028*(steps/5)
b_next = bias_retention(mode)*b
```

The airway family receives `max(PM2.5 - 34, 0)*0.00019`; other families do not. The bias retention is 0.98 for sensor drift and 0.70 otherwise. Mode-specific process-noise matrices and observation-noise values are specified directly in `recap.py`. All coefficients are engineering assumptions, not physiological constants or clinically fitted parameters.

Observation equations subtract personal resting baselines and instantaneous activity terms:

```
RR - resting_RR - 0.04*(steps/5) = 7.5*d + r + b + noise
HR - resting_HR - 0.33*(steps/5) = 13*d + 2.4*r + 0.12*b + noise
PEF / personal_best = 1 - 0.60*d - 0.006*r + noise
```

An independently measured RR is modeled without the wearable bias term; it retains the instantaneous activity contribution. EHR attack history sets the initial family priors. EHR baselines affect measurements throughout replay, so static and dynamic information are fused at every update.

Each component uses a linear Kalman update with Joseph-form covariance correction. State clipping introduces a nonlinear approximation; the covariance is not corrected for truncation. Therefore the resulting Gaussian moments are descriptive. Weight updates use log(weight)*0.96 + log-likelihood*0.30 followed by normalization and a 1% uniform reset mixture. This reset prevents an explanation from becoming irrecoverably zero during a regime change. These are hand-specified robustness choices, not an optimally learned switching process. Components do not exchange state as in a full interacting-multiple-model filter.

## Forecast and risk mapping

Each component advances 24 steps with no additional activity and current PM2.5 held constant. Future exposure is not read. Mixture means and total variances are combined by the law of total variance. Bands use mean +/-1.645 standard deviations with display support clipping. They are **not** conformal or clinically calibrated 90% intervals, and mixture skew makes a Gaussian interpretation approximate.

At each horizon, compute a Gaussian marginal probability of PEF fraction below 0.8. Take the maximum geometric mean over consecutive triples. This is a smooth risk index; multiplying marginal probabilities does not correctly integrate a joint correlated crossing event. A scalar logistic mapping fitted on separate calibration patients maps the index to an empirical future-event probability. Prediction includes ongoing low states, and does not establish detection before onset.

## Information objective

Candidates are an optional peak-flow ratio observation and an independent respiratory-rate observation. Each candidate defines a Gaussian predictive observation under every component. Nine-point Gauss-Hermite quadrature, weighted by the component mixture, integrates possible observed outcomes.

For each hypothetical outcome, recompute only hypothesis weights using Bayes likelihood. Hold the component future risk indices fixed. Define U as binary entropy of the mixture risk index plus 0.15 times hypothesis entropy. Expected gain is U before minus expected U after. Score equals this gain minus the assumed burden (0.035 nats for PEF, 0.018 for independent RR). Values are rounded for display and selection. A positive highest score may request a simulated measurement; otherwise choose wait. Enforce no more than two optional probes per day and a 24-step cooldown.

The entropy and burden operate in algorithmic units, not clinical utility. Candidate uncertainty from a full covariance update is not propagated through hypothetical future forecasts. This approximation is deliberately documented rather than mislabeled exact Bayesian experimental design. A more exact extension would update each candidate-conditioned state, reforecast and integrate the downstream clinical loss, but would need a validated loss and measurement model.

When a simulated observation is actually supplied, all components receive both state/covariance updates and revised mixture weights. The data generator provides a new current-time observation; future targets remain unavailable. Optional independent RR has independent measurement noise and no wearable-bias term.

## What is proposed and how it is tested

The proposed contribution is the exact integration of a recovery-memory hypothesis bank with a limited-budget disagreement-resolution workflow. It is built from existing methods and is not established as a first invention. Tests remove recovery diversity and EHR personalization, compare simpler classifiers, and compare budgeted adaptive observation with a fixed schedule. These experiments can support or reject a benefit for this implementation in its simulator; they cannot validate biological truth or establish a research priority claim.
