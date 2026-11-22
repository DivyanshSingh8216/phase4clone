# Demo fixtures and Phase 3 source audit

## Demo identities

These four identities are fabricated test fixtures, not real employees or production credentials:
- demo_admin: ADMIN, company-wide test scope.
- demo_hr: HR, company-wide test scope; metric policy still limits metrics and dimensions.
- demo_manager_d01: MANAGER, assigned to D01 Engineering and teams T01/T02 only.
- demo_executive: EXECUTIVE, company-wide executive aggregate scope.

The user identities are fabricated. D01/T01/T02 are actual identifiers in the supplied Phase 3 workbook's dim_department and dim_team sheets. Do not use these fixtures in production. Production must use verified SSO claims.

## Source archive inspected

Source: PulseIQ_Phase3_Complete (2)(1).zip
- Official dictionary: outputs/metric_catalog.csv and workbook sheet metric_dictionary.
- Warehouse: outputs/pulseiq.duckdb (included in archive).
- Star schema: docs/star_schema.md.
- Governed metric SQL: sql/metric_views.sql.
- Department and team source dimensions: workbook sheets dim_department and dim_team.
- ETL row summary: outputs/etl_row_summary.csv.

The ETL summary records 11 departments, 16 teams, 430 attrition-risk rows, 72 forecast rows, and 891 headcount-month rows loaded, with source/load counts reconciling for those sheets.

## Verified organisation mapping

The workbook's dim_team sheet maps:
- D01 Engineering: T01 Platform Core, T02 Payments & Billing, T03 Mobile Apps, T04 QA Automation, T05 DevOps & Reliability.
- D02 Product & Design: T06 Product Squad, T07 Design Systems.
- D03 Data & AI: T08 Data Platform, T09 ML Services, T10 Analytics & BI.
- D04 Sales: T16 Sales Enablement.
- D05 Marketing: T11 Growth Marketing.
- D06 Customer Support: T12 Support Tooling.
- D07 Human Resources: T13 HR Systems.
- D08 Finance & Accounts: T14 Finance Automation.
- D09 Operations & IT: T15 Internal IT.
- D00 Executive Office and D10 Legal & Compliance have no teams in the supplied dim_team mapping.

## M27 source finding

The metric dictionary defines M27 as department-level high-risk share, formula COUNT(risk_band = High) / COUNT(*), point-in-time, minimum group size 10, and says to show by group only and never rank named people.

The Phase 3 SQL view v_m27_high_risk_share groups fact_attrition_risk by as_of_date and department_id, calculates the percentage, and applies HAVING COUNT(DISTINCT employee_id) >= 10.

Independent aggregation of the supplied workbook's fact_attrition_risk confirms:
- 2026-09-30 department groups: D01 163, D02 25, D03 50, D04 44, D05 12, D06 58, D07 19, D08 16, D09 28, D10 10.
- D00 has no risk rows.
- 2026-03-31 records include only D01=3, D03=1 and D04=1, all below threshold and correctly suppressed by the governed view.
- For 2026-09-30, high-risk shares are based on those department populations. Do not publish numerator or employee-level detail.

This provides positive and negative suppression test cases: September groups meet the minimum; March groups do not.

## M28 source finding

The dictionary defines M28 as department/month forecast error (MAPE), requiring actual headcount for each forecast month.

The Phase 3 SQL view joins fact_forecast to fact_headcount_monthly on forecast month and department, then calculates MAPE only where actual exists and is nonzero, with HAVING MAX(actual) >= 10.

The supplied workbook contains 72 forecasts, all for October 2026 through March 2027 (six months × 12 scopes: ALL plus D01-D10). The supplied actual headcount data ends in September 2026. Independent key matching found zero forecast-month/department matches. Therefore M28 correctly has no observations in this snapshot: all forecasts are future periods with no actuals yet. This is not a dashboard chart bug and must not be fixed by fabricating actuals or forecast errors.

When actuals arrive for those periods, the refresh pipeline should rebuild M28 and the dashboard should display newly available matched periods.

## Important implementation caveat

The official all_metrics schema exposes metric_id, metric_name, period, department_id, value, unit, min_group_size and caveat. It does not expose a universal group-size count or team_id column. M27's SQL view enforces the threshold before publication but does not expose the count. The explorer must not guess group-size fields or treat department_id as team_id except for the explicitly documented M24 legacy mapping. A hierarchy-aware explorer needs metric-specific query adapters / governed views.
