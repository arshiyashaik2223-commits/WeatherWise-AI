"""Safe loading and basic profiling for CSV and Excel datasets."""
from pathlib import Path
from io import BytesIO
import pandas as pd

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

def load_dataset(source, filename: str | None = None) -> pd.DataFrame:
    """Load a path or uploaded file-like object; reject unsupported/empty inputs."""
    name = filename or getattr(source, "name", "") or (str(source) if isinstance(source, (str, Path)) else "upload.csv")
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type. Upload a CSV or Excel (.xlsx/.xls) file.")
    if isinstance(source, (str, Path)):
        if not Path(source).exists():
            raise FileNotFoundError(f"File not found: {source}")
        if Path(source).stat().st_size > MAX_UPLOAD_BYTES:
            raise ValueError("File exceeds the 25 MB limit.")
        stream = source
    else:
        data = source.getvalue() if hasattr(source, "getvalue") else source.read()
        if not data:
            raise ValueError("The uploaded file is empty.")
        if len(data) > MAX_UPLOAD_BYTES:
            raise ValueError("File exceeds the 25 MB limit.")
        stream = BytesIO(data)
    try:
        if suffix == ".csv":
            df = pd.read_csv(stream, low_memory=False)
        else:
            df = pd.read_excel(stream)
    except Exception as exc:
        raise ValueError(f"Could not read this file: {exc}") from exc
    if df.empty or len(df.columns) == 0:
        raise ValueError("The file contains no usable rows or columns.")
    df.columns = [str(c).strip() for c in df.columns]
    if any(not c for c in df.columns):
        raise ValueError("Every column must have a name. Rename blank columns and try again.")
    return df

def profile_dataset(df: pd.DataFrame) -> dict:
    return {"rows": int(len(df)), "columns": int(len(df.columns)), "column_names": list(map(str, df.columns)),
            "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
            "missing_by_column": {str(k): int(v) for k, v in df.isna().sum().items()},
            "duplicate_rows": int(df.duplicated().sum()), "numeric_columns": list(df.select_dtypes(include="number").columns),
            "memory_mb": round(df.memory_usage(deep=True).sum() / (1024**2), 3)}
