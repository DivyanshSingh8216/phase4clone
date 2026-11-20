# M27 and M28 validation status

The public Phase 4 repository does not contain the Phase 3 DuckDB warehouse or the metric dictionary. Therefore this project does not assert a validated M27 denominator, M28 forecast/actual pairing, or MAPE result.

Run the read-only diagnostic after configuring PULSEIQ_DB_PATH:

python scripts/diagnose_m27_m28.py

For M27, verify the metric definition, eligible population, numerator, denominator, grain, suppression threshold and source view. A count of output rows is not proof that the denominator is large enough or that a department-level percentage is disclosable.

For M28, locate forecast values and actual values at matching entity, metric and period grain. Confirm the forecast horizon and cutoff. If actuals are absent, MAPE is unavailable, not zero. Exclude zero actual denominators or handle them according to the official metric dictionary.

Do not change the source warehouse or Phase 1-3 code during this diagnostic.
