# Prior-art check and originality boundary

Reviewed 18 October 2026. This is a targeted public-literature check, not an exhaustive systematic review, patent search, or proof that nobody has implemented the same composition.

## Existing work that rules out broad novelty claims

1. **Home monitoring in asthma: towards digital twins** (2023). https://pubmed.ncbi.nlm.nih.gov/37102597/ . Asthma home-monitoring twins are an established direction. REBOUND cannot claim to invent them.
2. **AirPredict** (2025). https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2025.1573342/full . Wearables, personal pollution exposure, spirometry and clinician interfaces already exist together. Adding environmental sensing to asthma monitoring is not this project’s novelty.
3. **Slowing Down of Recovery as a Generic Risk Marker** (2016). https://doi.org/10.1097/CCM.0000000000001564 . Recovery slowing has been proposed across episodic disorders, including asthma. REBOUND does not invent recovery-based warning.
4. **OTTER-A**, University of Edinburgh project. https://usher.ed.ac.uk/research/medical-informatics/projects/otter-a . Wearable signatures of recovery and deterioration after an asthma attack are being studied. A recovery-focused asthma project is not unique by itself.
5. **AAMOS-00 / home monitoring dataset** (2023). https://www.nature.com/articles/s41597-023-02241-9 . A public research direction already combines connected asthma monitoring with attack prediction. The article identifies 22 phase-two participants and a longitudinal dataset. REBOUND has not downloaded, trained on or validated against these participants.
6. **Digital markers of asthma exacerbations: systematic review** (2024). https://pmc.ncbi.nlm.nih.gov/articles/PMC11647917/ . Existing marker evidence is heterogeneous; lung-function evidence is conflicting in the review. A plausible wearable association does not validate REBOUND’s endpoint or its hidden-state explanations.

## Existing methodological foundations

Kalman state estimation, Bayesian model averaging, multiple-model estimation, expected information gain, Gaussian quadrature and cost-sensitive sensing are existing methods. RECAP does not claim new mathematical foundations. It is not a full interacting multiple-model estimator because states are not mixed between components. Its approximate information objective does not integrate a validated clinical decision loss.

## Narrow contribution being proposed

A patient-conditioned bank explicitly competes between activity-recovery, airway-state and sensor-bias explanations; recovery diversity changes inferred temporal state; the system chooses or defers an extra observation under a two-measurement budget; actual new observations revise the displayed hypotheses. The package makes this workflow executable and tests whether the components help. The targeted search did not establish an identical implementation, but that absence does not establish uniqueness.

## Falsifiable hypotheses

- Personal EHR baselines improve future low-PEF risk estimates over a population baseline.
- A bank of recovery time constants improves over one fixed retention setting.
- Adaptive information-based observation selection improves risk prediction relative to two fixed additional PEF observations.
- A drifting sensor can sometimes be separated from an airway-state change by an independent observation.

Report the measured results, including failures. Do not claim that collecting information necessarily improves event prediction, that the displayed explanation is a diagnosis, or that the project is clinically superior to existing products.

## Clinical context

WHO asthma fact sheet: https://www.who.int/news-room/fact-sheets/asthma . Asthma is a chronic noncommunicable disease; environmental triggers and monitoring are relevant context. WHO South-East Asia burden report: https://www.who.int/southeastasia/publications/i/item/9789290221494 . These sources establish relevance, not simulator validity. No Indian-population prevalence or efficacy statistic is invented for the pitch.
