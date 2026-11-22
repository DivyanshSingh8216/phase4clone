# PulseIQ Phase 4 | Streamlit deployment

Phase 4 is additive to the Phase 3 warehouse. The original `PulseIQ_Dataset.xlsx` and all Phase 1-3 source artifacts must remain unchanged.

## Streamlit Community Cloud

The Streamlit entry point is `streamlit_app.py`. Deploy the `phase4-complete` branch from GitHub and set the main file to `streamlit_app.py`. Configure OIDC and the hosted warehouse secrets as documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

The app uses Streamlit OIDC sign-in, maps the verified email to an approved `user_id`, and reads role/scope from `phase4_complete/config/demo_users.csv`. It downloads a hosted HTTPS DuckDB snapshot, verifies its SHA-256 checksum and required tables, and opens it read-only. No laptop upload or committed database is used.

## Task 18 role and metric access policy

The permission registry is role-specific and covers all 28 catalogue IDs. Access is not a blanket grant of the same five metrics to every role.

| Role | Approved metric scope |
|---|---|
| ADMIN | All catalogue metrics, restricted to each metric's actual company, department, or team grain. Administrative access does not bypass source-view privacy suppression. |
| HR | HR Analytics metrics M01-M06 and M13-M14, plus the governed AI/ML high-risk share M27. No payroll amount or finance-ledger metrics are granted by the HR role. |
| MANAGER | Department-scoped headcount/attrition/attendance and cost metrics (M01, M04-M05, M09-M10, M13-M14), plus operational delivery metrics M22-M25. M22-M25 are team-grain and limited to the manager's assigned team IDs. |
| EXECUTIVE | All catalogue metrics at their source-defined grain. Company-grain metrics remain company-only; department/team metrics are shown only at their defined grain and remain subject to privacy rules. |

The registry applies the metric catalogue's documented minimum-group thresholds to people/payroll/finance metrics where present. The upstream governed Phase 3 views enforce these thresholds; M27 retains its threshold of 10 and must never identify or rank named employees. M24 is an operational velocity aggregate and are allowed without an employee-count threshold. M22-M25 store team IDs in the `department_id` field of `all_metrics`, as documented in the metric view.

M28 is present in the catalogue and permission registry but currently has no rows because matching actual headcount is unavailable for the forecast periods. The explorer reports it as unavailable rather than manufacturing forecast accuracy.

Manager scope comes only from the approved `demo_users.csv` department/team assignments and the hierarchy file. No department/team mapping is inferred from metric ownership. The current demo manager is scoped to D01 and T01/T02. Before production, the hierarchy and role grants must be approved by the data owner and HR/privacy owner; the ADMIN role is privileged and must be assigned only to trusted administrators.

## Other Phase 4 deliverables

| Task | Current repository status |
|---|---|
| 16 | Monthly report builder and manually triggered GitHub report workflow; scheduled cadence and clean-machine evidence remain to verify |
| 17 | Streamlit deployment entry point and hosted snapshot validation; public deployment, scheduled warehouse refresh, phone and stranger tests remain external |
| 18 | OIDC identity mapping and fail-closed policy foundation; full role matrix, hierarchy drilldown and break-it acceptance remain open |
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
