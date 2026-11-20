# Phase 4 achievement register

This register preserves previously completed work and distinguishes it from new work.

| Area | Existing achievement | Evidence state |
|---|---|---|
| Task 16 | Monthly PDF/XLSX report builder with five evidence tables | Previously executed |
| Task 16 | Full-period and September 2026 report artifacts | Files retained in reports/ |
| Task 16 | Reconciliation to five Phase 3 governed views | Previously completed |
| Task 16 | Workforce and anomaly export suppression | Implemented and previously tested |
| Task 17 | Streamlit explorer, Dockerfile and Render Blueprint | Implemented; deployment unverified |
| Task 17 | Monthly GitHub Actions report artifact workflow | Implemented; not a warehouse refresh |
| Task 18 | ADMIN, HR, MANAGER and EXECUTIVE role concepts | Existing access-control code |
| Task 18 | Executive company-only and Manager assigned-department rules | Previously tested |
| Task 18 | Department aggregates for HR/Admin | Partial implementation |
| Task 19 | FastAPI health route and five-metric allowlist M16/M17/M18/M21/M22 | Previously tested |
| Task 19 | API lineage metadata | Implemented |
| Task 20 | Board pack PPTX and narrative | Generated; PPTX integrity previously checked |
| Quality | 10 tests passed in a prior local run | Historical result; not a result for this new workspace |
| Data integrity | Original Phase 1/2/3 workbook SHA-256 checks passed | Historical result |

## New additive work in this branch

- Fail-closed metric/dimension policy module.
- Demo identity resolver that requires a real configured demo user.
- Trusted hierarchy loader with duplicate/blank mapping checks.
- Privacy helper that withholds results if group size or threshold is unknown.
- Role-first explorer implementation, pending official source configuration and runtime tests.
- Task 17 hosting/refresh decision record.
- Task 18 acceptance and adversarial test plan.

## Not achieved / externally blocked

- Official demo user and metric dictionary files are not in the committed source repository.
- Department/team hierarchy and group-size source columns have not been validated against Phase 3 warehouse.
- M27/M28 calculations are not validated against source data.
- SSO/OIDC production adapter is not configured.
- Warehouse refresh/publish has not been executed.
- Public hosting, live URL, phone screenshot and stranger test have not been completed.
- No new local pytest or Docker build was run in the hosted build environment.
