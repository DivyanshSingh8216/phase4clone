import pandas as pd

def apply_suppression(frame: pd.DataFrame, *, group_size_column: str, threshold: int | None, value_columns: list[str]):
    out=frame.copy()
    if threshold is None:
        for c in value_columns:
            if c in out: out[c]=None
        out['privacy_status']='SUPPRESSED_THRESHOLD_UNDEFINED'
        return out
    if group_size_column not in out: raise ValueError('Privacy denominator is missing: '+group_size_column)
    sizes=pd.to_numeric(out[group_size_column],errors='coerce')
    safe=sizes.notna() & sizes.ge(int(threshold))
    for c in value_columns:
        if c in out: out.loc[~safe,c]=None
    out['privacy_status']=safe.map({True:'RELEASED',False:'SUPPRESSED_SMALL_GROUP'})
    return out.drop(columns=[group_size_column])

def reject_complementary_disclosure(has_total: bool, has_suppressed_children: bool):
    if has_total and has_suppressed_children: raise PermissionError('Total could reveal suppressed subgroup values.')