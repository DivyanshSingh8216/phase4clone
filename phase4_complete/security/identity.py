"""Identity resolution; production remains fail-closed until verified SSO is configured."""
import csv
import os
from .policy import Principal, ROLES

def resolve_principal(config_dir):
    if os.getenv("PULSEIQ_AUTH_MODE", "development").lower() == "production":
        raise PermissionError("Production SSO adapter is not configured. Access denied by default.")
    user_id = os.getenv("PULSEIQ_DEMO_USER", "").strip()
    if not user_id:
        raise PermissionError("Set PULSEIQ_DEMO_USER to a user in config/demo_users.csv for localhost testing.")
    with (config_dir / "demo_users.csv").open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["user_id"].strip() == user_id:
                role = row["role"].strip().upper()
                if role not in ROLES:
                    break
                teams = tuple(x.strip() for x in row.get("team_ids", "").split(";") if x.strip())
                return Principal(user_id, role, row.get("department_id") or None, teams)
    raise PermissionError("Demo user is not present in the configured user registry.")
