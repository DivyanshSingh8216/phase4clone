# Task 17 - Hosting and refresh decision

## Options

| Platform | Entry cost / free option | Sleep and storage behaviour | Fit |
|---|---|---|---|
| Streamlit Community Cloud | Free community hosting | Apps sleep after 12 hours without traffic; published resource limits are approximate and can change. No managed persistent database is included. | Fastest public portfolio demo for non-sensitive, small aggregate data. Not suitable for confidential role-based HR data without a separate secure architecture. |
| Render | Free web service; paid web compute currently starts at USD 7/month for 0.5 CPU / 512 MB | Free web services spin down after 15 idle minutes, wake in about a minute, and have ephemeral filesystems. Persistent disks require paid compute. | Existing Docker/Render work makes migration straightforward. Paid service plus persistent storage is the more credible path for an always-on dashboard. |
| Railway | Usage-based paid service; trial/plan terms vary | Persistent volumes and service sleep depend on plan/configuration. | Viable alternative, but requires a separate cost and storage validation before selection. |

Prices and limits are provider-published and may change. Re-check the provider pricing pages before provisioning.

Sources:
- Streamlit Community Cloud resource and hibernation documentation: https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- Streamlit Community Cloud status and limitations: https://docs.streamlit.io/deploy/streamlit-community-cloud/status
- Render free service limitations: https://render.com/docs/free
- Render pricing: https://render.com/pricing

## Decision

Recommended target: Render paid web service for the dashboard, with a separately managed persistent data store or hosted database. The existing project already contains a Render/Docker starting point. A free Render instance is suitable for a temporary demonstration only: it sleeps after 15 minutes and loses local filesystem changes on restart/redeploy. Streamlit Community Cloud is simpler for an anonymous, non-sensitive demo but does not solve the production identity and data-governance requirements.

Do not publish employee-level or confidential HR data to an anonymous public app. Public URL reachability and anonymous data access are different requirements.

## 200 MB publishing decision

Do not upload the original workbook or an entire warehouse by default. First measure the actual database and each candidate export. Publish only governed aggregate tables/views required by the approved dashboard metrics, plus metric catalog, freshness metadata and the authoritative organisation mapping required for navigation. Exclude raw employee records, credentials, source workbook and unused staging tables. Retain the source warehouse in its controlled environment.

No data-size measurement is claimed in this repository because the Phase 3 DuckDB file was not committed to this public repository.

## Refresh design

The existing monthly-report workflow is not a dashboard warehouse refresh. A real refresh must:

1. Obtain the approved upstream data extract or source snapshot.
2. Run the existing Phase 1/2/3 ingestion and validation process in a controlled pipeline.
3. Build the governed metric aggregates.
4. Run row-count, reconciliation, schema and privacy checks.
5. Publish a versioned aggregate database/object atomically.
6. Update a freshness manifest containing source cutoff, refresh timestamp, row counts and validation status.
7. Let the dashboard read the current published version.
8. Preserve the previous good version if any validation or publish step fails.

Schedule: monthly at 05:00 UTC on the 2nd day, matching the existing report schedule, unless the business data owner approves a different cadence. This schedule is a proposed target, not an operational refresh that has been executed.

## External prerequisites

A real source-feed location, credentials, GitHub secrets, hosting account, production identity provider, and approved role/dimension policy are required. Never put secrets in Git or bake them into the Docker image.
