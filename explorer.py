"""Password-gated, executive-only public demo of governed PulseIQ KPIs."""
import os
import hmac
from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parent
DB = Path(os.getenv("PULSEIQ_DB_PATH", "/data/pulseiq.duckdb"))

st.set_page_config(page_title="PulseIQ KPI Explorer", page_icon="📈", layout="wide")
st.title("PulseIQ | KPI Explorer")
st.caption("Executive demo · Governed company-level aggregates only · No employee-level records")

# A shared demo password gates this limited executive-only preview. It is not SSO
# and must not be reused as production identity for multiple organisational roles.
expected_password = os.getenv("PULSEIQ_DEMO_PASSWORD", "")
if not expected_password:
    st.error("Demo access is not configured. Set PULSEIQ_DEMO_PASSWORD in the hosting environment.")
    st.stop()

if not st.session_state.get("pulseiq_authenticated", False):
    with st.form("pulseiq_login"):
        password = st.text_input("Demo access password", type="password")
        submitted = st.form_submit_button("Sign in")
    if submitted:
        if hmac.compare_digest(password, expected_password):
            st.session_state["pulseiq_authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

if not DB.exists():
    st.error(f"Warehouse not found at {DB}. Attach the approved Phase 3 DuckDB file to persistent storage.")
    st.stop()

try:
    with duckdb.connect(str(DB), read_only=True) as con:
        catalog = con.execute("""
            SELECT metric_id, metric_name, unit, minimum_group_size, caveat, good_direction
            FROM metric_catalog
            WHERE metric_id IN ('M16','M17','M18','M21','M22')
            ORDER BY metric_id
        """).fetchdf()
        if catalog.empty:
            st.error("The five approved executive KPIs are missing from metric_catalog.")
            st.stop()
        labels = {f"{r.metric_id} · {r.metric_name}": r.metric_id for r in catalog.itertuples()}
        selected = st.selectbox("Select KPI", list(labels))
        metric_id = labels[selected]
        row = catalog[catalog.metric_id == metric_id].iloc[0]
        df = con.execute("""
            SELECT CAST(period AS DATE) AS period, value, unit, caveat
            FROM all_metrics
            WHERE metric_id = ? AND department_id IS NULL
            ORDER BY period
        """, [metric_id]).fetchdf()
except Exception as exc:
    st.error(f"Unable to read the governed warehouse: {exc}")
    st.stop()

st.caption("Role: EXECUTIVE · Scope: Company · Source: Phase 3 governed metric views")
if df.empty:
    st.warning("No company-level observations are available for this KPI.")
else:
    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df = df.dropna(subset=["period"])
    if df.empty:
        st.warning("No valid reporting periods are available.")
    else:
        latest = df.sort_values("period").iloc[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("Latest value", f"{latest.value:,.2f}" if pd.notna(latest.value) else "Not available")
        c2.metric("Latest period", latest.period.strftime("%b %Y"))
        c3.metric("Unit", str(latest.unit))
        st.plotly_chart(px.line(df, x="period", y="value", markers=True, title=str(row.metric_name)), use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(str(row.caveat or ""))

st.info("This password-gated preview is limited to executive company-level KPIs. It does not implement SSO or the four-role self-service acceptance test.")
if st.button("Sign out"):
    st.session_state["pulseiq_authenticated"] = False
    st.rerun()
