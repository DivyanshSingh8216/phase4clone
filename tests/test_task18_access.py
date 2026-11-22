from pathlib import Path

from phase4_complete.security.policy import (
    Principal,
    authorize_dimension,
    authorize_metric,
    load_permissions,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "phase4_complete" / "config" / "metric_permissions.csv"


def test_policy_covers_all_28_metrics_for_admin_and_executive():
    permissions = load_permissions(POLICY)
    expected = {f"M{i:02d}" for i in range(1, 29)}
    for role in ("ADMIN", "EXECUTIVE"):
        assert {metric for (r, metric) in permissions if r == role} == expected


def test_hr_receives_people_metrics_not_payroll_or_finance_amounts():
    permissions = load_permissions(POLICY)
    actual = {metric for (role, metric) in permissions if role == "HR"}
    assert actual == {"M01", "M02", "M03", "M04", "M05", "M06", "M13", "M14", "M27"}
    assert not ({"M07", "M08", "M09", "M16", "M17"} & actual)


def test_manager_receives_only_assigned_scope_metric_set():
    permissions = load_permissions(POLICY)
    actual = {metric for (role, metric) in permissions if role == "MANAGER"}
    assert actual == {"M01", "M04", "M05", "M09", "M10", "M13", "M14", "M22", "M23", "M24", "M25"}
    manager = Principal("demo_manager_d01", "MANAGER", "D01", ("T01", "T02"))
    permission = authorize_metric(manager, "M24", permissions)
    assert authorize_dimension(manager, permission, "team") == "team"
    assert permission.metric_grain == "team"
    assert permission.dimensions == ("team",)


def test_manager_without_scope_cannot_select_department_or_team():
    permissions = load_permissions(POLICY)
    manager = Principal("unscoped", "MANAGER")
    dept_permission = authorize_metric(manager, "M01", permissions)
    team_permission = authorize_metric(manager, "M24", permissions)
    import pytest
    with pytest.raises(PermissionError):
        authorize_dimension(manager, dept_permission, "department")
    with pytest.raises(PermissionError):
        authorize_dimension(manager, team_permission, "team")


def test_people_metrics_keep_catalogue_privacy_thresholds():
    permissions = load_permissions(POLICY)
    assert permissions[("HR", "M27")].minimum_group_size == 10
    assert permissions[("HR", "M27")].privacy_mode == "governed_view"
    assert permissions[("MANAGER", "M04")].minimum_group_size == 10
    assert permissions[("MANAGER", "M01")].minimum_group_size == 5


def test_company_and_team_grain_are_not_relabelled_as_department_grain():
    permissions = load_permissions(POLICY)
    for role in ("ADMIN", "EXECUTIVE"):
        for metric in ("M16", "M17", "M18", "M19", "M20", "M21", "M26"):
            assert permissions[(role, metric)].metric_grain == "company"
            assert permissions[(role, metric)].dimensions == ("company",)
        assert permissions[(role, "M24")].metric_grain == "team"
        assert permissions[(role, "M24")].dimensions == ("team",)


def test_m28_is_catalogued_but_no_data_is_fabricated():
    permissions = load_permissions(POLICY)
    assert permissions[("ADMIN", "M28")].metric_grain == "department"
    assert permissions[("EXECUTIVE", "M28")].metric_grain == "department"
