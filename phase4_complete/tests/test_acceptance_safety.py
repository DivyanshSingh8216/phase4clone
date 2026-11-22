from pathlib import Path

import pytest

from security.policy import (
    Principal,
    authorize_dimension,
    authorize_metric,
    load_permissions,
)
from security.privacy import check_group_size, suppress_rows

CONFIG = Path(__file__).resolve().parents[1] / "config"


def test_all_defined_metrics_are_registered_for_the_intended_roles():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    expected = {
        "ADMIN": {f"M{i:02d}" for i in range(1, 29)},
        "HR": {*(f"M{i:02d}" for i in range(1, 16)), "M27", "M28"},
        "MANAGER": {
            *(f"M{i:02d}" for i in range(1, 7)),
            *(f"M{i:02d}" for i in range(9, 16)),
            "M24",
        },
        "EXECUTIVE": {
            *(f"M{i:02d}" for i in range(16, 22)),
            "M22", "M23", "M25", "M26",
        },
    }
    for role, metric_ids in expected.items():
        actual = {metric for (r, metric) in permissions if r == role}
        assert actual == metric_ids


def test_registry_has_no_duplicate_or_unsupported_grains():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    assert len(permissions) == 69
    for permission in permissions.values():
        assert permission.metric_grain in {"company", "department", "team"}
        assert permission.dimensions == (permission.metric_grain,)


def test_manager_is_restricted_to_assigned_department_and_teams():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    manager = Principal("demo_manager_d01", "MANAGER", "D01", ("T01", "T02"))
    department_metric = authorize_metric(manager, "M01", permissions)
    team_metric = authorize_metric(manager, "M24", permissions)
    assert authorize_dimension(manager, department_metric, "department") == "department"
    assert authorize_dimension(manager, team_metric, "team") == "team"
    with pytest.raises(PermissionError):
        authorize_metric(manager, "M27", permissions)


def test_executive_only_gets_company_grain_metrics():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    executive = Principal("demo_executive", "EXECUTIVE")
    for metric_id in ("M16", "M17", "M18", "M19", "M20", "M21", "M22", "M23", "M25", "M26"):
        permission = authorize_metric(executive, metric_id, permissions)
        assert permission.dimensions == ("company",)
        assert permission.metric_grain == "company"
        with pytest.raises(PermissionError):
            authorize_dimension(executive, permission, "department")


def test_sensitive_people_metrics_keep_their_minimum_group_thresholds():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    for role in ("ADMIN", "HR", "MANAGER"):
        for metric_id in ("M01", "M02", "M03", "M07", "M08", "M09", "M10",
                          "M11", "M12", "M13", "M14", "M15"):
            permission = permissions.get((role, metric_id))
            if permission:
                expected_minimum = 10 if metric_id in {"M04", "M05", "M06"} else 5
                assert permission.privacy_mode == "governed_view"
                assert permission.minimum_group_size == expected_minimum
    for role in ("ADMIN", "HR", "MANAGER"):
        for metric_id in ("M04", "M05", "M06"):
            permission = permissions[(role, metric_id)]
            assert permission.minimum_group_size == 10


def test_small_or_unknown_groups_are_withheld_before_return():
    rows = [
        {"department": "D01", "count": 2, "value": 12},
        {"department": "D02", "count": 12, "value": 30},
    ]
    safe, withheld = suppress_rows(rows, "count", 10)
    assert safe == [{"department": "D02", "count": 12, "value": 30}]
    assert withheld == 1
    for count in (None, 1, 2, 9):
        assert not check_group_size(count, 10).allowed
    assert check_group_size(10, 10).allowed
    assert not check_group_size(10, None).allowed
