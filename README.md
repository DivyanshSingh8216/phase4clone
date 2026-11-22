# PulseIQ Phase 4 | Streamlit deployment

Phase 4 is additive to the Phase 3 warehouse. The original `PulseIQ_Dataset.xlsx` and all Phase 1-3 source artifacts must remain unchanged.

## Streamlit Community Cloud

The Streamlit entry point is `streamlit_app.py`. Deploy the `phase4-complete` branch from GitHub and set the main file to `streamlit_app.py`. Configure OIDC and the hosted warehouse secrets as documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

The app uses Streamlit OIDC sign-in, maps the verified email to an approved `user_id`, and reads role/scope from `phase4_complete/config/demo_users.csv`. It downloads a hosted HTTPS DuckDB snapshot, verifies its SHA-256 checksum and required tables, and opens it read-only. No laptop upload or committed database is used.

## Task 18 role and metric access policy

The four application roles have different responsibilities and metric scopes. The registry is based on the Phase 3 governed `all_metrics` view, not solely on the catalogue's intended grain.

| Role | Metric access | Rationale |
|---|---|---|
| ADMIN | M01-M28, at the available governed grain | Trusted platform/data administrator. Can inspect all governed aggregates, but does not bypass SQL-view suppression or gain employee-level rows. |
| HR | M01-M15, M27-M28, at department grain | Workforce operations: headcount, hiring, exits, attrition, payroll aggregates, attendance, leave, attrition-risk share and forecast error. Gross/net pay and payroll metrics are only aggregated by department and the Phase 3 view applies its minimum group rules. |
| MANAGER | M01-M06, M09-M14 at the assigned department; M24 at assigned team | Department workforce planning, attrition, employer-cost/overtime/variable-pay aggregates and attendance. Team velocity is available only for the manager's assigned team IDs. No employee pay detail, HR risk scores, or company-wide finance data. |
| EXECUTIVE | M16-M21, M22-M23, M25-M26 at company grain | Company financial performance, receivables, aggregate task delivery/cycle-time and anomaly-rate indicators. No department/team drilldown or employee-level workforce data. |

### Source-grain limitations that the policy deliberately respects

The metric catalogue describes M16 as account-grain, M21 as client-grain, M22-M23 and M25 as team-grain, and M26 as source-grain. However, the current Phase 3 `all_metrics` view exposes only `metric_id, metric_name, period, department_id, value, unit, min_group_size, caveat`. The actual views for M16, M21, M22, M23, M25 and M26 return a NULL `department_id`; they therefore appear only as company-level aggregates in this explorer. The policy does not pretend that account, client, team or source drilldowns exist when the current data view does not expose those keys.

M24 is the exception: its `department_id` field explicitly contains `team_id`, so the explorer treats it as team-grain and restricts managers to their trusted team assignments. M01-M15 and M27 expose department keys and use the source-defined minimum group thresholds. M28 is permissioned for HR and ADMIN at department grain but currently has no matching actuals, so the explorer must show it as unavailable rather than zero.

The demo manager is assigned to D01 and T01/T02 in `demo_users.csv`. The hierarchy file currently contains IDs only; it does not provide department names or business-function labels. Consequently, role policy is based on the defined application roles and the available metric scopes, not guessed department names. Before production, the data owner and HR/privacy owner must approve role assignments and confirm the hierarchy mapping. ADMIN is privileged and must be assigned only to trusted administrators.

## Other Phase 4 deliverables

| Task | Current repository status |
|---|---|
| 16 | Monthly report builder and manually triggered GitHub report workflow; scheduled cadence and clean-machine evidence remain to verify |
| 17 | Streamlit deployment entry point and hosted snapshot validation; public deployment, scheduled warehouse refresh, phone and stranger tests remain external |
| 18 | Role-specific 28-metric permission registry, source/team/department grain controls, manager assignment scoping and policy tests added; local test run, privacy break-it evidence and production approval remain to verify |
| 19 | Five-metric FastAPI service and lineage endpoints; production identity proxy and separate API deployment remain open |
| 20 | Board pack and release notes; live-data reconciliation, demo recording, final challenge evidence and final release tag remain open |

## Local setup

Use Python 3.11 and the pinned dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
```

For local development only, set `PULSEIQ_AUTH_MODE=development` and `PULSEIQ_DEMO_USER` to a user in `phase4_complete/config/demo_users.csv`, then run the role explorer with the approved local Phase 3 warehouse. Never expose development mode publicly.

## Data integrity

The source workbook is read-only. Work only on copies and derived outputs. Never commit credentials, signed object URLs, the private DuckDB warehouse, or personal employee-level data.
