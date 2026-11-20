"""Privacy guards applied before any aggregate reaches UI, API, or export."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PrivacyDecision:
    allowed: bool
    reason: str | None = None

def check_group_size(group_size, minimum_group_size):
    if group_size is None or minimum_group_size is None:
        return PrivacyDecision(False, "Group size or metric threshold is unavailable; result withheld.")
    try:
        n, k = int(group_size), int(minimum_group_size)
    except (TypeError, ValueError):
        return PrivacyDecision(False, "Group size could not be validated; result withheld.")
    if n < k:
        return PrivacyDecision(False, f"Group contains fewer than the required {k} records.")
    return PrivacyDecision(True)

def suppress_rows(rows, group_size_field, minimum_group_size):
    safe, withheld = [], 0
    for row in rows:
        if check_group_size(row.get(group_size_field), minimum_group_size).allowed:
            safe.append(row)
        else:
            withheld += 1
    return safe, withheld
