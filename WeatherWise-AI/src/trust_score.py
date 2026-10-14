"""Transparent dataset trust score based on measurable quality checks."""
import pandas as pd
from .data_validation import validate_dataset

def calculate_trust_score(df: pd.DataFrame) -> dict:
    """Score = 60% completeness + 20% uniqueness + 20% parseability of date-like columns.
    If no date-like columns exist, the date component is neutral (100), not penalized.
    Unusual numeric values are reported separately and never automatically treated as errors.
    """
    if df.empty or len(df.columns)==0:
        return {"score":0,"completeness_pct":0,"duplicate_rows":0,"missing_cells":0,"invalid_date_values":0,"components":{"completeness":0,"uniqueness":0,"date_parseability":0},"formula":"0.60 × completeness + 0.20 × uniqueness + 0.20 × date parseability","recommendations":["Upload a dataset with at least one row and one column."]}
    validation=validate_dataset(df)
    total=df.shape[0]*df.shape[1]
    completeness=100*(1-validation["missing_cells"]/total) if total else 0
    uniqueness=100*(1-validation["duplicate_rows"]/max(len(df),1))
    dates=validation["date_candidates"]
    invalid_dates=sum(x["invalid"] for x in dates)
    date_total=sum(x["valid"]+x["invalid"] for x in dates)
    date_score=100*(1-invalid_dates/date_total) if date_total else 100
    score=round(max(0,min(100,.60*completeness+.20*uniqueness+.20*date_score)))
    rec=[]
    if validation["missing_cells"]: rec.append("Review missing cells and choose a documented handling strategy.")
    if validation["duplicate_rows"]: rec.append("Inspect duplicate rows before removing them.")
    if invalid_dates: rec.append("Correct or explicitly exclude unparseable values in date-like columns.")
    if not rec: rec.append("No missing cells, duplicate rows, or invalid date-like values were detected by these checks.")
    return {"score":score,"completeness_pct":round(completeness,2),"duplicate_rows":validation["duplicate_rows"],"missing_cells":validation["missing_cells"],"invalid_date_values":invalid_dates,"components":{"completeness":round(completeness,2),"uniqueness":round(uniqueness,2),"date_parseability":round(date_score,2)},"formula":"0.60 × completeness + 0.20 × uniqueness + 0.20 × date parseability","recommendations":rec,"note":"This score measures selected structural quality checks, not meteorological truth or forecast accuracy."}
