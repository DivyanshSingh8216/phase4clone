# PulseIQ Phase 4 API and lineage reference

This reference documents the five metrics currently exposed by FastAPI. The service reads the Phase 3 DuckDB warehouse in read-only mode.

## Endpoints
- GET /health: service and warehouse availability.
- GET /v1/metrics: authorised metric catalogue.
- GET /v1/metrics/{metric_id}: metric values and metadata.
- GET /v1/lineage/{metric_id}: metric lineage.
- /docs: interactive OpenAPI documentation when the service is running.

Production authentication is fail-closed by default. A production deployment must use a trusted identity proxy that strips caller-supplied X-Authenticated-Role and X-Authenticated-Department headers and injects verified claims. Never expose the development X-Role adapter publicly.

## Example requests

    curl https://YOUR-API-HOST/health
    curl -H "X-Authenticated-Role: EXECUTIVE" https://YOUR-API-HOST/v1/metrics
    curl -H "X-Authenticated-Role: EXECUTIVE" https://YOUR-API-HOST/v1/metrics/M16
    curl https://YOUR-API-HOST/v1/lineage/M16

The authenticated headers are illustrative. They are trustworthy only when injected by the configured identity proxy.

## Five metric lineage paths

### M16 Revenue
- Definition: income booked in the ledger, accounts 4001-4004.
- Source: warehouse.fact_ledger.
- Metric view: v_m16_revenue.
- Warehouse output: all_metrics.
- Dashboard: Phase 3 Profit & Loss and Executive Scorecard.

    Raw ledger rows -> Phase 1 ingestion and validation -> warehouse.fact_ledger -> v_m16_revenue -> all_metrics -> FastAPI and executive dashboard

### M17 Net profit
- Definition: revenue less expenses, including interest income as defined by the metric dictionary.
- Source: warehouse.fact_ledger.
- Metric view: v_m17_net_profit.
- Warehouse output: all_metrics.
- Dashboard: Phase 3 Profit & Loss and Executive Scorecard.

    Raw ledger rows -> Phase 1 ingestion and validation -> warehouse.fact_ledger -> v_m17_net_profit -> all_metrics -> FastAPI and executive dashboard

### M18 Operating margin
- Definition: net profit as a share of revenue.
- Inputs: v_m17_net_profit and v_m16_revenue.
- Metric view: v_m18_operating_margin.
- Warehouse output: all_metrics.
- Dashboard: Phase 3 Executive Scorecard.

    Raw ledger rows -> Phase 1 ingestion and validation -> warehouse.fact_ledger -> v_m16_revenue + v_m17_net_profit -> v_m18_operating_margin -> all_metrics -> FastAPI and executive dashboard

### M21 Overdue receivables
- Definition: unpaid invoice balance past due date at the report date.
- Source: warehouse.fact_invoice.
- Metric view: v_m21_overdue_receivables.
- Warehouse output: all_metrics.
- Dashboard: Phase 3 Receivables & Cash and Executive Scorecard.

    Raw invoice rows -> Phase 1 ingestion and validation -> warehouse.fact_invoice -> v_m21_overdue_receivables -> all_metrics -> FastAPI and executive dashboard

### M22 Task completion
- Definition: tasks done divided by tasks planned in the sprint, excluding cancelled tasks.
- Source: warehouse.fact_task.
- Metric view: v_m22_task_completion.
- Warehouse output: all_metrics.
- Dashboard: Phase 3 Executive Scorecard.

    Raw task rows -> Phase 1 ingestion and validation -> warehouse.fact_task -> v_m22_task_completion -> all_metrics -> FastAPI and executive dashboard

## Response and freshness contract

A metric response includes metric ID, definition, source, lineage description, dashboard destination, last_refresh, returned row count and data rows. Row data includes metric catalogue definition, formula, source table, unit and caveat where present.

last_refresh is the maximum metric period present for that metric. It is a data-period indicator, not proof of an ETL execution timestamp.

## Change impact

| Changed source | Metrics requiring review |
|---|---|
| warehouse.fact_ledger or account mapping | M16, M17, M18 |
| warehouse.fact_invoice due date, paid status or balance | M21 |
| warehouse.fact_task status or cancellation logic | M22 |
| all_metrics schema or period/grain conventions | All five |
| metric_catalog definitions, formulas or units | All affected metrics |

Before publishing a source schema change, rerun Phase 3 ETL, reconciliation and data-quality checks, then compare metric values and API responses. Confirm the documented source-to-view names against the deployed Phase 3 SQL when changing ETL logic.