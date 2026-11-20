# PulseIQ Board Pack | Evidence-backed slide plan

**Reporting window:** April 2025 to September 2026 (18 monthly periods), based on the Phase 3 packaged outputs. The report cutoff must be restated on the final exported pack.

This is an evidence-backed content outline for an 8-slide board presentation. Figures below are transcribed/calculated from Phase 3 output CSVs. They are not a substitute for refreshing the warehouse and re-running reconciliations before board circulation.

## Slide 1 | Executive overview
- PulseIQ provides a joined view of finance, cash, workforce cost, receivables and operating delivery.
- The Phase 3 P&L output totals ₹1,260.93m total income, ₹1,036.26m expenses and ₹224.67m net profit across the 18-month period.
- Recommendation: use the governed scorecard as the monthly review entry point, with detailed pages for exceptions.

## Slide 2 | Revenue and profitability
- 18-month operating revenue: ₹1,259.20m; other income: ₹1.73m; total income: ₹1,260.93m.
- 18-month net profit: ₹224.67m.
- September 2026: total income ₹80.60m, expenses ₹65.62m, net profit ₹14.99m, net margin 18.59%.
- Recommendation: review month-on-month margin movement and require tie-out review before external financial reporting.

## Slide 3 | Cash conversion and liquidity view
- Phase 3 cash-flow output totals: cash-in ₹1,419.35m, cash-out ₹185.83m, net cash flow ₹1,233.52m over the packaged 18 months.
- September 2026 cash-in ₹84.33m, cash-out ₹8.90m, net cash flow ₹75.44m.
- These are derived cash movement summaries, not a bank statement or audited cash balance.
- Recommendation: reconcile cash-flow totals to source payment registers and bank statements before treasury decisions.

## Slide 4 | Receivables ageing
- Open receivables ageing output totals ₹139.39m.
- 0–30 days: ₹134.42m across 59 invoices.
- 61–90 days: ₹1.94m across 1 invoice.
- 90+ days: ₹3.04m across 2 invoices.
- The 90+ bucket is a clear collections priority; total ageing is not synonymous with overdue receivables.
- Recommendation: assign owners and collection dates to the three invoices in the 61+ day buckets.

## Slide 5 | Workforce cost and reconciliation
- Department/month joined payroll employer cost reconciles to source payroll: ₹861,586,392.42 vs ₹861,586,392.42 (floating-point representation differs by negligible sub-paise precision).
- Overtime cost: ₹3,024,619.28 in both source and joined output.
- Approved leave days: 7,276 in both source and joined output.
- Recommendation: preserve the grain audit and reconciliation as a release gate for department-level workforce reporting.

## Slide 6 | Anomaly signals and investigation queue
- The anomaly output contains 405 flagged records across the listed anomaly groups, with estimated money-at-risk totals of ₹31.42m.
- 221 flagged records have no money-at-risk value populated.
- Statistical outlier group contributes ₹19.43m; gross-above-norm contributes ₹9.42m.
- These are model/rule-based investigation signals, not confirmed loss, fraud or accounting misstatement.
- Recommendation: triage by amount, verify source records, and document disposition before escalating.

## Slide 7 | Forecast readiness
- Phase 3 forecast output contains 72 forecast rows, all trained through September 2026.
- The packaged validation summary has zero rows with actuals and zero rows with forecast error.
- Recommendation: label current forecasts as forward-looking scenarios only; begin back-testing when observed periods arrive.

## Slide 8 | Decisions and next actions
1. Finance: sign off monthly P&L and cash reconciliation.
2. Collections: assign the three 61+ day receivables.
3. HR/Finance: retain the payroll-to-workforce reconciliation check.
4. Risk owners: disposition high-value anomaly signals; do not treat model flags as confirmed losses.
5. Analytics owner: establish forecast back-testing once actuals are available.
6. Technology owner: complete SSO, hosting, secrets, refresh monitoring and production acceptance before public release.

## Evidence caveats
- The Phase 3 Day 13 reference comparison contains 5 `INVESTIGATE` records, 2,569 `MATCH` records and 9,009 `ACTUAL_ONLY` records. `ACTUAL_ONLY` means outside the supplied reference coverage, not a failed join.
- The packaged Phase 3 forecast validation summary is 72 forecast rows, 0 rows with actuals and 0 rows with error.
- The anomaly output groups records by type and explanation. Counts are output-row aggregates; the anomaly flags are not a validated fraud label.
