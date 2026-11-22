# Submission checklist

- [ ] Create a clean Python 3.11 environment and install root requirements.
- [ ] Run the one-command warehouse bootstrap and metric validation.
- [ ] Review `reports/metric_validation.csv`; resolve every REVIEW/RECONCILE item with the data owner.
- [ ] Run `pytest -q` and retain the actual terminal output as evidence.
- [ ] Verify ADMIN, HR, MANAGER and EXECUTIVE demo access locally.
- [ ] Confirm M21/M27 are labeled as snapshots where only one period is available.
- [ ] Confirm M28 is unavailable rather than displayed as zero.
- [ ] Verify production OIDC and hosted warehouse secrets before deployment.
- [ ] Attach the final board pack and any required screenshots/recording.
- [ ] Confirm no secrets, local environments, source workbooks or DuckDB binaries are committed.

The checklist is not an acceptance claim. Mark items complete only after the
corresponding checks have actually been run and evidence retained.
