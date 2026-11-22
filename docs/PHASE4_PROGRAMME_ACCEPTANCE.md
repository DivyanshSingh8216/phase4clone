# Phase 4 programme acceptance status

Repository: https://github.com/DivyanshSingh8216/phase4clone
Working branch: phase4-complete
Programme release tag required: phase-4
Final software release tag required by task sheet: v1.0.0

This document distinguishes repository implementation from external acceptance evidence. A code file is not proof that a public service is deployed or usable.

| Task | Repository evidence | Status |
|---|---|---|
| 16 Report builder | build_report.py, pinned root dependencies, monthly GitHub Actions workflow | Implemented in repo; scheduled run and clean-machine artifact check remain to verify |
| 17 Live dashboard | streamlit_app.py, deployment guide, hosted DuckDB checksum validation | Not complete until deployed URL, hosted snapshot, scheduled refresh, phone test and independent-user test are recorded |
| 18 KPI explorer/privacy | OIDC mapping, fail-closed policy registry, small-group guard and tests | Partial; current grants are EXECUTIVE five company KPIs and HR M27 department aggregates. ADMIN/MANAGER have no KPI grants |
| 19 API/lineage | api.py, docs/API_LINEAGE.md, five metric endpoints and lineage routes | Repository implementation present; live API deployment and live responses remain outstanding |
| 20 Board pack/handover | board_pack.py and RELEASE_NOTES.md | Generator present; live reconciliation, deck review, demo, final challenge and final release tag remain outstanding |

## Data and governance limits
- Preserve original PulseIQ_Dataset.xlsx and Phase 1-3 outputs unchanged.
- Department/team hierarchy mappings have not been verified against an authoritative organisation source. Do not use them to grant real access until validated.
- The manager demo assignment is sample configuration, not verified employee access.
- M28 forecast error cannot be calculated because no forecast periods have matching actuals in the available Phase 3 evidence.
- Latest metric period is not proof of ETL execution time.
- Never publish employee-level data, secrets, signed object URLs or the private DuckDB file in the repository.

## External actions still required
1. Configure Streamlit Community Cloud and a real OIDC identity provider.
2. Host the approved DuckDB snapshot in private HTTPS storage and set its SHA-256 in Streamlit secrets.
3. Configure automated refresh/publish from the approved upstream Phase 3 process. The monthly report workflow builds reports from a supplied bundle; it does not refresh the warehouse.
4. Validate the organisation hierarchy and approve the metric/role/dimension matrix with the data owner.
5. Deploy FastAPI behind verified identity claims.
6. Run public-link, phone, stranger-usability, role and small-group break-it tests; capture evidence.
7. Re-run live reconciliation and data-quality checks, review the board pack, record the five-minute demo and verify its unlisted link in a private browser window.
8. After evidence passes, create and push tags phase-4 and v1.0.0.

## Submission packaging
- Programme site: 2-3 page Phase 4 report PDF with task status, evidence, test outputs and lessons.
- Google Form: consolidated 8-12 page report PDF, public dashboard link and five-minute demo video link.
- Do not upload the consolidated report to the programme site if the programme instructions specify Google Form only.