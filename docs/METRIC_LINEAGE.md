# PulseIQ API metric lineage

| API metric | Governed definition | Source | Transformation | Consumer |
|---|---|---|---|---|
| M16 | Revenue booked in ledger, accounts 4001–4004 | `warehouse.fact_ledger` | ETL → `v_m16_revenue` → `all_metrics` | Profit & Loss, Executive Scorecard, API |
| M17 | Net profit as defined by the Phase 3 metric dictionary | `warehouse.fact_ledger` | ETL → `v_m17_net_profit` → `all_metrics` | Profit & Loss, Executive Scorecard, API |
| M18 | Net profit / revenue × 100 | `warehouse.fact_ledger` via governed M16/M17 views | ETL → `v_m18_operating_margin` → `all_metrics` | Executive Scorecard, API |
| M21 | Past-due unpaid invoice balance | `warehouse.fact_invoice` | ETL → `v_m21_overdue_receivables` → `all_metrics` | Receivables & Cash, Executive Scorecard, API |
| M22 | Done tasks / non-cancelled tasks × 100 | `warehouse.fact_task` | ETL → `v_m22_task_completion` → `all_metrics` | Executive Scorecard, API |

## Freshness

The API calculates `last_refresh` as the maximum `period` available for the requested metric in `all_metrics`. This is the latest data period, not the wall-clock time at which the ETL job last ran. A production deployment should additionally persist an ETL run timestamp and publish it as `refreshed_at`.

## Data flow

```text
PulseIQ_Dataset.xlsx (read-only)
    -> Phase 1 ingestion and validation
    -> DuckDB warehouse tables
    -> governed SQL metric views
    -> all_metrics + metric_catalog
       -> Streamlit dashboards
       -> monthly PDF/XLSX report
       -> FastAPI /v1/metrics/{metric_id}
```

Metric definitions and caveats are sourced from the Phase 3 `metric_catalog` view and `outputs/metric_catalog.csv`. The API exposes five metrics selected for the Phase 4 release. It does not expose employee-level rows.
