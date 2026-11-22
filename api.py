"""PulseIQ governed metrics API. Production deployments must replace X-Role with verified identity claims."""
from __future__ import annotations
import os
from pathlib import Path
from datetime import date
from typing import Optional
import duckdb
import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Query
from access_control import principal, department_filter

ROOT=Path(__file__).resolve().parent
DB=Path(os.getenv("PULSEIQ_DB_PATH", ROOT.parent/"phase-3"/"outputs"/"pulseiq.duckdb"))
app=FastAPI(title="PulseIQ Metrics API",version="1.0.0",description="Read-only API for governed Phase 3 metrics. Roles are development headers only; use trusted SSO/API-gateway claims in production.")

LINEAGE={
 "M16":{"definition":"Income booked in the ledger (accounts 4001-4004).","source":"warehouse.fact_ledger","transformation":"Phase 1 warehouse ETL -> v_m16_revenue -> all_metrics","dashboard":"Phase 3 Profit & Loss / Executive Scorecard"},
 "M17":{"definition":"Revenue less expenses, including interest income as defined by the metric dictionary.","source":"warehouse.fact_ledger","transformation":"Phase 1 warehouse ETL -> v_m17_net_profit -> all_metrics","dashboard":"Phase 3 Profit & Loss / Executive Scorecard"},
 "M18":{"definition":"Net profit as a share of revenue.","source":"warehouse.fact_ledger","transformation":"v_m17_net_profit and v_m16_revenue -> v_m18_operating_margin -> all_metrics","dashboard":"Phase 3 Executive Scorecard"},
 "M21":{"definition":"Unpaid invoice balance past due date at the report date.","source":"warehouse.fact_invoice","transformation":"Phase 1 warehouse ETL -> v_m21_overdue_receivables -> all_metrics","dashboard":"Phase 3 Receivables & Cash / Executive Scorecard"},
 "M22":{"definition":"Tasks done divided by tasks planned in the sprint, excluding cancelled tasks.","source":"warehouse.fact_task","transformation":"Phase 1 warehouse ETL -> v_m22_task_completion -> all_metrics","dashboard":"Phase 3 Executive Scorecard"},
}
def connect():
    if not DB.exists(): raise FileNotFoundError(f"DuckDB warehouse not found: {DB}")
    return duckdb.connect(str(DB),read_only=True)
def records(df):
    # FastAPI JSON responses cannot contain NaN/NaT; preserve missing as JSON null.
    return df.astype(object).where(pd.notna(df), None).to_dict(orient="records")
def get_user(x_role: str, x_department_id: str | None,
             authenticated_role: str | None = None, authenticated_department: str | None = None):
    # In production, only accept identity claims injected by a trusted reverse proxy
    # that strips caller-supplied copies of these headers. Never trust X-Role from clients.
    if os.getenv("PULSEIQ_AUTH_MODE", "development").lower() == "production":
        role, department = authenticated_role, authenticated_department
        if not role:
            raise HTTPException(status_code=401, detail="Authenticated identity claims are required.")
    else:
        role, department = x_role or "EXECUTIVE", x_department_id
    try: return principal(role, department)
    except PermissionError as e: raise HTTPException(status_code=403,detail=str(e))
def authorize_api_metric(user, metric_id):
    # The published API metrics are company-grain KPIs. Only the executive role
    # has an approved company-level grant in the committed conservative policy.
    if user.role != "EXECUTIVE":
        raise HTTPException(status_code=403, detail="This API metric is not authorised for your role.")
    if metric_id not in LINEAGE:
        raise HTTPException(status_code=404, detail="Metric not exposed by this API.")

def query_metric(metric_id, period, requested_department, user):
    authorize_api_metric(user, metric_id)
    if metric_id not in LINEAGE: raise HTTPException(status_code=404,detail="Metric not exposed by this API.")
    mode, dept=department_filter(user,requested_department)
    try: con=connect()
    except Exception as e: raise HTTPException(status_code=503,detail=str(e))
    try:
        sql="""SELECT m.metric_id,m.metric_name,CAST(m.period AS VARCHAR) period,
                      CAST(m.department_id AS VARCHAR) department_id,m.value,m.unit,m.caveat,
                      m.min_group_size,c.business_definition,c.formula,c.source_table
               FROM all_metrics m JOIN metric_catalog c USING(metric_id)
               WHERE m.metric_id=?"""
        params=[metric_id]
        if period:
            sql += " AND CAST(m.period AS DATE)=?"
            params.append(period)
        if mode=="company": sql += " AND m.department_id IS NULL"
        elif mode=="all": sql += " AND m.department_id IS NOT NULL"
        elif mode=="department":
            sql += " AND CAST(m.department_id AS VARCHAR)=?"
            params.append(dept)
        sql += " ORDER BY m.period DESC LIMIT 24"
        rows=records(con.execute(sql,params).fetchdf())
        # API returns only governed aggregates. The SQL views enforce the configured
        # minimum-group rules; rows without a group threshold are not reinterpreted.
        last=con.execute("SELECT MAX(CAST(period AS DATE)) FROM all_metrics WHERE metric_id=?",[metric_id]).fetchone()[0]
        return rows,last
    finally: con.close()

@app.get("/health")
def health():
    return {"status":"ok" if DB.exists() else "warehouse_missing","warehouse_available":DB.exists()}

@app.get("/v1/metrics")
def list_metrics(x_role: str=Header(default="EXECUTIVE"),x_department_id: Optional[str]=Header(default=None),
                 authenticated_role: Optional[str]=Header(default=None, alias="X-Authenticated-Role"),
                 authenticated_department: Optional[str]=Header(default=None, alias="X-Authenticated-Department")):
    user=get_user(x_role,x_department_id,authenticated_role,authenticated_department)
    if user.role != "EXECUTIVE":
        raise HTTPException(status_code=403, detail="The API catalogue is currently approved for EXECUTIVE only.")
    try:
        con=connect()
        try:
            rows=records(con.execute("""SELECT metric_id,metric_name,business_definition,formula,source_table,grain,time_period,unit,good_direction,caveat,minimum_group_size
                                FROM metric_catalog WHERE metric_id IN ('M16','M17','M18','M21','M22') ORDER BY metric_id""").fetchdf())
        finally: con.close()
    except Exception as e: raise HTTPException(status_code=503,detail=str(e))
    return {"role":user.role,"metrics":rows}

@app.get("/v1/metrics/{metric_id}")
def metric(metric_id: str, period: Optional[date]=Query(default=None), department_id: Optional[str]=Query(default=None),
           x_role: str=Header(default="EXECUTIVE"), x_department_id: Optional[str]=Header(default=None),
           authenticated_role: Optional[str]=Header(default=None, alias="X-Authenticated-Role"),
           authenticated_department: Optional[str]=Header(default=None, alias="X-Authenticated-Department")):
    user=get_user(x_role,x_department_id,authenticated_role,authenticated_department)
    rows,last=query_metric(metric_id,period,department_id,user)
    return {"metric_id":metric_id,"definition":LINEAGE[metric_id]["definition"],
            "source":LINEAGE[metric_id]["source"],"lineage":LINEAGE[metric_id]["transformation"],
            "dashboard":LINEAGE[metric_id]["dashboard"],"last_refresh":str(last) if last else None,
            "returned_rows":len(rows),"data":rows}

@app.get("/v1/lineage/{metric_id}")
def lineage(metric_id: str):
    if metric_id not in LINEAGE: raise HTTPException(status_code=404,detail="Metric lineage not documented.")
    return {"metric_id":metric_id,**LINEAGE[metric_id],
            "path":["PulseIQ_Dataset.xlsx (read-only)","Phase 1 ingestion and validation","DuckDB warehouse",
                    "governed metric SQL view","all_metrics","FastAPI /v1/metrics/{metric_id} and Streamlit dashboards"]}
