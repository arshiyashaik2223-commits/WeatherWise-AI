"""Deterministic summaries and dataset-grounded insights."""
import pandas as pd

def summarize_dataset(df: pd.DataFrame) -> dict:
    numeric=df.select_dtypes(include="number")
    stats={}
    for col in numeric.columns:
        s=numeric[col].dropna()
        if len(s): stats[str(col)]={"count":int(s.count()),"mean":float(s.mean()),"median":float(s.median()),"min":float(s.min()),"max":float(s.max()),"std":float(s.std()) if len(s)>1 else 0.0,"min_index":str(s.idxmin()),"max_index":str(s.idxmax())}
    date_info=[]
    for col in df.columns:
        if any(w in str(col).lower() for w in ("date","time","timestamp")):
            d=pd.to_datetime(df[col],errors="coerce").dropna()
            if not d.empty: date_info.append({"column":str(col),"start":d.min().isoformat(),"end":d.max().isoformat(),"valid_dates":int(len(d))})
    correlations=numeric.corr(min_periods=3).round(3).to_dict() if numeric.shape[1]>=2 else {}
    return {"rows":len(df),"columns":len(df.columns),"column_names":list(map(str,df.columns)),"numeric_stats":stats,"date_coverage":date_info,"missing_by_column":{str(c):int(n) for c,n in df.isna().sum().items()},"duplicate_rows":int(df.duplicated().sum()),"correlations":correlations}

def answer_local_question(df: pd.DataFrame, question: str) -> str:
    """Safe deterministic Q&A for common analytical questions; no generated code."""
    q=question.lower().strip(); summary=summarize_dataset(df)
    if not q: return "Enter a question about the currently loaded dataset."
    if any(w in q for w in ("columns","information","dataset","available","describe")):
        return f"The dataset has {len(df):,} rows and {len(df.columns)} columns. Columns: {', '.join(map(str,df.columns))}. Numeric columns: {', '.join(map(str,df.select_dtypes(include='number').columns)) or 'none detected'}."
    if "missing" in q or "null" in q:
        counts=df.isna().sum(); found=counts[counts>0]
        return "No missing cells were detected." if found.empty else "Missing cells by column: " + "; ".join(f"{c}: {int(n)}" for c,n in found.items())
    if "duplicate" in q: return f"There are {int(df.duplicated().sum())} duplicate row(s). Review them before removing anything."
    numeric=list(df.select_dtypes(include="number").columns)
    if not numeric: return "This dataset has no numeric columns currently recognized by Pandas, so numeric statistics cannot be calculated."
    # Resolve a named column by case-insensitive substring. Do not guess if ambiguous.
    matches=[c for c in df.columns if str(c).lower() in q and pd.api.types.is_numeric_dtype(df[c])]
    if not matches:
        matches=[c for c in numeric if str(c).lower() in q]
    if len(matches)>1: return "Your question matches multiple numeric columns: " + ", ".join(map(str,matches)) + ". Please name one column more specifically."
    col=matches[0] if matches else (numeric[0] if any(w in q for w in ("average","mean","maximum","minimum","highest","lowest","summary","summarize")) else None)
    if col is None: return "I can answer dataset overview, missing values, duplicates, and numeric summaries. For a specific statistic, include the exact numeric column name in your question."
    s=pd.to_numeric(df[col],errors="coerce").dropna()
    if s.empty: return f"Column '{col}' has no valid numeric observations."
    if any(w in q for w in ("maximum","highest","max")):
        idx=s.idxmax(); return f"The maximum of '{col}' is {s.loc[idx]:g} at row index {idx}."
    if any(w in q for w in ("minimum","lowest","minimum","min")):
        idx=s.idxmin(); return f"The minimum of '{col}' is {s.loc[idx]:g} at row index {idx}."
    if "correlation" in q and len(numeric)>=2: return "Pairwise numeric correlations (Pearson):\n"+df[numeric].corr().round(3).to_string()+"\nCorrelation is not proof of causation."
    if "average" in q or "mean" in q: return f"The average of '{col}' is {s.mean():.4g}, calculated from {len(s)} valid observations."
    return f"Summary for '{col}': count={len(s)}, mean={s.mean():.4g}, median={s.median():.4g}, min={s.min():.4g}, max={s.max():.4g}."
