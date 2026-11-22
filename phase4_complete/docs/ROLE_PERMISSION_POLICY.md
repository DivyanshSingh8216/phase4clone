# Task 18 demo permission policy

Status: conservative implementation proposal for demo validation. This is not an approved production access-control policy. Obtain written approval from the PulseIQ data owner and HR/privacy owner before production use.

## Current grants

| Role | Metric IDs | Permitted grain | Rationale / limitation |
|---|---|---|---|
| EXECUTIVE | M16, M17, M18, M21, M22 | Company | Carries forward the existing Phase 4 executive aggregate allowlist. Company-level only; no department/team drill-down is granted here. |
| HR | M27 | Department | The Phase 3 dictionary defines M27 as department-level high-risk share, minimum group size 10. The Phase 3 governed view applies the threshold upstream. |
| MANAGER | None | None | The demo manager has a D01/T01/T02 assignment, but the source review did not establish which metrics the business authorizes managers to see. No grant is inferred from the assignment alone. |
| ADMIN | None | None | Administrative capability does not automatically confer access to sensitive workforce or payroll analytics. |

The registry intentionally omits M01-M15, M23-M28 for all roles except HR/M27, and all team-grain grants. The metric dictionary describes metric semantics and thresholds; it does not define role entitlements. Missing grants are denied.

## M27 privacy handling

- M27 is exposed only at department grain.
- The Phase 3 SQL view v_m27_high_risk_share groups by date and department and applies HAVING COUNT(DISTINCT employee_id) >= 10.
- The published all_metrics schema has no universal population-count column. The explorer therefore does not invent or infer one.
- The registry marks M27 as governed_view, and the UI relies on the upstream Phase 3 suppression. It does not expose numerator, employee rows, or population counts.
- Team drill-down is denied because M27 is not defined at team grain.

## M28 status

M28 is not granted in the current registry. In the inspected Phase 3 snapshot, forecasts cover October 2026 through March 2027 while actual headcount ends in September 2026. There are no matched forecast/actual periods, so MAPE cannot be calculated. Do not replace this with zero or display forecast projections as forecast accuracy. Revisit the grant only after matching actuals arrive and the source view produces valid MAPE observations.

## Production prerequisites

1. Data owner and HR/privacy owner approve the role/metric/dimension matrix.
2. Replace demo identities with verified SSO/OIDC claims and trusted manager scope.
3. Validate all source view definitions and aggregate rows against the production warehouse.
4. Run adversarial tests for filter manipulation, overlapping groups, differencing, exports, API access and role escalation.
5. Repeat the acceptance suite against the deployed production URL.

Demo CSV identities are fabricated test fixtures and must never be used as production credentials.
