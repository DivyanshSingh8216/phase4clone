# PulseIQ Phase 4 Complete

## Task 18: Self-service KPI explorer

Run the existing Streamlit entry point from the repository root. The KPI Explorer reads the existing Phase 3 `metric_catalog` and `all_metrics` views. It does not recreate or overwrite the 28 Phase 3 metrics.

### Role access

| Role | Available metrics | Data scope |
|---|---|---|
| ADMIN | M01-M28 | All available governed aggregates |
| HR | M01-M15, M27, M28 | Department aggregates only |
| MANAGER | M01-M06, M09-M15, M24 | Only the assigned department and explicitly assigned teams |
| EXECUTIVE | M16-M26, excluding M24 | Company aggregates only |

The role/metric/dimension registry in `config/metric_permissions.csv` is the allowlist used by the explorer. A metric not listed for a role is denied.

### Metric grain and drill-down

The explorer exposes each metric at the grain actually present in the Phase 3 warehouse:
- M01-M15 and M27-M28: department grain
- M16-M23 and M25-M26: company grain in the current `all_metrics` view
- M24: team grain

The UI only offers a dimension supported by the selected metric. It does not fabricate department or team breakdowns for company-only metrics, or team breakdowns for department-only metrics.

### Privacy and isolation

- M01-M03 and M07-M15 use the Phase 3 department-level governed views and their source-defined minimum group thresholds.
- M04-M06 and M27 use the source-defined threshold of 10.
- M22, M23 and M25 retain the task-count suppression applied by their Phase 3 views.
- The manager's department and team scope comes from the approved user registry and hierarchy file. The submitted selection is checked again on the server before the query.
- The dashboard only reads aggregate `all_metrics` rows. It does not expose employee-level records.
- Missing values and missing privacy counts must not be treated as zero or as permission to disclose.

### Demo users

The supplied `config/demo_users.csv` defines:
- `demo_admin`
- `demo_hr`
- `demo_manager_d01` assigned to D01 and T01/T02
- `demo_executive`

The hierarchy file contains IDs, not department display names. Keep those IDs as-is unless an authoritative name mapping is supplied.

### Run locally

From the repository root, use the existing project environment and entry point. For local demo only:

```powershell
$env:PULSEIQ_AUTH_MODE="development"
$env:PULSEIQ_DEMO_USER="demo_admin"
python -m streamlit run streamlit_app.py
```

Change `PULSEIQ_DEMO_USER` to `demo_hr`, `demo_manager_d01`, or `demo_executive` to verify the corresponding role. Do not expose development mode publicly.

Production authentication remains fail-closed until the deployed identity provider and trusted email-to-user mapping are configured. A successful local run is not proof of a production deployment.
