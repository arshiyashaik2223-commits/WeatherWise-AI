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
    """Answer common weather-data questions using local Pandas analysis."""
    from difflib import get_close_matches
    import re

    q = question.lower().strip()
    q = re.sub(r"[^\w\s]", " ", q)
    q = re.sub(r"\s+", " ", q)

    if not q:
        return "Please enter a question about your weather dataset."

    # Normalize common spelling mistakes.
    words = q.split()
    corrected = []
    for word in words:
        if word in ("tempertature", "tempertaure", "temprature"):
            word = "temperature"
        corrected.append(word)
    q = " ".join(corrected)

    numeric = list(df.select_dtypes(include="number").columns)
    columns = list(df.columns)

    # Dataset overview.
    if any(w in q for w in (
        "columns", "dataset", "available", "overview",
        "information", "data summary"
    )):
        return (
            f"Your dataset contains {len(df)} rows and "
            f"{len(columns)} columns. "
            f"Columns: {', '.join(map(str, columns))}. "
            f"Numeric columns: {', '.join(map(str, numeric)) or 'none'}."
        )

    # Missing values.
    if any(w in q for w in ("missing", "null", "empty values")):
        counts = df.isna().sum()
        found = counts[counts > 0]
        if found.empty:
            return "No missing cells were detected in the current dataset."
        return "Missing cells: " + "; ".join(
            f"{col}: {count}" for col, count in found.items()
        )

    # Duplicate rows.
    if "duplicate" in q:
        return f"The dataset contains {int(df.duplicated().sum())} duplicate row(s)."

    if not numeric:
        return "There are no numeric columns available for statistical analysis."

    # Match a column by its name or common weather-related aliases.
    aliases = {
        "temperature": ["temperature", "temp", "temperature_c", "temp c"],
        "humidity": ["humidity", "humidity_pct", "humidity percent"],
        "rainfall": ["rainfall", "rain", "rainfall_mm", "precipitation"],
        "wind": ["wind", "wind speed", "wind_speed_kmh"],
        "pressure": ["pressure", "air pressure", "pressure_hpa"],
    }

    matched_col = None

    for col in columns:
        col_name = str(col).lower().replace("_", " ")
        if col_name in q and col in numeric:
            matched_col = col
            break

    if matched_col is None:
        for key, terms in aliases.items():
            if any(term in q for term in terms):
                candidates = [
                    col for col in numeric
                    if key in str(col).lower()
                    or any(term.replace(" ", "_") in str(col).lower()
                           for term in terms)
                ]
                if candidates:
                    matched_col = candidates[0]
                    break

    # Try a gentle typo match against numeric column names.
    if matched_col is None:
        for word in words:
            candidates = get_close_matches(
                word,
                [str(col).lower().replace("_", " ") for col in numeric],
                n=1,
                cutoff=0.78,
            )
            if candidates:
                matched_col = next(
                    col for col in numeric
                    if str(col).lower().replace("_", " ") == candidates[0]
                )
                break

    # Understand requests for a general explanation of a weather measurement.
    general_question = any(
        phrase in q for phrase in (
            "what is", "what does", "explain", "define", "meaning of"
        )
    )

    if matched_col is None and general_question:
        if "temperature" in q or "temp" in q:
            matched_col = next(
                (c for c in numeric if "temperature" in str(c).lower()
                 or "temp" in str(c).lower()),
                None,
            )

    if matched_col is None:
        statistic_words = (
            "average", "mean", "maximum", "minimum", "highest",
            "lowest", "median", "summary", "summarize", "max", "min"
        )
        if any(word in q for word in statistic_words):
            if len(numeric) == 1:
                matched_col = numeric[0]
            else:
                return (
                    "Which measurement do you mean? Try temperature, "
                    "humidity, rainfall, wind speed, or pressure."
                )
        else:
            return (
                "I can explain weather measurements and calculate statistics. "
                "Try asking 'What is temperature?', 'What is the average "
                "temperature?', or 'What was the highest rainfall?'"
            )

    col = matched_col
    series = pd.to_numeric(df[col], errors="coerce").dropna()

    if series.empty:
        return f"Column '{col}' has no valid numeric observations."

    average_requested = any(
        word in q for word in ("average", "mean", "avg")
    )
    maximum_requested = any(
        word in q for word in ("maximum", "highest", "max")
    )
    minimum_requested = any(
        word in q for word in ("minimum", "lowest", "min")
    )
    median_requested = "median" in q
    correlation_requested = "correlation" in q

    if correlation_requested:
        if len(numeric) < 2:
            return "At least two numeric columns are needed for correlation."
        return (
            "Pairwise numeric correlations (Pearson):\n"
            + df[numeric].corr().round(3).to_string()
            + "\nCorrelation does not prove causation."
        )

    if average_requested:
        return (
            f"The average of '{col}' is {series.mean():.4g}, "
            f"calculated from {len(series)} valid observations."
        )

    if maximum_requested:
        return f"The highest value of '{col}' is {series.max():.4g}."

    if minimum_requested:
        return f"The lowest value of '{col}' is {series.min():.4g}."

    if median_requested:
        return f"The median of '{col}' is {series.median():.4g}."

    # A general question such as "What is temperature?"
    if general_question:
        explanations = {
            "temperature": (
                "Temperature measures how hot or cold the air is. "
                "Your dataset records it in degrees Celsius (°C)."
            ),
            "humidity": (
                "Humidity describes the amount of moisture in the air. "
                "This dataset records relative humidity as a percentage."
            ),
            "rainfall": (
                "Rainfall measures the amount of rain received, typically "
                "in millimetres (mm)."
            ),
            "wind": (
                "Wind speed measures how fast the air is moving. "
                "Your dataset records it in kilometres per hour (km/h)."
            ),
            "pressure": (
                "Air pressure is the pressure exerted by the atmosphere. "
                "Your dataset records it in hectopascals (hPa)."
            ),
        }

        name = str(col).lower()
        explanation = next(
            (text for key, text in explanations.items() if key in name),
            f"'{col}' is a numeric measurement in your dataset.",
        )

        return (
            f"{explanation}\n\n"
            f"Your data contains {len(series)} valid observations. "
            f"Average: {series.mean():.4g}; "
            f"minimum: {series.min():.4g}; "
            f"maximum: {series.max():.4g}."
        )

    return (
        f"Summary for '{col}': count={len(series)}, "
        f"mean={series.mean():.4g}, median={series.median():.4g}, "
        f"min={series.min():.4g}, max={series.max():.4g}."
    )
