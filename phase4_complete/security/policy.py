"""Fail-closed, data-driven role/metric/dimension authorization."""
from dataclasses import dataclass
import csv

ROLES = {"ADMIN", "HR", "MANAGER", "EXECUTIVE"}
DIMENSIONS = {"company", "department", "team", "source"}
GRAINS = {"company", "department", "team", "source"}
PRIVACY_MODES = {"none", "group_count", "governed_view"}

@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str
    department_id: str | None = None
    team_ids: tuple[str, ...] = ()

@dataclass(frozen=True)
class Permission:
    role: str
    metric_id: str
    dimensions: tuple[str, ...]
    minimum_group_size: int | None
    metric_grain: str = ""
    org_key_column: str = ""
    group_size_column: str = ""
    privacy_mode: str = "none"

def load_permissions(path):
    result = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            role = row["role"].strip().upper()
            metric = row["metric_id"].strip().upper()
            if role not in ROLES or not metric:
                raise ValueError(f"Invalid permission row: {row}")
            dims = tuple(x.strip().lower() for x in row.get("allowed_dimensions", "").split(";") if x.strip())
            if not dims or set(dims) - DIMENSIONS:
                raise ValueError(f"Invalid or empty dimensions for {role}/{metric}")
            grain = row.get("metric_grain", "").strip().lower()
            org_key = row.get("org_key_column", "").strip()
            group_col = row.get("group_size_column", "").strip()
            raw_min = row.get("minimum_group_size", "").strip()
            privacy_mode = row.get("privacy_mode", "none").strip().lower() or "none"
            if grain not in GRAINS or not org_key:
                raise ValueError(f"Missing or invalid metric grain/key for {role}/{metric}")
            if privacy_mode not in PRIVACY_MODES:
                raise ValueError(f"Invalid privacy mode for {role}/{metric}")
            minimum = int(raw_min) if raw_min else None
            if minimum is not None and minimum < 1:
                raise ValueError(f"Minimum group size must be positive for {role}/{metric}")
            if privacy_mode == "group_count" and (not group_col or minimum is None):
                raise ValueError(f"group_count requires group_size_column and minimum_group_size for {role}/{metric}")
            if privacy_mode == "governed_view" and minimum is None:
                raise ValueError(f"governed_view requires a documented threshold for {role}/{metric}")
            if "team" in dims and grain != "team":
                raise ValueError(f"Team dimension cannot be granted for non-team metric {role}/{metric}")
            if "department" in dims and grain == "company":
                raise ValueError(f"Department dimension cannot be granted for company-grain metric {role}/{metric}")
            key = (role, metric)
            if key in result:
                raise ValueError(f"Duplicate permission row: {role}/{metric}")
            result[key] = Permission(role, metric, dims, minimum, grain, org_key, group_col, privacy_mode)
    return result

def authorize_metric(user, metric_id, permissions):
    permission = permissions.get((user.role, metric_id.upper()))
    if permission is None:
        raise PermissionError("This metric is not authorised for your role.")
    return permission

def authorize_dimension(user, permission, dimension):
    dimension = dimension.strip().lower()
    if dimension not in permission.dimensions:
        raise PermissionError("This dimension is not authorised for your role and metric.")
    if dimension == "department" and user.role == "MANAGER" and not user.department_id:
        raise PermissionError("Manager has no trusted department assignment.")
    if dimension == "team" and user.role == "MANAGER" and not user.team_ids:
        raise PermissionError("Manager has no trusted team assignment.")
    return dimension
