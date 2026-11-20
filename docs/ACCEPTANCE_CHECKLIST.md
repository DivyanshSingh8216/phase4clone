# Phase 4 acceptance checklist

## Day 16 | Monthly reporting
- [ ] Run report for the complete source period and a single-month period.
- [ ] Confirm both PDF and XLSX are created.
- [ ] Confirm report start, end and data cutoff are printed.
- [ ] Tie KPI values to `all_metrics` and the report's five evidence tables to Phase 3 outputs.
- [ ] Confirm missing values remain blank/Not available, not zero.
- [ ] Open the PDF and Excel workbook on Windows.

## Day 17 | Deployment
- [ ] Build Docker image from repository root: `docker build -f phase-4/Dockerfile -t pulseiq-phase4 .`
- [ ] Verify API `/health` and `/docs`.
- [ ] Verify Streamlit explorer on the intended host/port.
- [ ] Configure persistent warehouse refresh, secrets, TLS, DNS and monitoring.
- [ ] Verify a real live URL and record it in the release evidence.
- [ ] Configure identity provider; do not expose `X-Role` as public authorization.

## Day 18 | Privacy
- [ ] Confirm EXECUTIVE receives company rows only.
- [ ] Confirm MANAGER cannot request another department.
- [ ] Confirm HR/ADMIN department access is authenticated.
- [ ] Confirm the source metric view suppresses groups below its declared threshold.
- [ ] Attempt URL/query manipulation, direct API calls and department-ID substitution.
- [ ] Test differencing risk across time periods and overlapping groups before wider access.
- [ ] Confirm no employee identifiers or row-level attrition-risk records are exposed.

## Day 19 | API and lineage
- [ ] Test M16, M17, M18, M21 and M22 endpoints.
- [ ] Confirm each response includes definition, source, lineage, last refresh and values.
- [ ] Confirm unknown metrics return 404 and unauthorized access returns 403.
- [ ] Confirm API uses read-only DuckDB connections.
- [ ] Confirm `/docs` accurately describes endpoints.

## Day 20 | Handover and release
- [ ] Re-run Phase 3 pipeline and tests on a copy/approved workspace.
- [ ] Review DQ and all reconciliation outputs.
- [ ] Refresh monthly report and board-pack evidence.
- [ ] Confirm original `PulseIQ_Dataset.xlsx` SHA256 is unchanged.
- [ ] Run `python -m pytest -q`.
- [ ] Record deployment URL, build ID, data cutoff, test results and owners.
- [ ] Create `v1.0.0-rc1` only after acceptance.
- [ ] Create `v1.0.0` only after RC defects are closed and production sign-off is recorded.
