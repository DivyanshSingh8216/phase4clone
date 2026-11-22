from pathlib import Path

import pytest

from security.policy import (
    Principal, authorize_metric, authorize_dimension, load_permissions
)
from security.privacy import check_group_size

CONFIG = Path(__file__).resolve().parents[1] / "config"


def test_permission_registry_contains_all_28_metrics_for_admin():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    admin_metrics = {metric for role, metric in permissions if role == "ADMIN"}
    assert admin_metrics == {f"M{i:02d}" for i in range(1, 29)}


def test_hr_and_manager_have_distinct_metric_access():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    hr_metrics = {metric for role, metric in permissions if role == "HR"}
    manager_metrics = {metric for role, metric in permissions if role == "MANAGER"}
    assert hr_metrics == {*[f"M{i:02d}" for i in range(1, 16)], "M27", "M28"}
    assert manager_metrics == {
        *[f"M{i:02d}" for i in range(1, 7)],
        *[f"M{i:02d}" for i in range(9, 16)],
        "M24",
    }


def test_manager_cannot_access_another_roles_or_unassigned_metrics():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    manager = Principal("demo_manager_d01", "MANAGER", "D01", ("T01", "T02"))
    with pytest.raises(PermissionError):
        authorize_metric(manager, "M27", permissions)
    with pytest.raises(PermissionError):
        authorize_metric(manager, "M16", permissions)


def test_manager_without_department_or_team_scope_is_denied():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    manager = Principal("unscoped", "MANAGER")
    department_permission = authorize_metric(manager, "M01", permissions)
    team_permission = authorize_metric(manager, "M24", permissions)
    with pytest.raises(PermissionError):
        authorize_dimension(manager, department_permission, "department")
    with pytest.raises(PermissionError):
        authorize_dimension(manager, team_permission, "team")


def test_hr_cannot_drill_department_metric_to_team():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    hr = Principal("demo_hr", "HR")
    permission = authorize_metric(hr, "M27", permissions)
    assert permission.metric_grain == "department"
    assert permission.minimum_group_size == 10
    assert authorize_dimension(hr, permission, "department") == "department"
    with pytest.raises(PermissionError):
        authorize_dimension(hr, permission, "team")


def test_privacy_threshold_boundary_and_missing_values():
    assert not check_group_size(9, 10).allowed
    assert check_group_size(10, 10).allowed
    assert not check_group_size(None, 10).allowed
    assert not check_group_size(10, None).allowed
