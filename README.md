# PulseIQ Phase 4 | Release, access, APIs and handover

Phase 4 adds release tooling to the Phase 3 DuckDB warehouse. It is additive: it reads the Phase 3 database and exports derived reports; it does not edit the source workbook or earlier phase folders.

## Included deliverables

| Day | Deliverable | Entry point |
|---|---|---|
| 16 | Monthly PDF/XLSX reporting with five evidence tables, date range and cutoff | `python build_report.py --start 2025-04-01 --end 2026-09-30 --format both` |
| 17 | Container-ready Streamlit/API deployment configuration and scheduled GitHub Actions refresh | `Dockerfile`, `render.yaml`, `.github/workflows/monthly-report.yml` |
| 18 | Role-aware KPI explorer with department/team drilldown hooks, server-side access checks and small-group suppression | `streamlit run explorer.py` |
| 19 | FastAPI metrics API, metric definitions, source lineage and freshness metadata | `uvicorn api:app --host 0.0.0.0 --port 8000` |
| 20 | Board-pack narrative, release notes, handover and validation scripts | `docs/BOARD_PACK.md`, `RELEASE_NOTES.md`, `scripts/validate_release.py` |

## Data contract and safety

- Warehouse path defaults to `../phase-3/outputs/pulseiq.duckdb` relative to this directory. Override with `PULSEIQ_DB_PATH`.
- The original `phase-3/data/PulseIQ_Dataset.xlsx` is read-only and is never opened for writing by Phase 4.
- Report and API metrics come from Phase 3's governed `all_metrics` and `metric_catalog` views. The five board/report KPIs are M16 Revenue, M17 Net profit, M18 Operating margin, M21 Overdue receivables and M22 Task completion rate.
- Missing values remain missing. A missing value is never silently converted to zero.
- The explorer/API never accept raw SQL from a user. Role authorization and minimum-group suppression are applied in the backend.
- `ADMIN` and `HR` can inspect department aggregates; `EXECUTIVE` sees company-level rows only; `MANAGER` is restricted to the department ID in the trusted server-side assignment. Department breakdowns exclude the company total to reduce simple differencing risk. Do not trust a department ID supplied by a browser.
- Groups smaller than the metric's `minimum_group_size` are suppressed. Where the metric has no threshold, no new threshold is invented. Do not use the explorer for employee-level data.

## Setup (Windows PowerShell)

```powershell
cd path\to\pulseiq-main\phase-4
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set the warehouse path if your directory layout differs:

```powershell
$env:PULSEIQ_DB_PATH = (Resolve-Path ..\phase-3\outputs\pulseiq.duckdb).Path
```

### Monthly report

```powershell
python build_report.py --start 2025-04-01 --end 2026-09-30 --format both
```

Files are written to `phase-4/reports/`. Use `--format pdf`, `--format xlsx`, or `--format both`. `--cutoff` may be supplied as an ISO date; otherwise the latest date found in the selected governed metric data is used.

### KPI explorer

```powershell
streamlit run explorer.py
```

For local role simulation, set environment variables before starting Streamlit:

```powershell
$env:PULSEIQ_ROLE = "EXECUTIVE"  # ADMIN, EXECUTIVE, HR, MANAGER
$env:PULSEIQ_MANAGER_DEPARTMENT = "YOUR_DEPARTMENT_ID"
```

The explorer intentionally refuses to start when `PULSEIQ_AUTH_MODE=production` until a verified SSO adapter is implemented. Do not expose the development mode publicly. The deployment blueprint sets production mode so the app fails closed rather than silently treating every visitor as an executive.

### Metrics API

```powershell
uvicorn api:app --host 127.0.0.1 --port 8000
```

Open `/docs` for interactive OpenAPI documentation.

Example:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/v1/metrics/M16?period=2026-09-01"
```

Send `X-Role` for role selection in local development. In production, set `PULSEIQ_AUTH_MODE=production` and configure a trusted reverse proxy to strip caller-supplied `X-Authenticated-Role` / `X-Authenticated-Department` headers and inject verified claims. The Render blueprint uses production mode. Never trust `X-Role` from a public client.

## Deployment

`Dockerfile` and `render.yaml` provide a reproducible container deployment starting point. The Streamlit app and API are separate services. Mount or publish a refreshed DuckDB file at the configured path; never put credentials in source control. `.github/workflows/monthly-report.yml` demonstrates a scheduled GitHub Actions report build and artifact upload.

**Not performed by this source package:** cloud account provisioning, secrets creation, SSO configuration, DNS/TLS, public deployment, or live URL verification. Those require access to the target hosting account and production identity provider. Do not describe the application as live until the deployment URL has been tested.

### Regenerate the board deck

```powershell
python board_pack.py
```

The editable 8-slide deck is saved to `board_pack/PulseIQ_Board_Pack_Phase4.pptx`.

## Validation

```powershell
python -m pytest -q
python scripts\validate_release.py
```

The tests use temporary SQLite-independent fixtures/mocks for pure policy and formatting logic. End-to-end warehouse queries require the Phase 3 DuckDB database and the pinned DuckDB dependency. Run the full acceptance checklist in `docs/ACCEPTANCE_CHECKLIST.md` on the target Windows machine before tagging a release.

## Release status

This package is a Phase 4 implementation candidate. `v1.0.0-rc1` and `v1.0.0` are Git release tags to create only after local acceptance, privacy tests, deployment checks and final reconciliation pass. No live deployment or release tag is claimed by this package.
