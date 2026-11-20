from __future__ import annotations
import csv, os
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class Principal:
    user_id: str
    email: str
    role: str
    department_id: str | None = None
    team_ids: tuple[str, ...] = ()

ROLES = {'ADMIN','HR','MANAGER','EXECUTIVE'}

def resolve_registry_identity(email: str, registry_path: Path | None = None) -> Principal:
    if not email: raise PermissionError('Authenticated email claim is missing.')
    path = registry_path or Path(os.getenv('PULSEIQ_USER_REGISTRY', Path(__file__).resolve().parents[1] / 'config' / 'demo_users.csv'))
    if not path.is_file(): raise PermissionError('Trusted user registry is missing; access denied.')
    with path.open(newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            if (row.get('email') or '').strip().casefold() == email.strip().casefold() and (row.get('enabled') or 'true').lower() == 'true':
                role = (row.get('role') or '').strip().upper()
                if role not in ROLES: raise PermissionError('Unsupported role in trusted registry.')
                dept = (row.get('department_id') or '').strip() or None
                if role == 'MANAGER' and not dept: raise PermissionError('Manager has no trusted department assignment.')
                teams = tuple(x.strip() for x in (row.get('team_ids') or '').split(';') if x.strip())
                return Principal(row.get('user_id','').strip(), email.strip(), role, dept, teams)
    raise PermissionError('Authenticated user is not assigned access in the trusted registry.')

def current_principal(st):
    if os.getenv('PULSEIQ_AUTH_MODE','development').lower() == 'production':
        if not getattr(getattr(st,'user',None),'is_logged_in',False):
            st.login(); st.stop()
        return resolve_registry_identity(getattr(st.user,'email',None))
    role = os.getenv('PULSEIQ_ROLE','').upper()
    if role not in ROLES: raise PermissionError('Set PULSEIQ_ROLE for localhost development.')
    dept = os.getenv('PULSEIQ_MANAGER_DEPARTMENT') if role == 'MANAGER' else None
    if role == 'MANAGER' and not dept: raise PermissionError('Manager simulation requires an assigned department.')
    return Principal('local-demo','local-demo@localhost',role,dept,())