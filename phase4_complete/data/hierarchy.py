"""Trusted company/department/team hierarchy loader."""
import pandas as pd

REQUIRED = {"company_id", "department_id", "team_id"}

def load_hierarchy(path):
    if not path.exists():
        raise FileNotFoundError(f"Hierarchy mapping is required: {path}")
    df = pd.read_csv(path, dtype=str).fillna("")
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Hierarchy mapping missing columns: {sorted(missing)}")
    if df.duplicated(["department_id", "team_id"]).any():
        raise ValueError("Duplicate department/team mapping detected.")
    if (df["department_id"] == "").any() or (df["team_id"] == "").any():
        raise ValueError("Blank department/team identifiers are not allowed.")
    return df
