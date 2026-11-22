from pathlib import Path
import pytest

from security.policy import (
    Principal, authorize_metric, authorize_dimension, load_permissions
)
from security.privacy import check_group_size

CONFIG = Path(__file__).resolve().parents[1] / "config"


def test_demo_registry_is_conservative_and_role_scoped():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    assert set(permissions) == {
        ("EXECUTIVE", "M16"), ("EXECUTIVE", "M17"),
        ("EXECUTIVE", "M18"), ("EXECUTIVE", "M21"),
        ("EXECUTIVE", "M22"), ("HR", "M27"),
    }
    assert not any(role == "ADMIN" for role, _ in permissions)
    assert not any(role == "MANAGER" for role, _ in permissions)


def test_hr_m27_is_department_only_and_uses_upstream_suppression():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    hr = Principal("demo_hr", "HR")
    permission = authorize_metric(hr, "M27", permissions)
    assert permission.metric_grain == "department"
    assert permission.org_key_column == "department_id"
    assert permission.minimum_group_size == 10
    assert permission.privacy_mode == "governed_view"
    assert authorize_dimension(hr, permission, "department") == "department"
    with pytest.raises(PermissionError):
        authorize_dimension(hr, permission, "team")


def test_manager_cannot_request_unassigned_metrics():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    manager = Principal("demo_manager_d01", "MANAGER", "D01", ("T01", "T02"))
    with pytest.raises(PermissionError):
        authorize_metric(manager, "M27", permissions)


def test_company_metric_does_not_allow_department_drilldown():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    executive = Principal("demo_executive", "EXECUTIVE")
    permission = authorize_metric(executive, "M16", permissions)
    assert permission.metric_grain == "company"
    assert permission.dimensions == ("company",)
    with pytest.raises(PermissionError):
        authorize_dimension(executive, permission, "department")


def test_m27_privacy_threshold_boundary():
    assert not check_group_size(9, 10).allowed
    assert check_group_size(10, 10).allowed
