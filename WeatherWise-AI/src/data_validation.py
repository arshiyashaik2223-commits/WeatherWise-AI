"""Dataset validation without assuming fixed weather column names."""
import pandas as pd

def validate_dataset(df: pd.DataFrame) -> dict:
    issues=[]
    if df.empty: issues.append({"severity":"error","message":"Dataset has no rows."})
    if df.columns.duplicated().any(): issues.append({"severity":"error","message":"Duplicate column names were detected."})
    missing=int(df.isna().sum().sum())
    duplicates=int(df.duplicated().sum())
    if missing: issues.append({"severity":"warning","message":f"{missing} missing cell(s) across {int((df.isna().sum()>0).sum())} column(s)."})
    if duplicates: issues.append({"severity":"warning","message":f"{duplicates} duplicate row(s)."})
    numeric=list(df.select_dtypes(include="number").columns)
    invalid_numeric={}
    for col in df.columns:
        if df[col].dtype == object:
            nonblank=df[col].notna() & df[col].astype(str).str.strip().ne("")
            converted=pd.to_numeric(df.loc[nonblank,col], errors="coerce")
            bad=int(converted.isna().sum())
            if bad and len(nonblank): invalid_numeric[str(col)]=bad
    for col,n in invalid_numeric.items(): issues.append({"severity":"info","message":f"Column '{col}' has {n} non-numeric text value(s); it may be categorical."})
    date_candidates=[]
    for col in df.columns:
        if any(word in str(col).lower() for word in ("date","time","timestamp")):
            parsed=pd.to_datetime(df[col], errors="coerce")
            date_candidates.append({"column":str(col),"valid":int(parsed.notna().sum()),"invalid":int((df[col].notna() & parsed.isna()).sum())})
            bad=int((df[col].notna() & parsed.isna()).sum())
            if bad: issues.append({"severity":"warning","message":f"Date-like column '{col}' contains {bad} unparseable value(s)."})
    return {"rows":len(df),"columns":len(df.columns),"missing_cells":missing,"duplicate_rows":duplicates,"numeric_columns":list(map(str,numeric)),"date_candidates":date_candidates,"issues":issues}
