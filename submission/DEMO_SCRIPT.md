# REBOUND — 20-minute demonstration and narration

This script accompanies the 12-slide project PDF. The supplied local video, when present, is computer narrated and uses verified application captures; it is not an uninterrupted live screen recording. Review it before upload. Team narration and live interaction are preferable for a final jury presentation. Do not upload the obsolete GlucoTwin walkthrough as this entry’s demo.

## 01 — The question

Welcome to Aegis REBOUND. We are Team Aegis, Abhishek Bharathi and Aadithya Ram, from Amrita Vishwa Vidyapeetham in Coimbatore. We have no incubator affiliation. Our project asks a question that a single risk number often hides. When someone’s breathing remains raised after ordinary daily activity, what is actually failing to return to baseline, and what observation would resolve that uncertainty?

The prototype is a focused respiratory digital twin for an adult asthma use case. It combines personal historical context with changing measurements and keeps several possible explanations alive. It can forecast a future low-peak-flow condition and select an additional simulated observation, subject to a small measurement budget. It can also decide that another measurement is not worth its assumed burden.

All records and all physiological relationships in this demonstration are invented. The software is a functioning engineering prototype, not a validated medical system. The included narration is computer generated. The application captures come from the implemented local dashboard. No person is asked to exercise, expose themselves to pollution, delay medical review, or change treatment. We observe routine activity passively inside a simulation and make the model’s assumptions visible.

## 02 — Competing explanations

Consider three virtual explanations for the same elevated respiratory signal. The first is ordinary recovery from activity. The second is a developing airway-state change. The third is a biased wearable sensor. Their predicted trajectories may overlap initially, but they do not imply the same hidden state or respond to the same additional observation.

A single classifier can produce an accurate future-event score without showing this ambiguity. REBOUND adds an inspectable hypothesis bank. Each explanation has continuous internal states and an evolving weight. The weights describe how well these particular models explain the observations. They are not diagnostic probabilities, and a high airway-family weight does not prove that a person has an exacerbation.

There are also cases the bank cannot represent. Infection, anxiety, cardiac conditions, poor measurement effort, medication effects, and other disturbances are not comprehensively modeled. If every component is wrong, averaging them does not make the result correct. The interface therefore labels these as competing model explanations and exposes the limitations next to the forecast. The project’s contribution is making the uncertainty actionable within the simulator, not claiming to resolve every real clinical cause of raised breathing.

## 03 — Two streams, one personal state

The static stream contains synthetic historical information: a personal resting respiratory rate, resting heart rate, personal-best peak flow, and prior attack count. The profile also shows age and asthma duration, but those two display fields are not used by the RECAP filter. Historical baselines matter because the same observed respiratory rate can represent a different deviation for different people.

The dynamic stream contains simulated respiratory rate, heart rate, five-minute step counts, environmental particulate concentration, and a sparse peak-flow observation every four hours. The model never reads a future sensor sample. It also does not receive the simulator’s hidden obstruction, recovery debt, bias values, or scenario label.

At each five-minute replay step, the system advances every candidate state and compares predicted measurements with the new observed values. This updates both the states and their explanatory weights. A patient’s history remains part of the measurement model throughout that process, so static and dynamic fusion happens continuously. The source includes a public-patient projection that strips out hidden states and future targets. Tests confirm that the predictor produces the same result with that public-only input, and that changing future samples cannot change an earlier result.

## 04 — Inside the proposed RECAP algorithm

RECAP stands for Recovery-conditioned Ensemble with Cost-Aware Probing. It is a proposed combination of existing mathematical ideas, not a claim to invent Kalman filtering, Bayesian model averaging, or information gain. The implementation crosses three explanations with three recovery-retention settings, giving nine small virtual patients.

Each candidate tracks four state variables: an obstruction proxy, its trend, an activity-recovery memory, and respiratory-sensor bias. Activity raises the recovery-memory state, which then decays according to the candidate’s retention value. Airway and sensor-drift families differ in their assumed process dynamics and noise. Personal EHR baselines condition the observation equations.

Kalman updates estimate continuous states. Tempered likelihood evidence updates model weights. Soft forgetting and a small reset mixture prevent a hypothesis from becoming permanently impossible after an early mismatch. These are explicit engineering choices, not optimally learned physiological constants. The model then forecasts twenty-four five-minute peak-flow ratios under two stated assumptions: no new activity and current exposure held constant. It cannot know the future route, future pollution, or future treatment. Those scenario assumptions are part of the forecast, not hidden facts supplied by the generator.

## 05 — A working state update

The captured application shows synthetic patient sixty-five at ten o’clock. The current respiratory rate is twenty-one point eight breaths per minute, and the personal historical resting rate is seventeen point four. Recent walking is visible as pale activity bars beneath the respiratory trace. The activity has ended, but the breathing signal does not simply return to the earlier baseline.

Before an optional observation, the airway-family weight is about eighty-one point two percent. Ordinary recovery has about five point two percent and sensor drift about thirteen point five percent. The calibrated synthetic future-low-peak-flow event estimate is seventy point three percent. These numbers are model outputs for this scripted case, not observed diagnoses.

The information panel selects a simulated peak-flow observation. When it is supplied, the airway-family weight rises to approximately ninety-seven point one percent, and one of the two optional observations has been spent. The state and forecast change because new current-time evidence was assimilated. The system then chooses wait because a second immediate observation is blocked by the cooldown and its remaining information score. In a live presentation, run the application and repeat this interaction rather than treating the screenshot as proof of a complete clinical workflow.

## 06 — Choosing the next observation

The planner compares two candidates: a peak-flow observation and a respiratory-rate reading from an independent simulated instrument. Peak flow responds differently to the modeled airway state than a wearable respiratory signal with bias. The independent respiratory reading excludes the wearable-bias term but retains activity effects. Neither observation is assumed to be perfect.

For each candidate, nine-point Gaussian quadrature integrates possible outcomes under every current component. Each hypothetical outcome changes the component weights through its likelihood. The utility combines entropy of the mixture’s future-risk index with a smaller hypothesis-entropy term. Expected reduction in that uncertainty is compared with an assumed burden, expressed in the same algorithmic units.

This implementation is approximate. It holds the component future-risk indices fixed while changing hypothetical weights. It does not reforecast every candidate-conditioned state or evaluate a validated clinical loss. Consequently, it may select a measurement that reduces ambiguity without improving the future-event forecast. A positive best score can spend a probe, but a two-hour cooldown and maximum two optional observations prevent unlimited testing. Wait is a genuine action. The burdens are disclosed assumptions, not measured patient preferences or healthcare costs.

## 07 — The experiment can reject the idea

We evaluate the mechanisms rather than assume that added complexity must help. The primary synthetic study has forty-eight training patients, sixteen calibration patients, and twenty-four held-out test patients. Every patient has twenty-four hours of five-minute observations. Patients do not cross splits.

Snapshot classifiers fit their normalization and coefficients using training patients. The filter dynamics are hand specified; the filters use the calibration group only to fit a scalar mapping from a risk index to an empirical future-event probability. The test group contains nine hundred and four usable issue windows, with two hundred and ninety-eight positives. Forecast issues occur every thirty minutes after three hours of history.

Our endpoint is three consecutive future peak-flow samples below eighty percent of personal best within the next two hours. It includes states where peak flow is already low, so it is not a claim of warning before an asthma attack. We remove recovery diversity, remove personal resting baselines and history priors, compare simple classifiers, and compare optional-measurement policies. The source preserves exact denominators and row-level predictions so the study can be reproduced and its limitations examined.

## 08 — Budgeted observation results

All observation policies receive the same regular peak-flow readings every four hours. The fixed policy adds two peak-flow observations, at nine in the morning and five in the afternoon. These times deliberately avoid the regular measurement timestamps, so an additional observation does not merely duplicate an existing value.

The adaptive policy can spend at most two optional probes per patient, using the information objective and cooldown. Across twenty-four patients, the fixed policy spends forty-eight additional observations. Adaptive selection spends thirty-eight, about twenty-one percent fewer. Its pooled Brier score is zero point zero five nine three, compared with zero point zero six two two for the fixed schedule. Lower Brier score means lower average squared probability error.

The paired patient-mean difference is approximately minus zero point zero zero two eight two. A one-thousand-resample patient bootstrap gives an interval from about minus zero point zero zero five three six to minus zero point zero zero zero one six. This favors adaptive probing in this one synthetic experiment. It is not proof of reduced patient burden or healthcare cost. The policies share a maximum budget, not equal realized probe counts, and the scoring objective and simulator may favor this particular strategy.

## 09 — The negative comparisons matter

Passive RECAP has an area under the receiver-operating curve of about zero point nine four three and a Brier score of zero point zero six four three. The single-recovery-setting version has a slightly better Brier score of zero point zero six three three. Recovery diversity therefore did not improve future-event classification in this experiment.

A simpler wearable-and-context snapshot classifier has Brier score zero point zero five seven four, also better than passive RECAP. This feature set still uses peak flow normalized by personal best, so its artifact name does not mean it contains no historical information at all. Removing personal resting baselines and attack-history priors from the filter degrades its Brier score to about zero point one six five, but even that ablation retains peak-flow normalization.

These outcomes limit our claim. We cannot say the proposed algorithm beats all baselines or that every component is necessary. Its purpose is to combine an evolving interpretable state with a measurement-selection workflow. That workflow has a modest positive observation-budget result here, while several classification comparisons favor simpler alternatives. We report both rather than retune after seeing the test outcome and present an apparent universal win.

## 10 — Missingness and changed physiology

The Sensor gap control loads a case with stale readings and approximately forty-two percent completeness in the last hour. The display withholds the event estimate and hypothesis ranking. The requirements are explicit: at least three hours of history, a paired heart and respiratory reading no older than fifteen minutes, and at least seventy-five percent completeness in the last hour.

This is a useful software boundary, but it is not a complete safety guarantee. Complete sensors may still be biased. Real behavior, illness, effort, devices, and treatment changes may violate the model. We test one such change using twelve new synthetic patients with another random seed, slower activity recovery, changed exposure sensitivity, and larger peak-flow observation noise.

Under this shift, area under the curve falls to about zero point nine zero six and Brier rises to about zero point zero seven five. These results show degradation within another invented setting, not external validation. Forecast bands are uncalibrated Gaussian-mixture moments and must not be called guaranteed ninety-percent clinical intervals. Their apparent biological meaning is limited by the equations and clipping approximations in the source. The dashboard keeps those limits next to the forecast.

## 11 — Originality and related work

Our prior-art check found existing asthma digital twins, connected exposure-and-spirometry platforms, studies of wearable recovery signatures, and proposals to use slowing recovery as a warning marker. Information-based experimental design and hypothesis banks are established methodological foundations. REBOUND does not claim to invent any of those ingredients.

The narrower proposed contribution is the executable composition: personal EHR conditioning, competing recovery and sensor explanations, a shared observation stream, and a budgeted choice of the next ambiguity-resolving observation. The testable question is whether that choice is useful under a stated simulator and measurement budget. The included prior-art map names related work and says what each source rules out as a novelty claim.

A targeted literature search cannot prove that nobody has built an identical system, and this is not a patent search. Likewise, a synthetic endpoint cannot establish clinical asthma-attack prediction. A stronger research program would require permitted linked patient data, source-availability timestamps, external devices and sites, clinical event adjudication, prospective silent evaluation, and relevant ethical and regulatory review. The current implementation supplies a reviewable foundation for that work rather than claiming it has already been completed.

## 12 — Reproduction and submission

The final package runs locally with Python and NumPy and includes the calibrated artifacts. It needs no GPU, paid service, API key or cloud connection after installation. The code includes the nonlinear synthetic generator, nine-filter bank, quadrature planner, baselines, policy experiment, raw predictions, and sixteen passing tests.

The tests cover future-data isolation, hidden-state exclusion, sequential replay, missing-data abstention, covariance and weight sanity, probe limits, budget and cooldown, state changes after an observation, endpoint boundaries, API validation, and patient split separation. The architecture PDF, project presentation, technical report, algorithm specification, data card and prior-art map accompany the implementation.

For external submission, designate the team leader, confirm both members’ student details, publish the actual GitHub repository publicly, and upload the reviewed demonstration as unlisted YouTube. Add the real links to the README and verify them without additional permissions. The local package does not perform those registration or publication steps. Team Aegis offers a focused respiratory twin that makes competing explanations and the next useful observation inspectable, with a proposed algorithm and experiments that can expose its limitations as well as its promise.
