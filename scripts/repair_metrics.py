"""Safe, read-only metric audit and local Phase 3 warehouse placement."""
from __future__ import annotations
import argparse, csv, hashlib, os, shutil, urllib.request
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "phase4_complete" / "data" / "pulseiq.duckdb"
URL = "https://raw.githubusercontent.com/DivyanshSingh8216/PulseIQ-Phase3/main/outputs/pulseiq.duckdb"
EXPECTED = "028c40f21e5968e8cf363d0bdf5e2b3cf0205e82"

def blob_sha(path):
    h=hashlib.sha1(); h.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",type=Path)
    ap.add_argument("--download-db",action="store_true")
    ap.add_argument("--validate",action="store_true")
    a=ap.parse_args()
    TARGET.parent.mkdir(parents=True,exist_ok=True)
    configured=os.getenv("PULSEIQ_DB_PATH","").strip()
    source=a.db.resolve() if a.db else (Path(configured).resolve() if configured else None)
    if source and source.is_file() and source != TARGET.resolve():
        # Preserve the supplied source file; copy only the verified derived DB.
        if blob_sha(source) != EXPECTED:
            raise SystemExit("Provided database does not match the verified Phase 3 warehouse; left untouched.")
        shutil.copy2(source,TARGET)
    elif not TARGET.is_file():
        if not a.download_db:
            raise SystemExit(f"Database not found. Supply --db .\\pulseiq.duckdb or use --download-db.")
        tmp=TARGET.with_suffix(".duckdb.part")
        try:
            req=urllib.request.Request(URL,headers={"User-Agent":"PulseIQ-Phase4-Metric-Validator/1.0"})
            with urllib.request.urlopen(req,timeout=120) as response,tmp.open("wb") as out:
                shutil.copyfileobj(response,out)
            if blob_sha(tmp)!=EXPECTED: raise RuntimeError("Downloaded DB checksum mismatch.")
            tmp.replace(TARGET)
        finally:
            if tmp.exists(): tmp.unlink()
    db=TARGET if TARGET.is_file() else (source or TARGET)
    if blob_sha(db)!=EXPECTED: raise SystemExit("Phase 3 DB SHA verification failed; no database changes made.")
    rows=[]
    con=duckdb.connect(str(db),read_only=True)
    try:
        tables={x[0] for x in con.execute("SHOW TABLES").fetchall()}
        missing={"all_metrics","metric_catalog"}-tables
        if missing: raise SystemExit(f"Missing required views: {sorted(missing)}")
        s=con.execute("""SELECT metric_id,metric_name,COUNT(*) n,COUNT(value) populated,
          COUNT(*)-COUNT(value) nulls,COUNT(DISTINCT period) periods,MIN(period) first_period,
          MAX(period) last_period,MIN(value) min_value,MAX(value) max_value
          FROM all_metrics GROUP BY 1,2 ORDER BY 1""").fetchdf()
        for i in range(1,29):
            mid=f"M{i:02d}"; m=s[s.metric_id.astype(str)==mid]
            if m.empty: rows.append({"metric_id":mid,"status":"MISSING","details":"No all_metrics rows"}); continue
            x=m.iloc[0]; status="POPULATED"; detail="Values present; source formula still requires lineage verification"
            if mid=="M28" and int(x.populated)==0: status="UNAVAILABLE"; detail="No MAPE observations; never display as 0%"
            elif mid in {"M21","M27"} and int(x.periods)<=1: status="SNAPSHOT_ONLY"; detail="One reporting period; display as snapshot, not trend"
            elif mid in {"M05","M06"} and int(x.nulls)>0: status="NULLS_PRESERVED"; detail=f"{int(x.nulls)} null/suppressed values; do not coerce to zero"
            rows.append({"metric_id":mid,"status":status,"details":detail,"rows":int(x.n),"populated":int(x.populated),"nulls":int(x.nulls),"periods":int(x.periods),"first_period":str(x.first_period),"last_period":str(x.last_period),"min_value":str(x.min_value),"max_value":str(x.max_value)})
        m18=con.execute("""SELECT a.period,a.value reported,p.value profit,r.value revenue
          FROM all_metrics a LEFT JOIN all_metrics p ON p.metric_id='M17' AND p.period=a.period
          LEFT JOIN all_metrics r ON r.metric_id='M16' AND r.period=a.period WHERE a.metric_id='M18'""").fetchdf()
        valid=m18.dropna(subset=["reported","profit","revenue"]); compared=bad=0
        for x in valid.itertuples():
            if float(x.revenue)==0: continue
            ratio=float(x.profit)/float(x.revenue); reported=float(x.reported)
            expected=ratio*100 if abs(reported)>1.5 else ratio; compared+=1
            if abs(reported-expected)>max(.05,abs(expected)*.002): bad+=1
        rows.append({"metric_id":"M18_CHECK","status":"RECONCILE" if bad else ("CHECKED" if compared else "NOT_COMPARABLE"),"details":f"{compared} matched periods checked against M17/M16; mismatches={bad}. Confirm official denominator before changing values."})
        neg=con.execute("SELECT COUNT(*) FROM all_metrics WHERE metric_id='M25' AND value<0").fetchone()[0]
        rows.append({"metric_id":"M25_CHECK","status":"REVIEW" if neg else "CHECKED","details":f"Negative cycle-time observations={neg}"})
        rows.append({"metric_id":"M09_CHECK","status":"MANUAL_RECONCILIATION","details":"Reconcile with approved ledger accounts 5001-5005; no ledger mapping is guessed."})
    finally: con.close()
    out=ROOT/"reports"/"metric_validation.csv"; out.parent.mkdir(exist_ok=True)
    fields=sorted({k for row in rows for k in row})
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"Verified read-only database placed at: {db}")
    print(f"Metric audit report: {out}")
    for x in rows: print(f"{x['metric_id']}: {x['status']} | {x['details']}")

if __name__=="__main__": main()
