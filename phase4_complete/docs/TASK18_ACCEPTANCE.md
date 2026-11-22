# Task 18 - Self-service KPI explorer acceptance

## Implemented foundations

- Demo identities are committed in config/demo_users.csv. They are fabricated test fixtures, not production identities.
- Department/team hierarchy is populated from the inspected Phase 3 dim_department and dim_team sheets.
- A conservative, explicit role/metric/dimension registry is committed in config/metric_permissions.csv.
- Missing role/metric/dimension grants are denied.
- Metric grain and SQL key are explicit per permission row; team drill-down is not inferred from department_id.
- M27 is granted to HR at department grain only. The Phase 3 governed view enforces the dictionary minimum group size of 10 before publishing results. The explorer does not invent a population-count field.
- M28 is not granted because the inspected Phase 3 snapshot has no matching forecast-month actuals. MAPE is unavailable, not zero.
- Production identity resolution fails closed until verified SSO/OIDC is configured.

See ROLE_PERMISSION_POLICY.md for the exact proposed demo matrix and approval caveat, and DEMO_FIXTURES_AND_SOURCE_AUDIT.md for source findings.

## Current proposed demo grants

- EXECUTIVE: M16, M17, M18, M21 and M22 at company grain only.
- HR: M27 at department grain only.
- MANAGER: no metric grants pending business-owner approval of manager-visible metrics.
- ADMIN: no KPI grants; administrative access does not imply access to sensitive analytics.

This is an implementation proposal for demo validation, not a production-approved access policy. Obtain data-owner and HR/privacy-owner approval before production.

## Remaining acceptance tests

- Run automated tests in GitHub Actions and record a passing run for the latest commit.
- Validate the explorer against the actual Phase 3 DuckDB file with PULSEIQ_DB_PATH set; the database is not bundled in this repository.
- Test company-to-department-to-team cascading only for metrics whose governed source grain supports each level.
- Test manager department/team manipulation after manager metric grants are approved.
- Test groups of 1, 2, 3, one below threshold, and exactly at threshold against governed views.
- Test repeated and overlapping filters, totals/subtotals, differencing, exports and API endpoints for reconstruction risks.
- Test all four roles and unknown/missing identity against the actual app.
- Capture role screenshots and repeat all adversarial tests against the deployed URL.

## Production completion criteria

Task 18 is not complete until Task 17 is live, production SSO and trusted scope are configured, the access matrix is approved, the live acceptance suite passes, and evidence is recorded. Do not expose development mode publicly.
