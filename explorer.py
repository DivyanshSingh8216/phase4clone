"""Privacy-aware self-service explorer for governed aggregate metrics."""
import os
from pathlib import Path
import duckdb
import pandas as pd
import streamlit as st
import plotly.express as px
from access_control import principal, department_filter

ROOT=Path(__file__).resolve().parent
DB=Path(os.getenv("PULSEIQ_DB_PATH",ROOT.parent/"phase-3"/"outputs"/"pulseiq.duckdb"))
st.set_page_config(page_title="PulseIQ KPI Explorer",page_icon="📈",layout="wide")
st.title("PulseIQ | KPI Explorer")
st.caption("Governed aggregate metrics only. Employee-level records are not available in this explorer.")
if os.getenv("PULSEIQ_AUTH_MODE", "development").lower() == "production":
    st.error("Production identity integration is not configured in this Streamlit build. Keep this service private until SSO supplies a verified role and department claim.")
    st.stop()
try:
    user=principal(os.getenv("PULSEIQ_ROLE","EXECUTIVE"),os.getenv("PULSEIQ_MANAGER_DEPARTMENT"))
except PermissionError as e:
    st.error(str(e)); st.stop()
if not DB.exists():
    st.error(f"DuckDB warehouse not found: {DB}. Set PULSEIQ_DB_PATH."); st.stop()
con=duckdb.connect(str(DB),read_only=True)
try:
    catalog=con.execute("SELECT metric_id,metric_name,unit,minimum_group_size,caveat,good_direction FROM metric_catalog ORDER BY metric_id").fetchdf()
    ids=catalog.metric_id.tolist()
    label_to_id={f"{r.metric_id} · {r.metric_name}":r.metric_id for r in catalog.itertuples()}
    selected=st.selectbox("Metric",list(label_to_id))
    metric_id=label_to_id[selected]
    row=catalog[catalog.metric_id==metric_id].iloc[0]
    # Department/team values are aggregates in all_metrics. M24 uses the
    # department_id field to carry team_id, as documented by its SQL view.
    is_team=(metric_id=="M24")
    dimensions=con.execute("SELECT DISTINCT CAST(department_id AS VARCHAR) FROM all_metrics WHERE metric_id=? AND department_id IS NOT NULL ORDER BY 1",[metric_id]).fetchdf().iloc[:,0].dropna().tolist()
    requested=None
    if user.role in ("ADMIN","HR") and dimensions:
        requested=st.selectbox("Team" if is_team else "Department",["All"]+dimensions)
        if requested=="All": requested=None
    elif user.role=="MANAGER":
        requested=user.department_id
        if requested not in dimensions:
            st.info("No governed aggregate is available for your assigned department and this metric.")
            st.stop()
    mode,dept=department_filter(user,requested)
    query="""SELECT CAST(period AS DATE) period,CAST(department_id AS VARCHAR) department_id,
                    value,unit,caveat,min_group_size
             FROM all_metrics WHERE metric_id=?"""
    params=[metric_id]
    if mode=="company": query+=" AND department_id IS NULL"
    elif mode=="all": query+=" AND department_id IS NOT NULL"
    elif mode=="department": query+=" AND CAST(department_id AS VARCHAR)=?"; params.append(dept)
    query+=" ORDER BY period"
    df=con.execute(query,params).fetchdf()
finally:
    con.close()
st.caption(f"Access role: {user.role} · Minimum group threshold: {row.minimum_group_size if pd.notna(row.minimum_group_size) else 'Not specified by source metric'}")
if df.empty:
    st.warning("No governed values are available for this selection. This may reflect missing source data, the metric's suppression rule, or the absence of a company-level aggregate.")
else:
    df["period"]=pd.to_datetime(df["period"],errors="coerce")
    df=df.dropna(subset=["period"])
    if not df.empty:
        latest=df.sort_values("period").iloc[-1]
        a,b,c=st.columns(3)
        a.metric("Latest value",f"{latest.value:,.2f}" if pd.notna(latest.value) else "Not available")
        b.metric("Period",latest.period.strftime("%b %Y"))
        c.metric("Unit",str(latest.unit))
        fig=px.line(df,x="period",y="value",color="department_id" if mode=="all" else None,
                    markers=True,title=f"{row.metric_name} over time")
        st.plotly_chart(fig,use_container_width=True)
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.caption(str(row.caveat or ""))
st.info("Privacy controls are enforced in this application layer and by the governed Phase 3 metric views. Production deployment must authenticate users with SSO and pass verified role and department claims; environment variables are for local demonstration only.")
