"""Server-side role and minimum-group policy shared by the explorer and API."""
from dataclasses import dataclass
from typing import Optional

ROLES = {"ADMIN", "EXECUTIVE", "HR", "MANAGER"}
@dataclass(frozen=True)
class Principal:
    role: str
    department_id: Optional[str] = None

def principal(role: str, department_id: str | None = None) -> Principal:
    role = (role or "").strip().upper()
    if role not in ROLES:
        raise PermissionError("Role must be one of ADMIN, EXECUTIVE, HR, MANAGER.")
    if role == "MANAGER" and not department_id:
        raise PermissionError("Manager access requires a trusted department assignment.")
    return Principal(role, str(department_id) if department_id is not None else None)

def department_filter(user: Principal, requested: str | None = None):
    """Return (mode, department_id). Never trust a manager's requested department."""
    if user.role == "EXECUTIVE":
        return ("company", None)
    if user.role == "MANAGER":
        if requested and str(requested) != user.department_id:
            raise PermissionError("Managers may only access their assigned department.")
        return ("department", user.department_id)
    if requested:
        return ("department", str(requested))
    return ("all", None)

def is_suppressed(value, group_size, minimum_group_size):
    if value is None:
        return False
    if minimum_group_size is None or group_size is None:
        return False
    return int(group_size) < int(minimum_group_size)
