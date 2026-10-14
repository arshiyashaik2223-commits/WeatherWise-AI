"""Helpers for choosing likely date columns without assuming a schema."""
import pandas as pd

def detect_date_columns(df):
    result=[]
    for c in df.columns:
        if any(w in str(c).lower() for w in ("date","time","timestamp")):
            parsed=pd.to_datetime(df[c],errors="coerce")
            if parsed.notna().sum() >= max(1, int(df[c].notna().sum()*.5)): result.append(c)
    return result
