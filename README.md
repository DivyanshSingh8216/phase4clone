# PulseIQ Phase 4 | Release candidate and verification

Phase 4 is an additive layer over the Phase 3 DuckDB warehouse. It must not modify the original `PulseIQ_Dataset.xlsx` or Phase 1-3 source artifacts. Run Phase 4 against a copy or read-only warehouse.

## Repository deliverables

| Task | Included implementation |
|---|---|
| 16 | PDF/XLSX monthly report builder, governed KPI snapshot, supporting Phase 3 evidence tables, privacy filters |
| 17 | Password-gated, executive-only Render dashboard preview with persistent-disk configuration. Full SSO and four-role acceptance remain open |
| 18 | Conservative role/metric policy foundation, privacy helpers and tests. Full role matrix, cascading hierarchy and production acceptance are not claimed |
| 19 | Read-only FastAPI endpoints for five company-grain KPIs, definitions, source lineage and latest available data period |
| 20 | Editable board deck, release notes, release validator and acceptance checklist |

## Important data and access limitations

- The Phase 3 DuckDB file and its companion evidence CSVs are not included in this repository. Set `PULSEIQ_DB_PATH` to the actual warehouse file.
- The five API KPIs (M16, M17, M18, M21, M22) are company-grain. The API currently grants them to EXECUTIVE only. Other roles are denied until an approved metric permission matrix exists.
- The separate `phase4_complete` policy registry is conservative: EXECUTIVE has company-grain grants; HR has M27 department-grain access using the upstream governed view. ADMIN and MANAGER have no KPI grants. This is intentional, not a claim that all four roles have completed self-service access.
- M24 team-grain and M28 forecast accuracy are not exposed as privacy-safe metrics. No team threshold or forecast actuals are invented.
- The Render preview is password-gated and exposes only company-level M16, M17, M18, M21 and M22. It is an executive-only demo, not SSO or the completed four-role Task 18 system. Configure `PULSEIQ_DEMO_PASSWORD` as a Render secret and place the approved Phase 3 DuckDB file on the persistent disk at `/data/pulseiq.duckdb`.
- A scheduled GitHub report build is deliberately manual. It requires the GitHub Actions secret `PULSEIQ_DATA_BUNDLE_BASE64`, containing a base64-encoded ZIP with `pulseiq.duckdb` and the Phase 3 evidence CSVs at the ZIP root.
- No live URL, SSO, phone test, independent-user test or final demo recording is claimed until evidence is collected.

## Windows setup and verification

Run from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PULSEIQ_DB_PATH = "C:\path\to\pulseiq.duckdb"
```

The CSV evidence files used by the report builder must sit in the same directory as the DuckDB file. Preserve the original source workbook. Do not copy over it.

### 1. Automated tests and release-file check

```powershell
python -m pytest -q
python scripts\validate_release.py
```

To verify the three original source workbook hashes, set `PULSEIQ_SOURCE_ROOT` to the folder containing `phase-1`, `phase-2` and `phase-3`, each with `data\PulseIQ_Dataset.xlsx`:

```powershell
$env:PULSEIQ_SOURCE_ROOT = "C:\path\to\PulseIQ-Master-Integration"
python scripts\validate_release.py --require-source-workbooks
```

### 2. Generate the PDF and Excel report

Use the date range present in the Phase 3 warehouse:

```powershell
python build_report.py --start 2025-04-01 --end 2026-09-30 --format both
```

The report prints the latest period actually present in the selected governed KPI rows as its data cutoff. Check the generated files under `reports\`, open both, and reconcile the KPI values and supporting tables to the Phase 3 outputs.

### 3. Verify the API locally

In PowerShell terminal 1:

```powershell
uvicorn api:app --host 127.0.0.1 --port 8000
```

In PowerShell terminal 2:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/v1/metrics -Headers @{ "X-Role" = "EXECUTIVE" }
Invoke-RestMethod "http://127.0.0.1:8000/v1/metrics/M16?period=2026-09-01" -Headers @{ "X-Role" = "EXECUTIVE" }
```

Confirm that an unapproved role is denied:

```powershell
try { Invoke-RestMethod http://127.0.0.1:8000/v1/metrics -Headers @{ "X-Role" = "HR" } } catch { $_.Exception.Response.StatusCode.value__ }
```

Expected: HTTP 403 for HR on this API catalogue. Also verify an unknown metric returns 404. Open `http://127.0.0.1:8000/docs` for OpenAPI documentation.

### 4. Deploy the executive preview on Render

Follow [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). The Render Blueprint creates a password-gated executive-only dashboard and persistent disk. Set `PULSEIQ_DEMO_PASSWORD` as a secret, then place the approved Phase 3 DuckDB file at `/data/pulseiq.duckdb`. Do not commit the database or password. This preview does not satisfy SSO or four-role acceptance.

### 5. Verify the container build

Install Docker Desktop and ensure the Phase 3 database is available separately. Build from the repository root:

```powershell
docker build -t pulseiq-phase4 .
```

The image does not embed the private warehouse. Run it with a read-only mount of the approved database at `/data/pulseiq.duckdb` and production identity must remain disabled until a trusted authentication proxy is configured.

## Production and submission acceptance gates

Do not mark the project fully accepted or tag `v1.0.0` until all of these are evidenced:

1. Official Task 18 starter files (demo users, metric dictionary and authoritative hierarchy) are reconciled with the committed policy.
2. Data owner and HR/privacy owner approve the complete role/metric/dimension matrix, including any team-level thresholds.
3. SSO/OIDC or a trusted identity proxy is configured and caller-supplied identity headers are stripped.
4. A persistent warehouse and approved refresh source are configured; refresh timestamp and failure alert are tested.
5. API and dashboard are deployed, live URL is recorded, and phone plus independent-user tests pass.
6. All four role journeys and adversarial privacy tests pass on the deployed app, including manipulation, differencing and small-group boundaries.
7. PDF/XLSX outputs and every board slide are reconciled against Phase 3 outputs; missing values remain missing, never zero-filled.
8. Phase 1-3 source workbook hashes, Phase 3 data-quality/reconciliation checks, latest CI run and final demo evidence are recorded.

The repository contains implementation and reproducible local checks, but the external production gates above require operator credentials and source approvals. Do not present them as complete without evidence.
