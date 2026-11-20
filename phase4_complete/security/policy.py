"""Fail-closed, data-driven role/metric/dimension authorization."""
from dataclasses import dataclass
import csv

ROLES = {"ADMIN", "HR", "MANAGER", "EXECUTIVE"}

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

def load_permissions(path):
    result = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            role, metric = row["role"].strip().upper(), row["metric_id"].strip().upper()
            if role not in ROLES or not metric:
                raise ValueError(f"Invalid permission row: {row}")
            dims = tuple(x.strip().lower() for x in row.get("allowed_dimensions", "").split(";") if x.strip())
            raw_min = row.get("minimum_group_size", "").strip()
            result[(role, metric)] = Permission(role, metric, dims, int(raw_min) if raw_min else None)
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
