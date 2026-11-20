import csv
from pathlib import Path
ROLES={'ADMIN','HR','MANAGER','EXECUTIVE'}
DIMENSIONS={'company','department','team'}

def load_metric_policy(path: Path):
    if not path.is_file(): raise PermissionError('Metric permission registry is missing.')
    policy={}
    with path.open(newline='',encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            mid=(row.get('metric_id') or '').strip()
            if not mid: continue
            roles={x.strip().upper() for x in (row.get('allowed_roles') or '').split(';') if x.strip()}
            dims={x.strip().lower() for x in (row.get('allowed_dimensions') or '').split(';') if x.strip()}
            if not roles <= ROLES or not dims <= DIMENSIONS: raise ValueError('Invalid permission row: '+mid)
            policy[mid]={'roles':roles,'dimensions':dims,'minimum_group_size':int(row['minimum_group_size']) if row.get('minimum_group_size') else None,'status':(row.get('status') or 'active').lower()}
    return policy

def allowed_metrics(user, policy):
    return sorted(mid for mid,p in policy.items() if user.role in p['roles'] and p['status']=='active')

def require_metric(user, metric_id, policy):
    p=policy.get(metric_id)
    if not p or p['status']!='active' or user.role not in p['roles']: raise PermissionError('Metric is not authorised for this role.')
    return p

def require_dimension(user, metric_policy, dimension):
    dimension=dimension.lower()
    if dimension not in DIMENSIONS or dimension not in metric_policy['dimensions']: raise PermissionError('Dimension is not authorised for this metric and role.')
    if user.role=='EXECUTIVE' and dimension!='company': raise PermissionError('Executives may access company aggregates only.')
    if user.role=='MANAGER' and dimension=='company': raise PermissionError('Managers cannot access company-wide aggregates.')
    return dimension