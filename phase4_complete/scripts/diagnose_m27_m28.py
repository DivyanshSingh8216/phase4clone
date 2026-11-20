"""Read-only source diagnostics for M27 and M28; does not invent or calculate missing inputs."""
import os
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.getenv("PULSEIQ_DB_PATH", ROOT.parent / "phase-3" / "outputs" / "pulseiq.duckdb"))

def main():
    if not DB.exists():
        raise SystemExit(f"Phase 3 DuckDB not found: {DB}. Set PULSEIQ_DB_PATH.")
    con = duckdb.connect(str(DB), read_only=True)
    try:
        print("DATABASE:", DB)
        print("\nMETRIC CATALOG")
        print(con.execute("SELECT * FROM metric_catalog WHERE metric_id IN ('M27','M28') ORDER BY metric_id").df().to_string(index=False))
        print("\nALL_METRICS SCHEMA")
        print(con.execute("DESCRIBE all_metrics").df().to_string(index=False))
        print("\nM27/M28 OBSERVATIONS")
        print(con.execute("SELECT * FROM all_metrics WHERE metric_id IN ('M27','M28') ORDER BY metric_id, period").df().to_string(index=False))
        print("\nPOTENTIAL FORECAST/ACTUAL OBJECTS")
        objects = con.execute("SELECT table_name, table_type FROM information_schema.tables WHERE lower(table_name) LIKE '%forecast%' OR lower(table_name) LIKE '%actual%' ORDER BY table_name").df()
        print(objects.to_string(index=False) if not objects.empty else "No forecast/actual-named objects found.")
    finally:
        con.close()

if __name__ == "__main__":
    main()
