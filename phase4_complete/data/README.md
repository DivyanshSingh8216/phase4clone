# Local Phase 3 warehouse

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\repair_metrics.py --download-db --validate
```

The verified Phase 3 warehouse is downloaded here as `pulseiq.duckdb`.
The binary is intentionally ignored by Git; do not commit the warehouse or
employee-level source data. The application opens it read-only.
