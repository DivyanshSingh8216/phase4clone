"""Export only explicitly approved governed aggregates to a size-checked Parquet bundle."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.getenv("PULSEIQ_DB_PATH", ROOT.parent / "phase-3" / "outputs" / "pulseiq.duckdb"))
MAX_BYTES = 200 * 1024 * 1024
DEFAULT_METRICS = ("M16", "M17", "M18", "M21", "M22")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "published"))
    ap.add_argument("--metrics", nargs="+", default=list(DEFAULT_METRICS))
    ap.add_argument("--max-mb", type=int, default=200)
    args = ap.parse_args()
    metrics = tuple(dict.fromkeys(x.upper() for x in args.metrics))
    if not metrics or any(x not in DEFAULT_METRICS for x in metrics):
        raise SystemExit(f"Only approved aggregate metrics may be exported: {', '.join(DEFAULT_METRICS)}")
    if not DB.exists():
        raise SystemExit(f"Warehouse missing: {DB}")
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    staging = out / "_staging"
    staging.mkdir(exist_ok=True)
    parquet = staging / "metrics.parquet"
    catalog_file = staging / "metric_catalog.parquet"
    con = duckdb.connect(str(DB), read_only=True)
    try:
        con.execute("CREATE TEMP TABLE export_metrics AS SELECT metric_id, metric_name, CAST(period AS DATE) period, department_id, value, unit, caveat, min_group_size FROM all_metrics WHERE metric_id IN (" + ",".join("?" for _ in metrics) + ")", list(metrics))
        con.execute("CREATE TEMP TABLE export_catalog AS SELECT metric_id, metric_name, business_definition, formula, source_table, grain, time_period, unit, good_direction, caveat, minimum_group_size FROM metric_catalog WHERE metric_id IN (" + ",".join("?" for _ in metrics) + ")", list(metrics))
        con.execute("COPY export_metrics TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(parquet)])
        con.execute("COPY export_catalog TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(catalog_file)])
        rows = con.execute("SELECT COUNT(*) FROM export_metrics").fetchone()[0]
        cutoff = con.execute("SELECT MAX(period) FROM export_metrics").fetchone()[0]
    finally:
        con.close()
    total = parquet.stat().st_size + catalog_file.stat().st_size
    limit = args.max_mb * 1024 * 1024
    if total > limit:
        raise SystemExit(f"Export is {total / 1024 / 1024:.2f} MB, above the {args.max_mb} MB limit. Reduce approved aggregate scope.")
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_cutoff": str(cutoff) if cutoff else None,
        "metric_ids": list(metrics),
        "row_count": rows,
        "bundle_bytes": total,
        "bundle_limit_bytes": limit,
        "files": {
            "metrics.parquet": {"bytes": parquet.stat().st_size, "sha256": sha256(parquet)},
            "metric_catalog.parquet": {"bytes": catalog_file.stat().st_size, "sha256": sha256(catalog_file)}
        },
        "source_database": "configured DuckDB warehouse (read-only)",
        "privacy_note": "Only explicitly allowlisted governed aggregate metrics are exported; no raw source tables are exported."
    }
    (staging / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    final = out / "current"
    backup = out / "previous"
    if backup.exists():
        import shutil; shutil.rmtree(backup)
    if final.exists():
        final.replace(backup)
    staging.replace(final)
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
