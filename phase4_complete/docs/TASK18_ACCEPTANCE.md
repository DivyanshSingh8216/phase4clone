# Task 18 - Self-service KPI explorer acceptance

## Required source-of-truth inputs

- Official demo_users.csv with ADMIN, HR, MANAGER and EXECUTIVE assignments.
- Official metric dictionary with definitions, grain, sensitivity, source, denominator and minimum group size.
- Authoritative company/department/team hierarchy.
- Metric-specific governed group-size/population field.

The repository templates are blank by design until these source files are supplied. No user assignment, metric permission, threshold or team mapping is invented.

## Permission policy

The final matrix must be generated from the official metric dictionary and reviewed by the data owner. Each role/metric row must specify:
- allowed_dimensions: company, department and/or team
- metric_grain: company, department or team
- org_key_column: governed key used by the metric view
- group_size_column: population count used for privacy enforcement
- minimum_group_size: dictionary-approved threshold

A metric/dimension pair absent from the registry is denied. Missing group size or missing threshold suppresses the result.

## Drill-down

The UI must authenticate the user first, resolve trusted scope, then show only permitted metrics and dimensions. Company → department → team selectors must cascade from the authoritative hierarchy. Manager department/team scope comes from the trusted demo-user/SSO record, never from an editable browser parameter.

## Privacy attack tests

- Groups of 1, 2 and 3.
- Group exactly at threshold and one below threshold.
- Department/team filter manipulation.
- Direct API calls with changed role, department and metric IDs.
- Repeated and overlapping filters to test differencing.
- Totals/subtotals that could reconstruct a suppressed value.
- Exports and downloadable tables.
- Missing group-size field and missing threshold.

The expected outcome is no value, count or chart point for a suppressed group. A generic suppression message may be shown without disclosing the suppressed group size.

## Live acceptance

Capture screenshots of at least two role views, record each adversarial test and outcome, deploy the corrected app, and repeat tests against the live URL. Task 18 is not complete until Task 17 is live and this live retest passes.
