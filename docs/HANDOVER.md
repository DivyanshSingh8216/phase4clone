# PulseIQ Phase 4 handover

## Five-minute demo sequence

1. **30 seconds:** introduce PulseIQ and the Phase 1–3 governed DuckDB foundation.
2. **60 seconds:** run `build_report.py` for a selected date range and open the PDF/XLSX.
3. **60 seconds:** launch the KPI explorer and show the company-level Executive view, then demonstrate a Manager's fixed department scope using local development settings.
4. **60 seconds:** open FastAPI `/docs`, request M16 and show the definition, source, lineage and latest period.
5. **60 seconds:** open the editable board pack and discuss the receivables, payroll reconciliation and anomaly caveats.
6. **30 seconds:** close with production gates: SSO, trusted proxy, live source refresh, deployment URL and acceptance sign-off.

## Local run commands

```powershell
cd phase-4
python -m pip install -r requirements.txt
python build_report.py --start 2025-04-01 --end 2026-09-30 --format both
python -m pytest -q
uvicorn api:app --reload
```

In a second terminal:

```powershell
cd phase-4
$env:PULSEIQ_ROLE = "EXECUTIVE"
streamlit run explorer.py
```

## Independent final challenge

Use a separate Git branch and do not modify the original workbook. Suggested challenge: add a second API metric selected by the reviewer, including its governed definition, lineage, permission rule, tests and a report/export tie-out. The reviewer should choose the metric only after the branch is created so the work demonstrates independent implementation rather than a prebuilt answer.

## Handover record to complete at production sign-off

- Release commit:
- Release tag:
- API URL:
- Dashboard URL:
- Data cutoff:
- Warehouse refresh timestamp:
- Identity provider / proxy owner:
- Data owner:
- Test run and results:
- Open risks:
- Approval:
