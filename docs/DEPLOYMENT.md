# Deployment guide

## Fast hosted preview: Render

The repository now includes a Render Blueprint for a **password-gated, executive-only dashboard preview**. It is deliberately narrower than the final four-role production system.

1. Push/pull the latest `phase4-complete` branch and open the repository in Render.
2. Choose **New + → Blueprint**, select this repository and branch, then apply `render.yaml`.
3. In the created `pulseiq-kpi-explorer` service, add the secret environment variable `PULSEIQ_DEMO_PASSWORD`. Use a strong, unique password and do not commit it.
4. Wait for the Docker build and deployment to finish. Confirm the health check `/_stcore/health` passes.
5. Open the public service URL and sign in with the demo password.
6. If the warehouse is not installed, use the in-app uploader to upload the approved Phase 3 `pulseiq.duckdb` file. The app validates that it contains `all_metrics` and `metric_catalog` before saving it to `/data/pulseiq.duckdb` on the persistent disk.
7. Do not upload the original source workbook and do not put the database in Git.
8. After installation, verify M16, M17, M18, M21 and M22.

The Render Blueprint requests a Starter web service and a 1 GB persistent disk. Persistent disks require a paid Render service. The database is intentionally not packaged in the Docker image. If Render Shell is unavailable on the selected plan, use an approved secure transfer method to place the database on the mounted disk.

## What this preview does and does not prove

- It exposes only company-grain M16, M17, M18, M21 and M22.
- A shared demo password gates access. This is suitable for a controlled demonstration, **not SSO, not individual user authentication, and not the four-role Task 18 acceptance test**.
- No HR, ADMIN or MANAGER role switching is exposed in this public preview.
- The API is not part of this single-service preview. Keep the API private until verified identity claims and a trusted proxy are configured.
- The preview uses a fixed Phase 3 snapshot. It does not implement automated warehouse refresh, alerting or freshness orchestration.

## Local container check

Run from the repository root:

```powershell
docker build -t pulseiq-phase4 .
docker run --rm -p 8501:8501 -e PULSEIQ_DEMO_PASSWORD="local-demo-password" -e PULSEIQ_DB_PATH=/data/pulseiq.duckdb -v "C:\\path\\to\\outputs:/data:ro" pulseiq-phase4 streamlit run explorer.py --server.address 0.0.0.0 --server.port 8501
```

The mounted folder must contain the approved `pulseiq.duckdb`. The source workbook remains untouched.

## API deployment gate

Do not expose `api.py` publicly until a trusted authentication proxy or OIDC integration is configured to verify identity and strip caller-supplied `X-Authenticated-Role` and `X-Authenticated-Department` headers. The API's current production headers are trusted-proxy claims, not self-authenticating credentials.

## Full production acceptance still requires

1. Approved SSO/OIDC and role-to-user mapping.
2. Owner-approved four-role metric/dimension permissions and authoritative department/team hierarchy.
3. Privacy tests against small groups, differencing and adversarial filters.
4. Approved refresh pipeline, persistent warehouse, timestamp and failure alerts.
5. Separate API deployment behind verified identity, with API docs and lineage tests.
6. Live URL, phone and independent-user test evidence.
7. Reconciled PDF/XLSX, board deck, final challenge evidence and release tag.
