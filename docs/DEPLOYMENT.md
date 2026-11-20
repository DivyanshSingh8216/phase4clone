# Deployment notes and hosting decision

## Candidate hosting options

| Option | Fit for this repository | Important checks before choosing |
|---|---|---|
| Streamlit Community Cloud | Fastest low-ops demo for a Streamlit-only dashboard | Private repository access, resource limits, sleep/availability behaviour, secrets, file-size and persistent-storage constraints |
| Render | Supports separate containerized API and Streamlit services from one repository | Paid instance cost, persistent disk requirements, service sleep policy, region, environment variables and trusted auth proxy |
| Railway | Convenient container deployment and managed services | Current usage pricing, persistent volume cost, egress, deployment limits and identity integration |
| AWS App Runner / ECS | More control for a production architecture | IAM, networking, load balancing, secrets, logs, database/storage design and ongoing operational cost |

No current plan prices are hard-coded here because hosting prices and limits change. Verify current provider pricing and service constraints before procurement.

## Selected implementation starting point

The repository includes a Render Blueprint and a Dockerfile. The Docker build context is the repository root:

```powershell
docker build -f phase-4/Dockerfile -t pulseiq-phase4 .
docker run --rm -p 8000:8000 pulseiq-phase4
```

The API is the default container command. Run the explorer locally with:

```powershell
docker run --rm -p 8501:8501 --entrypoint streamlit pulseiq-phase4 run explorer.py --server.address 0.0.0.0 --server.port 8501
```

The Docker image copies the Phase 3 DuckDB file into the image. That makes the image reproducible but does not provide a live refresh mechanism. A refreshed warehouse requires a new build/deployment or a separately designed persistent-volume/data-publishing process.

## Security gates

- Do not publish the API directly with development `X-Role` authorization.
- In production API mode, a trusted authentication proxy must strip incoming `X-Authenticated-Role` and `X-Authenticated-Department` headers and inject verified identity claims.
- The Streamlit explorer fails closed in production mode until an SSO adapter is connected.
- Store credentials in the host's secret manager, not in GitHub variables or committed files.
- Use TLS, least-privilege service identities, logs and access monitoring.
- Do not expose the DuckDB file as a public downloadable asset.

## Refresh status

The Phase 3 workbook is a fixed supplied dataset. Phase 4 can generate recurring reports from the committed warehouse, but this is not equivalent to receiving fresh operational data each month. A real production refresh requires an approved live source feed, credentials, data contracts, an ingestion schedule, a refresh timestamp and a failure alert. Those inputs are not present in this ZIP, so no fake refresh job is included.
