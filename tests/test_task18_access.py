from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PHASE4 = ROOT / "phase4_complete"
sys.path.insert(0, str(PHASE4))

from security.policy import Principal, load_permissions, authorize_metric, authorize_dimension
from security.privacy import check_group_size


def _permissions():
    return load_permissions(PHASE4 / "config" / "metric_permissions.csv")


def test_all_demo_roles_have_approved_metric_access():
    permissions = _permissions()
    for role in ("ADMIN", "HR", "MANAGER", "EXECUTIVE"):
        assert any(key[0] == role for key in permissions), f"{role} has no metric grants"


def test_admin_and_executive_company_metrics_are_company_only():
    permissions = _permissions()
    company_metrics = {"M16", "M17", "M18", "M21", "M22"}
    for role in ("ADMIN", "EXECUTIVE"):
        granted = {metric for (r, metric) in permissions if r == role}
        assert granted == company_metrics | ({"M27"} if role == "ADMIN" else set())
        for metric in company_metrics:
            permission = authorize_metric(Principal("demo", role), metric, permissions)
            assert permission.metric_grain == "company"
            assert permission.dimensions == ("company",)


def test_hr_department_access_has_minimum_group_threshold():
    permission = authorize_metric(Principal("demo_hr", "HR"), "M27", _permissions())
    assert permission.dimensions == ("department",)
    assert permission.minimum_group_size == 10
    assert permission.privacy_mode == "governed_view"


def test_manager_department_access_is_limited_to_assigned_scope():
    manager = Principal("demo_manager_d01", "MANAGER", "D01", ("T01", "T02"))
    permission = authorize_metric(manager, "M27", _permissions())
    assert authorize_dimension(manager, permission, "department") == "department"
    assert permission.minimum_group_size == 10
    assert manager.department_id == "D01"
    assert set(manager.team_ids) == {"T01", "T02"}


def test_small_groups_are_withheld_and_threshold_boundary_is_allowed():
    for size in (1, 2, 9):
        assert not check_group_size(size, 10).allowed
    assert check_group_size(10, 10).allowed


def test_unknown_or_unauthorised_metric_fails_closed():
    permissions = _permissions()
    manager = Principal("demo_manager_d01", "MANAGER", "D01", ("T01", "T02"))
    try:
        authorize_metric(manager, "M16", permissions)
    except PermissionError:
        pass
    else:
        raise AssertionError("Manager unexpectedly received company-only metric M16")
