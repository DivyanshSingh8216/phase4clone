# Phase 4 implementation gap register

## Preserved achievements
- Monthly PDF/XLSX report builder and generated report artifacts.
- Report reconciliation against five Phase 3 governed views.
- Report-side workforce and anomaly small-group filtering.
- Board-pack PPTX and narrative.
- FastAPI health endpoint and five-metric API allowlist: M16, M17, M18, M21, M22.
- Metric lineage, release validator, handover and acceptance documentation.
- The recorded 10-test result is historical evidence, not a new test run on this branch.

## Task 17 gaps
1. The monthly GitHub Actions workflow builds and uploads report artifacts; it does not refresh and publish the database consumed by the dashboard.
2. The Docker image contains a database snapshot, not a live refresh mechanism.
3. Render is a starting point. Streamlit production intentionally fails closed until verified SSO exists.
4. No live URL, phone screenshot, stranger test, hosted secret configuration or successful production refresh is evidenced.
5. Hosting comparison and the 200 MB data publishing decision require actual warehouse size and provider-plan measurements.

## Task 18 gaps
1. The current explorer loads the entire metric catalogue before role-specific selection.
2. It has a department/team selector, not a verified cascading company-to-department-to-team hierarchy.
3. The existing API allowlist is not the Task 18 metric permission matrix for every dictionary metric.
4. The repository lacks the official demo_users.csv, metric dictionary and authoritative department/team hierarchy. Templates are intentionally unpopulated.
5. The old suppression helper returns false when group size or threshold is missing. The new privacy helper fails closed.
6. Full adversarial testing across filters, API, exports, overlapping groups and differencing remains required.

## Data-dependent blockers
- Do not invent role assignments, metric sensitivity, thresholds, team membership, or M27/M28 calculation inputs.
- M27 requires validation of its denominator/population and threshold from the dictionary and governed source view.
- M28 requires forecast and actual inputs; do not calculate MAPE if actuals are absent or misaligned.
- A genuine upstream refresh source and production identity provider are external prerequisites.

This workspace is additive. It does not claim Task 17 or Task 18 production acceptance until the blockers are resolved and live tests are evidenced.
