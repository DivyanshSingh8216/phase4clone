"""Role-first, dimension-aware PulseIQ explorer.

Only metric/dimension pairs present in the reviewed permission registry are selectable.
Production remains unavailable until verified SSO is configured.
"""
import os
from pathlib import Path
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from security.identity import resolve_principal
from security.policy import load_permissions, authorize_metric, authorize_dimension
from security.privacy import check_group_size
from data.hierarchy import load_hierarchy

ROOT = Path(__file__).resolve().parent
PHASE4_ROOT = ROOT.parent
DB = Path(os.getenv("PULSEIQ_DB_PATH", PHASE4_ROOT / "phase-3" / "outputs" / "pulseiq.duckdb"))
CONFIG = ROOT / "config"

st.title("PulseIQ | Governed KPI Explorer")
st.caption("Role-authorised aggregate analytics. Employee-level records are never displayed.")

try:
    user = resolve_principal(CONFIG)
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    hierarchy = load_hierarchy(CONFIG / "department_team_hierarchy.csv")
except Exception as exc:
    st.error(f"Explorer is unavailable: {exc}")
    st.stop()

if not DB.exists():
    st.error(f"Warehouse not found: {DB}")
    st.stop()

role_permissions = [p for (role, _), p in permissions.items() if role == user.role]
if not role_permissions:
    st.warning("No KPI metrics are approved for this role in the current demo policy. Contact the data owner.")
    st.stop()

with duckdb.connect(str(DB), read_only=True) as con:
    catalog = con.execute(
        "SELECT metric_id, metric_name, unit, caveat FROM metric_catalog ORDER BY metric_id"
    ).fetchdf()

allowed_ids = {p.metric_id for p in role_permissions}
catalog = catalog[catalog.metric_id.isin(allowed_ids)].copy()
if catalog.empty:
    st.warning("No authorised metrics are present in the governed metric catalogue.")
    st.stop()

labels = {f"{r.metric_id} · {r.metric_name}": r.metric_id for r in catalog.itertuples()}
selected_label = st.selectbox("1. Choose an authorised metric", list(labels))
metric_id = labels[selected_label]
permission = authorize_metric(user, metric_id, permissions)

available_dimensions = list(permission.dimensions)
dimension = st.selectbox("2. Choose an authorised dimension", available_dimensions)
authorize_dimension(user, permission, dimension)

department_id = None
team_id = None
if dimension in ("department", "team"):
    if user.role == "MANAGER":
        allowed_departments = [user.department_id] if user.department_id else []
        allowed_teams = list(user.team_ids)
    else:
        allowed_departments = sorted(hierarchy.department_id.unique().tolist())
        allowed_teams = sorted(hierarchy.team_id.unique().tolist())

    if dimension == "department":
        choices = allowed_departments
        if not choices:
            st.info("No authorised department scope is assigned.")
            st.stop()
        department_id = st.selectbox("3. Choose department", choices)
        if user.role == "MANAGER" and department_id != user.department_id:
            st.error("Access denied: this department is outside your assigned scope.")
            st.stop()
    elif dimension == "team":
        scoped = hierarchy.copy()
        if user.role == "MANAGER":
            scoped = scoped[
                scoped.department_id.eq(user.department_id)
                & scoped.team_id.isin(allowed_teams)
            ]
        else:
            department_id = st.selectbox(
                "3. Choose department", sorted(scoped.department_id.unique().tolist())
            )
            scoped = scoped[scoped.department_id.eq(department_id)]
        teams = sorted(scoped.team_id.unique().tolist())
        if not teams:
            st.info("No authorised teams are mapped to this department.")
            st.stop()
        team_id = st.selectbox("4. Choose team", teams)
        # Re-check the submitted selection on the server, not only in the UI options.
        if user.role == "MANAGER":
            if department_id is not None and department_id != user.department_id:
                st.error("Access denied: this department is outside your assigned scope.")
                st.stop()
            if team_id not in user.team_ids:
                st.error("Access denied: this team is outside your assigned scope.")
                st.stop()
elif dimension == "source":
    with duckdb.connect(str(DB), read_only=True) as con:
        sources = con.execute(
            "SELECT DISTINCT CAST(department_id AS VARCHAR) FROM all_metrics "
            "WHERE metric_id = ? AND department_id IS NOT NULL ORDER BY 1",
            [metric_id],
        ).fetchdf().iloc[:, 0].dropna().tolist()
    if not sources:
        st.info("No source-level aggregates are available for this metric.")
        st.stop()
    source_id = st.selectbox("3. Choose source", sources)

grain = permission.metric_grain
org_key = permission.org_key_column
group_size_column = permission.group_size_column
if dimension == "team" and grain != "team":
    st.error("This metric is not defined at team grain.")
    st.stop()
if dimension == "department" and grain not in {"department", "team"}:
    st.error("This metric is not defined at department grain.")
    st.stop()
if dimension == "company" and grain != "company":
    st.error("This metric is not defined at company grain.")
    st.stop()
if dimension == "source" and grain != "source":
    st.error("This metric is not defined at source grain.")
    st.stop()

period_min = st.date_input("Start date", value=None)
period_max = st.date_input("End date", value=None)
if period_min and period_max and period_min > period_max:
    st.error("Start date must be on or before end date.")
    st.stop()

# SQL identifiers are read only from the validated, committed permission registry.
query = f"""
SELECT CAST(period AS DATE) AS period,
       CAST({org_key} AS VARCHAR) AS org_key,
       value, unit, caveat
       {"," + group_size_column + " AS group_size" if group_size_column else ""}
FROM all_metrics
WHERE metric_id = ?
"""
params = [metric_id]
if period_min:
    query += " AND CAST(period AS DATE) >= ?"
    params.append(str(period_min))
if period_max:
    query += " AND CAST(period AS DATE) <= ?"
    params.append(str(period_max))
if dimension == "company":
    query += f" AND {org_key} IS NULL"
elif dimension == "department":
    query += f" AND CAST({org_key} AS VARCHAR) = ?"
    params.append(str(department_id))
elif dimension == "team":
    query += f" AND CAST({org_key} AS VARCHAR) = ?"
    params.append(str(team_id))
elif dimension == "source":
    query += f" AND CAST({org_key} AS VARCHAR) = ?"
    params.append(str(source_id))
query += " ORDER BY period"

try:
    with duckdb.connect(str(DB), read_only=True) as con:
        data = con.execute(query, params).fetchdf()
except Exception as exc:
    st.error(f"Governed query failed closed: {exc}")
    st.stop()

if data.empty:
    if metric_id == "M28":
        st.info("Forecast error (MAPE) is unavailable: no matching actual headcount exists for the forecast periods in this warehouse snapshot.")
    else:
        st.warning("No governed values exist for this selection.")
    st.stop()

if dimension != "company":
    if permission.privacy_mode == "group_count":
        if not group_size_column or permission.minimum_group_size is None:
            st.error("Privacy configuration is incomplete. All values are withheld.")
            st.stop()
        safe_mask = data.group_size.apply(
            lambda n: check_group_size(n, permission.minimum_group_size).allowed
        )
        withheld = int((~safe_mask).sum())
        data = data.loc[safe_mask].copy()
        if withheld:
            st.info("One or more results were withheld by the minimum-group privacy rule.")
    elif permission.privacy_mode == "governed_view":
        # The source view has already applied the dictionary threshold in SQL.
        # Do not infer a population count from all_metrics or expose employee rows.
        st.caption(f"Privacy threshold: {permission.minimum_group_size}+ records, enforced upstream by the governed Phase 3 view.")
    elif permission.privacy_mode == "none" and metric_id in {"M23", "M24", "M25", "M26"}:
        # These are operational delivery/velocity aggregates, not employee-level
        # people metrics. M24 is team-grain and is additionally restricted to the
        # manager's explicitly assigned team_ids by the hierarchy scope below.
        st.caption("Operational aggregate. No employee-level records are exposed.")
    else:
        st.error("No approved privacy enforcement is configured for this non-company view. Results withheld.")
        st.stop()

if data.empty:
    st.warning("All results were withheld because they did not meet the privacy threshold.")
    st.stop()

st.caption(f"Role: {user.role} · Metric: {metric_id} · Dimension: {dimension}")
data["period"] = pd.to_datetime(data["period"], errors="coerce")
data = data.dropna(subset=["period", "value"])
if data.empty:
    st.warning("No valid numeric observations are available.")
    st.stop()

latest = data.sort_values("period").iloc[-1]
a, b, c = st.columns(3)
a.metric("Latest value", f"{latest.value:,.2f}")
b.metric("Latest period", latest.period.strftime("%b %Y"))
c.metric("Unit", str(latest.unit))
metric_name = str(catalog.loc[catalog.metric_id.eq(metric_id), "metric_name"].iloc[0])
st.plotly_chart(px.line(data, x="period", y="value", markers=True, title=metric_name), use_container_width=True)
st.dataframe(data.drop(columns=["group_size"], errors="ignore"), use_container_width=True, hide_index=True)
st.caption(str(latest.caveat or ""))

st.info("M28 forecast error is intentionally not included in the selectable metrics until actual headcount is available for matching forecast periods. Forecast projections must not be presented as forecast accuracy.")
