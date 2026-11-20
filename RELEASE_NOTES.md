# PulseIQ Phase 4 Release Notes

## 1.0.0-rc1 candidate

### Added
- Monthly PDF and Excel report builder with explicit reporting dates and data cutoff.
- Five governed report KPIs: M16, M17, M18, M21 and M22.
- Five supporting Phase 3 evidence tables: P&L, expense categories, cash flow, receivables ageing and anomaly signals.
- Role-aware aggregate KPI explorer with server-side department scoping.
- Read-only FastAPI endpoints for metric catalogue, metric values and lineage.
- Data freshness metadata in API responses.
- Docker and Render deployment starting points.
- Scheduled GitHub Actions report generation and artifact retention.
- Acceptance checklist, privacy policy tests, board-pack evidence notes and handover.

### Controls and limitations
- No employee-level data is exposed by Phase 4.
- The explorer uses the minimum-group suppression rules already encoded in the Phase 3 governed metric views; it does not invent a replacement threshold.
- The `X-Role` API header and environment-based Streamlit role are local development adapters only. Production API mode accepts identity headers only from a trusted proxy that strips caller copies; Streamlit fails closed until a verified SSO adapter is connected.
- Cloud deployment, SSO, secrets, DNS, TLS and live URL checks require operator access and are not performed by this repository change.
- The original Excel workbook and Phase 1–3 files are not modified.
- Forecast validation remains pending because the Phase 3 evidence reports 72 forecast rows and zero rows with actuals.

### Release gate
Do not tag `v1.0.0-rc1` or `v1.0.0` until the acceptance checklist passes on the target machine, all privacy tests pass, the live deployment is verified, and source-to-report reconciliation is signed off.
