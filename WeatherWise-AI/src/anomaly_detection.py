"""Explainable IQR anomaly detection for numeric columns."""
import pandas as pd

def detect_anomalies(df: pd.DataFrame, column: str, multiplier: float=1.5) -> pd.DataFrame:
    if column not in df.columns: raise ValueError(f"Column '{column}' does not exist.")
    numeric=pd.to_numeric(df[column], errors="coerce")
    valid=numeric.dropna()
    if len(valid)<4: return pd.DataFrame(columns=["row_index","value","method","reason"])
    q1,q3=valid.quantile([.25,.75]); iqr=q3-q1
    if pd.isna(iqr) or iqr==0: return pd.DataFrame(columns=["row_index","value","method","reason"])
    low,high=q1-multiplier*iqr,q3+multiplier*iqr
    mask=numeric.notna() & ((numeric<low)|(numeric>high))
    date_col=next((c for c in df.columns if any(x in str(c).lower() for x in ("date","time","timestamp"))),None)
    result=pd.DataFrame({"row_index":df.index[mask].astype(str),"value":numeric[mask].values,"method":"IQR (1.5 × IQR)","reason":[f"Outside IQR fences [{low:.4g}, {high:.4g}]" for _ in range(int(mask.sum()))]})
    if date_col:
        result.insert(1,"date",df.loc[mask,date_col].astype(str).values)
    return result.reset_index(drop=True)
