import pytest
from access_control import principal, department_filter, is_suppressed

def test_executive_only_company():
    p=principal("executive")
    assert department_filter(p,"D01")==("company",None)

def test_manager_locked_to_assigned_department():
    p=principal("MANAGER","D03")
    assert department_filter(p,None)==("department","D03")
    with pytest.raises(PermissionError):
        department_filter(p,"D04")

def test_hr_all_departments_not_company_total():
    p=principal("HR")
    assert department_filter(p,None)==("all",None)
    assert department_filter(p,"D02")==("department","D02")

def test_manager_requires_trusted_department():
    with pytest.raises(PermissionError):
        principal("MANAGER")

def test_unknown_role_denied():
    with pytest.raises(PermissionError):
        principal("PUBLIC")

def test_suppression_helper():
    assert is_suppressed(123,4,5)
    assert not is_suppressed(123,5,5)
    assert not is_suppressed(None,1,5)
