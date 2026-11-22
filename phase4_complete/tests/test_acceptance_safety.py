from pathlib import Path
from security.policy import load_permissions, Principal, authorize_metric, authorize_dimension
from security.privacy import check_group_size, suppress_rows
CONFIG = Path(__file__).resolve().parents[1] / "config"

def test_permission_registry_is_valid_and_fail_closed():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    assert set(permissions) == {("EXECUTIVE","M16"),("EXECUTIVE","M17"),("EXECUTIVE","M18"),("EXECUTIVE","M21"),("EXECUTIVE","M22"),("HR","M27")}
    for role in ("ADMIN","MANAGER"):
        assert not [p for (r, _), p in permissions.items() if r == role]

def test_company_metric_cannot_be_drilled_to_department_or_team():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    user = Principal("demo_executive","EXECUTIVE")
    permission = authorize_metric(user,"M16",permissions)
    assert authorize_dimension(user,permission,"company") == "company"
    for dimension in ("department","team"):
        try: authorize_dimension(user,permission,dimension)
        except PermissionError: pass
        else: raise AssertionError(f"Unapproved {dimension} drilldown must be denied")

def test_manager_without_grants_is_denied():
    permissions = load_permissions(CONFIG / "metric_permissions.csv")
    try: authorize_metric(Principal("manager_without_scope","MANAGER"),"M16",permissions)
    except PermissionError: pass
    else: raise AssertionError("Unapproved manager metric access must be denied")

def test_small_or_unknown_groups_are_withheld():
    for n in (None,1,2,9): assert not check_group_size(n,10).allowed
    assert check_group_size(10,10).allowed
    assert not check_group_size(10,None).allowed

def test_suppression_happens_before_rows_are_returned():
    rows=[{"department":"D01","count":2,"value":12},{"department":"D02","count":12,"value":30}]
    safe, withheld=suppress_rows(rows,"count",10)
    assert safe == [{"department":"D02","count":12,"value":30}]
    assert withheld == 1