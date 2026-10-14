"""Explicit, non-destructive cleaning operations."""
import pandas as pd

def clean_dataset(df: pd.DataFrame, remove_duplicates=False, missing_strategy="keep", selected_columns=None):
    """Return a cleaned copy and a short audit; original frame is never mutated."""
    out = df.copy(deep=True)
    before = len(out)
    if remove_duplicates:
        out = out.drop_duplicates().copy()
    columns = selected_columns or list(out.columns)
    if missing_strategy == "drop rows":
        out = out.dropna(subset=[c for c in columns if c in out.columns]).copy()
    elif missing_strategy in {"median", "mean", "mode"}:
        for col in columns:
            if col not in out.columns: continue
            if pd.api.types.is_numeric_dtype(out[col]):
                value = out[col].median() if missing_strategy == "median" else out[col].mean() if missing_strategy == "mean" else (out[col].mode().iloc[0] if not out[col].mode().empty else None)
            else:
                modes = out[col].mode(dropna=True)
                value = modes.iloc[0] if not modes.empty else None
            if value is not None and pd.notna(value): out[col] = out[col].fillna(value)
    elif missing_strategy != "keep":
        raise ValueError("Unknown missing-value strategy.")
    return out, {"rows_before": before, "rows_after": len(out), "rows_removed": before-len(out), "missing_strategy": missing_strategy, "duplicates_removed": int(before - len(df.drop_duplicates())) if remove_duplicates else 0}
