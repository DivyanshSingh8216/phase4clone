# PulseIQ Phase 4 | Submission Repository

PulseIQ Phase 4 extends the Phase 3 governed warehouse with reporting, API,
deployment scaffolding, board-pack outputs, and a role-aware Streamlit KPI
Explorer (Task 18).

## Repository layout

- `streamlit_app.py`: Streamlit application entry point.
- `phase4_complete/`: Task 18 explorer, role policy, privacy helpers, config,
  tests, and implementation notes.
- `scripts/`: release validation and metric validation/bootstrap utilities.
- `docs/`: deployment, API lineage, metric lineage, handover, and acceptance.
- `board_pack/`: Phase 4 board-pack presentation.
- `reports/`: generated validation/report outputs (local outputs are ignored).

## Quick start (Windows PowerShell)

Python 3.11 is recommended.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\repair_metrics.py --download-db --validate
$env:PULSEIQ_AUTH_MODE = "development"
$env:PULSEIQ_DEMO_USER = "demo_admin"
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

The metric utility downloads the verified Phase 3 warehouse into
`phase4_complete/data/pulseiq.duckdb`, checks its Git blob SHA-1, opens it
read-only, and writes `reports/metric_validation.csv`. It never edits the
warehouse. To select another approved demo role, set
`PULSEIQ_DEMO_USER` to `demo_hr`, `demo_manager_d01`, or
`demo_executive`.

## Metric handling and data integrity

- M28 is unavailable when matching forecast/actual observations are absent;
  it must never be shown as 0% accuracy.
- M21 and M27 are snapshots when only one reporting period exists. The UI
  labels them as snapshots instead of implying a time trend.
- M05/M06 null or suppressed values remain missing, not zero.
- M18 is checked against matched M17/M16 periods. The official metric
  denominator must be confirmed before any source value is changed.
- M09 requires reconciliation against the approved ledger account mapping.
- M25 negative cycle-time values are flagged for source inspection.
- The database is opened read-only. The original Phase 3 source workbook and
  database are not modified.

## Demo identities

| User ID | Role |
|---|---|
| demo_admin | ADMIN |
| demo_hr | HR |
| demo_manager_d01 | MANAGER |
| demo_executive | EXECUTIVE |

Development mode is for local demonstration only. Production must use verified
OIDC identity and the configured hosted warehouse secrets. Never expose demo
authentication publicly.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\validate_release.py
```

Test execution and production deployment must be verified in the target
environment before claiming acceptance. See `docs/ACCEPTANCE_CHECKLIST.md`
and `phase4_complete/docs/IMPLEMENTATION_GAPS.md`.

## Data and secrets policy

The downloaded DuckDB is a local runtime artifact and is excluded from Git.
Do not commit employee-level source data, credentials, private object URLs,
virtual environments, generated reports, or machine-specific files.
