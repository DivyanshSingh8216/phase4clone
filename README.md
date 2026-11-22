# PulseIQ Phase 4 | Streamlit deployment

Phase 4 is additive to the Phase 3 warehouse. The original `PulseIQ_Dataset.xlsx` and all Phase 1-3 source artifacts must remain unchanged.

## Streamlit Community Cloud

The Streamlit entry point is `streamlit_app.py`. Deploy the `phase4-complete` branch from GitHub and set the main file to `streamlit_app.py`. Configure OIDC and the hosted warehouse secrets as documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

The app uses Streamlit OIDC sign-in, maps the verified email to an approved `user_id`, and reads role/scope from `phase4_complete/config/demo_users.csv`. It downloads a hosted HTTPS DuckDB snapshot, verifies its SHA-256 checksum and required tables, and opens it read-only. No laptop upload or committed database is used.

## Current role-policy status

The committed demo policy now grants:
- ADMIN: M16, M17, M18, M21 and M22 at company grain, plus M27 at department grain.
- EXECUTIVE: M16, M17, M18, M21 and M22 at company grain.
- HR: M27 at department grain, with a minimum-group threshold of 10 enforced by the governed source view.
- MANAGER: M27 at department grain, restricted in the explorer to the manager's assigned department (D01 in the demo registry); the governed source view enforces the minimum-group threshold of 10.

The demo hierarchy and user assignments are illustrative. Before production, the data owner must approve the metric grants and validate the hierarchy against an authoritative source. Task 18 still requires end-to-end role screenshots, live break-it testing, and confirmation that the upstream M27 view suppresses groups below 10.

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
