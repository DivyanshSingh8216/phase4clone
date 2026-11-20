import pandas as pd
REQUIRED={'department_id','team_id'}

def load_hierarchy(path):
    df=pd.read_csv(path,dtype=str).fillna('')
    missing=REQUIRED-set(df.columns)
    if missing: raise ValueError('Missing hierarchy columns: '+str(sorted(missing)))
    df['department_id']=df.department_id.str.strip(); df['team_id']=df.team_id.str.strip()
    df=df[(df.department_id!='')&(df.team_id!='')].drop_duplicates()
    if df.empty: raise ValueError('No valid department/team mappings.')
    if df.groupby('team_id').department_id.nunique().gt(1).any(): raise ValueError('Team maps to multiple departments.')
    return df

def departments_for(user,hierarchy):
    return [user.department_id] if user.role=='MANAGER' and user.department_id else sorted(hierarchy.department_id.unique())

def teams_for(user,hierarchy,department_id):
    if user.role=='MANAGER' and department_id!=user.department_id: raise PermissionError('Manager cannot drill into another department.')
    teams=hierarchy.loc[hierarchy.department_id==department_id,'team_id'].tolist()
    if user.role=='MANAGER' and user.team_ids: teams=[t for t in teams if t in user.team_ids]
    return sorted(teams)