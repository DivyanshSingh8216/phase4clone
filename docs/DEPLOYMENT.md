# Streamlit Community Cloud deployment

This is the deployment path for PulseIQ. The Render Blueprint is not used.

## 1. Host the approved warehouse

The dashboard must not depend on a file uploaded from a developer's laptop or a database committed to GitHub.

1. Place the approved, read-only Phase 3 DuckDB snapshot in private HTTPS object storage.
2. Calculate its SHA-256 checksum.
3. Verify that it contains the governed `all_metrics` and `metric_catalog` tables.
4. Keep the object URL private and rotate signed URLs when the snapshot changes.

The app downloads the snapshot at startup, verifies its checksum, validates required tables and opens it read-only. It rejects non-HTTPS URLs and files larger than 2 GB.

## 2. Deploy from GitHub

1. Push the `phase4-complete` branch.
2. Open Streamlit Community Cloud and select **Create app**.
3. Repository: `DivyanshSingh8216/phase4clone`.
4. Branch: `phase4-complete`.
5. Main file path: `streamlit_app.py`.
6. Select Python 3.11 if prompted.

## 3. Configure app secrets and OIDC

In **App settings → Secrets**, add TOML with real values:

```toml
[auth]
redirect_uri = "https://YOUR-APP-NAME.streamlit.app/oauth2callback"
cookie_secret = "REPLACE_WITH_A_LONG_RANDOM_SECRET"
client_id = "YOUR_OIDC_CLIENT_ID"
client_secret = "YOUR_OIDC_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

PULSEIQ_DB_URL = "https://YOUR_PRIVATE_OBJECT_STORAGE_SIGNED_URL"
PULSEIQ_DB_SHA256 = "64_CHARACTER_SHA256_OF_THE_APPROVED_DUCKDB_FILE"

[identity.email_to_user_id]
"approved-admin@example.com" = "demo_admin"
"approved-hr@example.com" = "demo_hr"
"approved-manager@example.com" = "demo_manager_d01"
"approved-executive@example.com" = "demo_executive"
```

The four email addresses are placeholders. Replace them with approved test accounts. Configure the OIDC client redirect URI to exactly match the Streamlit URL plus `/oauth2callback`. The metadata URL shown is Google's example; use the selected identity provider's metadata URL.

The email-to-user map links a verified OIDC email to a `user_id` in `phase4_complete/config/demo_users.csv`. Role, department and team assignments are then read from that registry, not from browser input.

## 4. Current permission boundary

The committed policy currently grants:
- EXECUTIVE: M16, M17, M18, M21 and M22 at company grain.
- HR: M27 at department grain, with minimum group size 10 enforced by the governed Phase 3 view.
- ADMIN and MANAGER: no KPI grants.

This is fail-closed and does **not** yet satisfy the complete four-role company → department → team self-service requirement. Do not add grants until the official metric dictionary, data-owner approvals and authoritative hierarchy confirm metrics, grains, dimensions and thresholds. Small manager teams must remain suppressed unless the approved policy proves the result safe.

## 5. Deployment tests

- Unknown OIDC emails are denied.
- Each approved account sees only its assigned role.
- EXECUTIVE sees only its five company KPIs.
- HR sees only M27 department aggregates and no group below 10.
- ADMIN and MANAGER receive no KPI data under the current policy.
- Query-parameter changes and direct metric/department/team IDs cannot bypass policy.
- Data cutoff and caveats are visible.
- Phone and independent-user tests are recorded.

## 6. Refresh and API limitations

The app loads a checksum-pinned snapshot from the HTTPS object URL at startup. It is not itself a scheduled ETL refresh service. A separate scheduled job must publish a new approved snapshot and update the URL/checksum secrets together. Do not claim automated refresh until that workflow, timestamp and failure handling have been verified.

FastAPI is not deployed by this Streamlit app. Deploy it separately behind verified identity claims before exposing it publicly.
