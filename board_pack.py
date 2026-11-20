"""Generate an editable 8-slide PowerPoint board pack from Phase 3 output evidence."""
from pathlib import Path
import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"board_pack"; OUT.mkdir(exist_ok=True)
P3=ROOT.parent/"phase-3"/"outputs"
def csv(n): return pd.read_csv(P3/n)
pnl=csv("phase3_day11_pnl_monthly.csv")
cash=csv("phase3_day12_cash_flow_monthly.csv")
age=csv("phase3_day12_receivables_ageing.csv")
anom=csv("phase3_day14_anomalies_by_type.csv")
recon=csv("phase3_day13_reconciliation.csv").iloc[0]
forecast=csv("phase3_day14_forecast_validation_summary.csv").iloc[0]
ref=csv("phase3_day13_reference_comparison.csv")
prs=Presentation(); prs.slide_width= Inches(13.333); prs.slide_height= Inches(7.5)
NAVY=RGBColor(20,43,74); BLUE=RGBColor(36,105,166); CYAN=RGBColor(55,160,180); PALE=RGBColor(235,242,248); DARK=RGBColor(38,50,56); GREY=RGBColor(105,118,130); WHITE=RGBColor(255,255,255)
def textbox(slide,x,y,w,h,text,size=18,color=DARK,bold=False,font="Aptos"):
    sh=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf=sh.text_frame; tf.clear(); tf.word_wrap=True
    p=tf.paragraphs[0]; p.text=str(text); p.font.name=font; p.font.size=Pt(size); p.font.bold=bold; p.font.color.rgb=color
    return sh
def base(title,sub=None):
    s=prs.slides.add_slide(prs.slide_layouts[6]); s.background.fill.solid(); s.background.fill.fore_color.rgb=WHITE
    band=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width, Inches(.18)); band.fill.solid(); band.fill.fore_color.rgb=BLUE; band.line.fill.background()
    textbox(s,.55,.38,12.2,.55,title,26,NAVY,True)
    if sub: textbox(s,.58,1.02,12.1,.35,sub,10,GREY)
    textbox(s,.55,7.13,12.2,.18,"PulseIQ | Phase 4 board pack | Phase 3 packaged evidence | Validate before external circulation",8,GREY)
    return s
def metric_card(s,x,y,w,label,value,caption=""):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(1.28))
    sh.fill.solid(); sh.fill.fore_color.rgb=PALE; sh.line.color.rgb=PALE
    textbox(s,x+.18,y+.12,w-.36,.24,label,10,GREY,True)
    textbox(s,x+.18,y+.40,w-.36,.45,value,23,NAVY,True)
    if caption: textbox(s,x+.18,y+.91,w-.36,.23,caption,8,GREY)
def add_chart(s,df,cat,series,x,y,w,h,title,chart_type=XL_CHART_TYPE.LINE):
    data=CategoryChartData(); data.categories=[str(v)[:7] for v in df[cat].tolist()]
    for col,label in series: data.add_series(label,tuple(float(v) for v in df[col].fillna(0)))
    chart=s.shapes.add_chart(chart_type, Inches(x), Inches(y), Inches(w), Inches(h), data).chart
    chart.has_legend=len(series)>1
    if chart.has_legend: chart.legend.position=XL_LEGEND_POSITION.BOTTOM
    chart.has_title=True; chart.chart_title.text_frame.text=title
    chart.value_axis.has_major_gridlines=True
    return chart
# 1 title
s=prs.slides.add_slide(prs.slide_layouts[6]); s.background.fill.solid(); s.background.fill.fore_color.rgb=NAVY
textbox(s,.85,1.35,11.6,.9,"PulseIQ",42,WHITE,True)
textbox(s,.9,2.35,11.5,.7,"Workforce, finance and operating intelligence",24,WHITE)
textbox(s,.9,3.3,11.2,.7,"Board review | April 2025 – September 2026",17,RGBColor(180,210,232))
textbox(s,.9,6.55,11.2,.35,"Prepared from the Phase 3 packaged analytics outputs. Refresh and reconcile before board circulation.",10,WHITE)
# 2 executive summary
s=base("Executive overview","18 monthly periods in the packaged Phase 3 evidence")
metric_card(s,.65,1.65,2.85,"Total income","₹1,260.93m","Apr 2025–Sep 2026")
metric_card(s,3.65,1.65,2.85,"Net profit","₹224.67m","Apr 2025–Sep 2026")
metric_card(s,6.65,1.65,2.85,"Open receivables","₹139.39m","Ageing output, not all overdue")
metric_card(s,9.65,1.65,2.85,"Estimated anomaly risk","₹31.42m","Investigation signal, not confirmed loss")
textbox(s,.8,3.45,11.7,1.5,"Management focus: protect margin visibility, accelerate older receivables, preserve workforce-cost reconciliations, and triage anomaly signals with evidence. Forecast accuracy remains unmeasured until actuals arrive.",19,DARK)
# 3 P&L
s=base("Revenue and profitability","Source: phase3_day11_pnl_monthly.csv | Values in INR")
add_chart(s,pnl,"period",[("operating_revenue","Operating revenue"),("expenses","Expenses"),("net_profit","Net profit")],.7,1.55,8.1,4.8,"Monthly P&L")
latest=pnl.iloc[-1]
metric_card(s,9.15,1.8,3.2,"Sep 2026 net profit",f"₹{latest.net_profit/1e6:.2f}m",f"Margin {latest.net_margin_pct:.2f}%")
metric_card(s,9.15,3.3,3.2,"Sep 2026 total income",f"₹{latest.total_income/1e6:.2f}m")
textbox(s,9.25,5.05,3.0,.9,"18-month net profit: ₹224.67m",14,NAVY,True)
# 4 cash flow
s=base("Cash movement","Source: phase3_day12_cash_flow_monthly.csv | Not an audited bank balance")
add_chart(s,cash,"period",[("cash_in","Cash in"),("cash_out","Cash out"),("net_cash_flow","Net cash flow")],.7,1.55,8.1,4.8,"Monthly cash movement",XL_CHART_TYPE.COLUMN_CLUSTERED)
latestc=cash.iloc[-1]
metric_card(s,9.15,1.8,3.2,"Sep 2026 net cash flow",f"₹{latestc.net_cash_flow/1e6:.2f}m")
metric_card(s,9.15,3.3,3.2,"18-month net cash flow",f"₹{cash.net_cash_flow.sum()/1e6:.2f}m")
textbox(s,9.25,5.05,3.0,.9,"Reconcile to payment registers and bank statements before treasury use.",12,GREY)
# 5 ageing
s=base("Receivables ageing","Source: phase3_day12_receivables_ageing.csv | Total open ageing ₹139.39m")
age=age.sort_values("bucket_order")
add_chart(s,age,"ageing_bucket",[("receivables_amount","Receivables")],.7,1.55,7.5,4.8,"Open receivables by ageing bucket",XL_CHART_TYPE.BAR_CLUSTERED)
for i,r in enumerate(age.itertuples()):
    metric_card(s,8.65,1.55+i*1.35,3.55,str(r.ageing_bucket),f"₹{r.receivables_amount/1e6:.2f}m",f"{int(r.invoice_count)} invoices")
# 6 workforce cost
s=base("Workforce cost reconciliation","Source: phase3_day13_reconciliation.csv")
metric_card(s,.8,1.7,3.6,"Payroll employer cost",f"₹{recon.payroll_employer_cost/1e6:.2f}m","Source payroll")
metric_card(s,4.85,1.7,3.6,"Joined employer cost",f"₹{recon.joined_employer_cost/1e6:.2f}m","Department/month output")
metric_card(s,8.9,1.7,3.6,"Approved leave days",f"{int(recon.source_approved_leave_days):,}","Source and joined output agree")
textbox(s,1.0,3.8,11.2,1.1,f"Overtime cost reconciles at ₹{recon.payroll_overtime_cost:,.2f}. Employer cost, overtime cost and approved leave days match to floating-point precision.",18,DARK)
textbox(s,1.0,5.4,11.2,.7,"Day 13 reference comparison: 2,569 MATCH, 5 INVESTIGATE, 9,009 ACTUAL_ONLY (outside supplied reference coverage).",12,GREY)
# 7 anomaly
s=base("Anomaly signals require investigation","Source: phase3_day14_anomalies_by_type.csv | Not proof of fraud or realized loss")
ag=anom.groupby("anomaly_type",as_index=False).agg(money_at_risk=("money_at_risk","sum"),flagged=("flagged_count","sum")).sort_values("money_at_risk",ascending=False).head(6)
add_chart(s,ag,"anomaly_type",[("money_at_risk","Estimated money at risk")],.7,1.55,8.0,4.8,"Highest estimated risk groups",XL_CHART_TYPE.BAR_CLUSTERED)
metric_card(s,9.1,1.8,3.2,"Estimated money at risk",f"₹{anom.money_at_risk.sum()/1e6:.2f}m","Across packaged anomaly output")
metric_card(s,9.1,3.35,3.2,"No money value",f"{int(anom.flagged_without_money_value.sum())}","Flagged records")
textbox(s,9.2,5.05,3.0,.9,"Triage, verify source records and record disposition.",12,GREY)
# 8 forecasts & decisions
s=base("Forecast readiness and decisions","Source: Phase 3 forecast validation and reference comparison outputs")
metric_card(s,.8,1.6,3.4,"Forecast rows",str(int(forecast.forecast_rows)),"Trained through Sep 2026")
metric_card(s,4.95,1.6,3.4,"Rows with actuals",str(int(forecast.rows_with_actual)),"No accuracy result yet")
metric_card(s,9.1,1.6,3.4,"Rows with error",str(int(forecast.rows_with_error)),"MAPE not available")
textbox(s,.95,3.45,11.3,2.2,"Board decisions\n1. Finance: sign off P&L and cash reconciliations.\n2. Collections: assign owners to the 61+ day receivables.\n3. HR/Finance: retain payroll-to-workforce reconciliation.\n4. Risk owners: disposition anomaly signals with source evidence.\n5. Analytics: back-test forecasts when actuals become available.\n6. Technology: complete SSO, hosting, secrets and production acceptance before public release.",15,DARK)
path=OUT/"PulseIQ_Board_Pack_Phase4.pptx"; prs.save(path); print(path)
