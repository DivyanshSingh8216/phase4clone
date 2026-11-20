"""Role-first, dimension-aware PulseIQ explorer.

This is deliberately separate from the historical explorer.py until source dictionaries,
identity assignments and hierarchy mappings are supplied and acceptance tests pass.
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

st.set_page_config(page_title="PulseIQ | Governed KPI Explorer", page_icon="📊", layout="wide")
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
    st.warning("No metrics have been approved for this role. Contact the data owner.")
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
if not available_dimensions:
    st.warning("No dimensions have been approved for this metric and role.")
    st.stop()

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

period_min = st.date_input("Start date", value=None)
period_max = st.date_input("End date", value=None)
if period_min and period_max and period_min > period_max:
    st.error("Start date must be on or before end date.")
    st.stop()

# Metric-specific grain, organization key and population-size column must be
# explicitly supplied in the permission registry. No implicit column guessing.
with (CONFIG / "metric_permissions.csv").open(encoding="utf-8-sig") as f:
    registry = pd.read_csv(f).fillna("")
row = registry[
    registry.role.astype(str).str.upper().eq(user.role)
    & registry.metric_id.astype(str).str.upper().eq(metric_id)
].iloc[0]
grain = str(row.get("metric_grain", "")).lower()
org_key = str(row.get("org_key_column", "")).strip()
group_size_column = str(row.get("group_size_column", "")).strip()
if grain not in {"company", "department", "team"} or not org_key:
    st.error("Metric grain and organisational key are not configured. Result withheld.")
    st.stop()
if dimension == "team" and grain != "team":
    st.error("This metric is not defined at team grain.")
    st.stop()
if dimension == "department" and grain not in {"department", "team"}:
    st.error("This metric is not defined at department grain.")
    st.stop()

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
query += " ORDER BY period"

try:
    with duckdb.connect(str(DB), read_only=True) as con:
        data = con.execute(query, params).fetchdf()
except Exception as exc:
    st.error(f"Governed query failed closed: {exc}")
    st.stop()

if data.empty:
    st.warning("No governed values exist for this selection.")
    st.stop()

if dimension != "company":
    if not group_size_column or permission.minimum_group_size is None:
        st.warning("Population size or minimum threshold is unavailable. All values are withheld.")
        st.stop()
    safe_mask = data.group_size.apply(
        lambda n: check_group_size(n, permission.minimum_group_size).allowed
    )
    withheld = int((~safe_mask).sum())
    data = data.loc[safe_mask].copy()
    if withheld:
        st.info(f"{withheld} result(s) withheld by the minimum-group privacy rule.")

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
st.plotly_chart(px.line(data, x="period", y="value", markers=True, title=str(catalog.loc[catalog.metric_id.eq(metric_id), "metric_name"].iloc[0])), use_container_width=True)
st.dataframe(data.drop(columns=["group_size"], errors="ignore"), use_container_width=True, hide_index=True)
st.caption(str(latest.caveat or ""))
