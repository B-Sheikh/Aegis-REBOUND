# Jury questions — precise answers

## What is different from another asthma-alert app?

The implemented workflow maintains competing dynamical explanations and spends a bounded optional-measurement budget to resolve them. The output includes an evolving state, hypothesis weights, a trajectory, the information score and the effect of assimilating a new observation. Asthma alerts themselves are not new.

## What exactly is new in the algorithm?

We propose this specific combination of personal-baseline conditioning, recovery-retention diversity, airway/sensor hypothesis competition, and cost-aware quadrature probing. The constituent methods are established. A targeted prior-art map is included, but no exhaustive novelty or patent claim is made.

## Why call it a twin instead of a classifier?

Each component has persistent continuous state updated through time, forecasts a future trajectory, and revises state after a new observation. It is a focused functional virtual-patient representation. It is not a whole-body replica or a clinically identified physiology model. A classifier can score better at the binary endpoint; that does not supply the same inspectable state/observation workflow.

## What did the experiments actually support?

On one synthetic held-out group, adaptive optional observations used 38 probes versus 48 for a fixed schedule and slightly improved Brier score. The paired patient-bootstrap interval favored the adaptive policy in that run. Removing personal resting baselines/priors degraded the filter, but personal-best PEF normalization remained. The recovery bank did not improve event classification and simpler classifiers had better Brier scores. Do not omit those negative findings.

## Is the endpoint an asthma attack?

No. It is three future dense simulator PEF observations below 80% of personal best within two hours, including ongoing low states. It is not a clinically adjudicated attack, admission, emergency event, or guaranteed advance warning.

## How do you stop future leakage?

The inference object receives only EHR and the observed prefix. Hidden scenario/state and dense future target arrays are excluded. A test mutates all future sensor samples and removes hidden target/state arrays without changing the earlier result. The optional probe is generated only at its request time. Retrospective reveal does not feed inference.

## Does the additional probe genuinely change the twin?

Yes. A Kalman state/covariance update and a likelihood weight update are applied to the current bank. A test confirms the change; the dashboard shows it. The current planner’s hypothetical information integration updates weights only and holds component risk indices fixed, so it is an approximation to a richer state-aware value-of-information calculation.

## What would be needed for clinical relevance?

Permitted genuinely paired longitudinal records, timestamps indicating availability, device-quality characterization, validated clinical outcomes, protocol freezing, site/time/patient separation, independent calibration and external evaluation, alarm-burden assessment, prospective silent testing, and clinician, ethics, security and applicable regulatory review. None is implied by synthetic performance.

## Did the earlier molecular cell model become a patient model?

No. Earlier projects supplied interface and simulation ideas. The respiratory algorithm is a separate implementation. Arbitrary cell-health targets are not used to infer patient physiology, and unlicensed code or private archive material is not redistributed.
