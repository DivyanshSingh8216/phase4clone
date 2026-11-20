import pytest
from security.policy import Principal, Permission, authorize_metric, authorize_dimension
from security.privacy import check_group_size, suppress_rows

def test_metric_permission_is_fail_closed():
    p = Principal("u1", "MANAGER", "D01", ("T01",))
    with pytest.raises(PermissionError):
        authorize_metric(p, "M01", {})

def test_dimension_permission_is_enforced():
    p = Principal("u1", "HR")
    permission = Permission("HR", "M27", ("department",), 10)
    assert authorize_dimension(p, permission, "department") == "department"
    with pytest.raises(PermissionError):
        authorize_dimension(p, permission, "team")

@pytest.mark.parametrize("n", [None, 0, 1, 2, 3, 9])
def test_small_or_unknown_groups_are_withheld(n):
    assert not check_group_size(n, 10).allowed

def test_threshold_boundary_is_inclusive():
    assert check_group_size(10, 10).allowed

def test_suppression_does_not_return_small_group_values():
    rows = [{"team":"T1","count":3,"value":92.0},{"team":"T2","count":14,"value":88.0}]
    safe, withheld = suppress_rows(rows, "count", 10)
    assert safe == [{"team":"T2","count":14,"value":88.0}]
    assert withheld == 1
