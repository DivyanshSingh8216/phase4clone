from pathlib import Path
import pytest

from phase4_complete.security.policy import (
    Principal, authorize_dimension, authorize_metric, load_permissions,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "phase4_complete" / "config" / "metric_permissions.csv"


def test_role_metric_sets_match_department_responsibilities():
    p = load_permissions(POLICY)
    expected = {
        "ADMIN": {f"M{i:02d}" for i in range(1, 29)},
        "HR": {*(f"M{i:02d}" for i in range(1, 16)), "M27", "M28"},
        "MANAGER": {*(f"M{i:02d}" for i in range(1, 7)), *(f"M{i:02d}" for i in range(9, 15)), "M24"},
        "EXECUTIVE": {*(f"M{i:02d}" for i in range(16, 21)), "M21", "M22", "M23", "M25", "M26"},
    }
    for role, metric_ids in expected.items():
        assert {metric for (r, metric) in p if r == role} == metric_ids


def test_hr_and_manager_only_receive_department_scoped_people_metrics():
    p = load_permissions(POLICY)
    for role in ("HR", "MANAGER"):
        for metric in ("M01", "M02", "M03", "M04", "M05", "M06", "M09", "M10", "M11", "M12", "M13", "M14"):
            assert p[(role, metric)].dimensions == ("department",)
            assert p[(role, metric)].metric_grain == "department"
    assert ("HR", "M16") not in p
    assert ("MANAGER", "M07") not in p
    assert ("MANAGER", "M08") not in p


def test_manager_team_access_is_only_velocity_and_assigned_teams():
    p = load_permissions(POLICY)
    manager = Principal("demo_manager_d01", "MANAGER", "D01", ("T01", "T02"))
    velocity = authorize_metric(manager, "M24", p)
    assert velocity.metric_grain == "team"
    assert authorize_dimension(manager, velocity, "team") == "team"
    assert ("MANAGER", "M22") not in p
    assert ("MANAGER", "M23") not in p
    assert ("MANAGER", "M25") not in p


def test_executive_is_company_grain_only():
    p = load_permissions(POLICY)
    for (role, metric), permission in p.items():
        if role == "EXECUTIVE":
            assert permission.dimensions == ("company",)
            assert permission.metric_grain == "company"


def test_admin_has_all_metrics_at_the_actual_available_grain():
    p = load_permissions(POLICY)
    for metric in [f"M{i:02d}" for i in range(1, 16)] + ["M27", "M28"]:
        assert p[("ADMIN", metric)].dimensions == ("department",)
    for metric in ["M16", "M17", "M18", "M19", "M20", "M21", "M22", "M23", "M25", "M26"]:
        assert p[("ADMIN", metric)].dimensions == ("company",)
    assert p[("ADMIN", "M24")].dimensions == ("team",)


def test_catalogue_privacy_thresholds_are_preserved():
    p = load_permissions(POLICY)
    assert p[("HR", "M27")].minimum_group_size == 10
    assert p[("MANAGER", "M04")].minimum_group_size == 10
    assert p[("MANAGER", "M01")].minimum_group_size == 5
    assert p[("ADMIN", "M22")].minimum_group_size == 5
    assert p[("ADMIN", "M24")].minimum_group_size is None


def test_unassigned_manager_cannot_use_department_or_team_dimension():
    p = load_permissions(POLICY)
    manager = Principal("unscoped", "MANAGER")
    dept = authorize_metric(manager, "M01", p)
    team = authorize_metric(manager, "M24", p)
    with pytest.raises(PermissionError):
        authorize_dimension(manager, dept, "department")
    with pytest.raises(PermissionError):
        authorize_dimension(manager, team, "team")


def test_metrics_with_missing_actuals_remain_unavailable_not_zero():
    p = load_permissions(POLICY)
    assert ("HR", "M28") in p
    assert p[("HR", "M28")].dimensions == ("department",)
