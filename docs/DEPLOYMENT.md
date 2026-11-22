# Deployment and production gates

## Build context

The Dockerfile is at the repository root. Build from the root directory:

```powershell
docker build -t pulseiq-phase4 .
```

The image contains the pinned Python dependencies, FastAPI API and local Streamlit entry point. It deliberately does not copy the Phase 3 DuckDB file or employee data into the image. At runtime, mount an approved, read-only warehouse at `/data/pulseiq.duckdb`. Set `PULSEIQ_DB_PATH` if the mount differs.

The Render Blueprint is a deployment template, not evidence of a live deployment. Before using it, configure persistent storage for the database, trusted identity, secret management, TLS, logging and a real data refresh process. The explorer intentionally refuses production mode until its SSO adapter is implemented.

## Authentication

- Never publish the development `X-Role` header or environment-based Streamlit role simulation.
- API production mode accepts role and department claims only from a trusted proxy that strips caller-supplied copies and injects verified claims.
- The currently exposed company-grain API metrics are restricted to EXECUTIVE. Other roles receive HTTP 403 until approved grants are implemented.
- Streamlit production access remains blocked until verified SSO/OIDC is integrated. Do not bypass this guard.

## Data refresh

The supplied Phase 3 warehouse is a fixed snapshot. A scheduled report is not a warehouse refresh. A real refresh requires an approved upstream feed, credentials, data contract, ingestion schedule, durable storage, refresh timestamp and failure alert.

The GitHub Actions monthly-report workflow is manual and requires the repository secret `PULSEIQ_DATA_BUNDLE_BASE64`. Its value must be a base64-encoded ZIP containing `pulseiq.duckdb` and the Phase 3 evidence CSVs at the archive root. The workflow fails clearly if the secret is absent. Do not commit the data bundle or put it in public artifacts.

## External acceptance evidence

Cloud account provisioning, persistent storage, SSO, secrets, DNS/TLS, public URL, live phone test and independent-user test are not completed by repository commits. Record actual evidence for each before declaring production acceptance.
