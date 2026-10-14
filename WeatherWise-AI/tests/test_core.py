import io
import pandas as pd
import pytest
from src.data_loader import load_dataset
from src.data_cleaning import clean_dataset
from src.data_validation import validate_dataset
from src.trust_score import calculate_trust_score
from src.anomaly_detection import detect_anomalies
from src.weather_analysis import summarize_dataset, answer_local_question
from src.report_generator import build_json_summary

def test_load_csv_bytes():
    result=load_dataset(io.BytesIO(b"x,y\n1,2\n"),"test.csv")
    assert result.shape==(1,2)

def test_reject_wrong_file_type():
    with pytest.raises(ValueError): load_dataset(io.BytesIO(b"abc"),"bad.txt")

def test_validation_missing_duplicates_and_dates():
    df=pd.DataFrame({"date":["2025-01-01","bad","bad","bad"],"value":[1,None,1,1]})
    result=validate_dataset(df)
    assert result["missing_cells"]==1
    assert result["duplicate_rows"]==1
    assert result["date_candidates"][0]["invalid"]==3

def test_trust_score_bounds_and_empty():
    df=pd.DataFrame({"date":["2025-01-01","2025-01-02"],"v":[1,2]})
    score=calculate_trust_score(df)
    assert 0<=score["score"]<=100
    assert calculate_trust_score(pd.DataFrame())["score"]==0

def test_anomaly_flags_outlier_and_constant_safe():
    df=pd.DataFrame({"measurement":[1,2,2,3,4,100]})
    found=detect_anomalies(df,"measurement")
    assert len(found)==1 and found.iloc[0]["value"]==100
    assert detect_anomalies(pd.DataFrame({"x":[2,2,2,2,2]}),"x").empty

def test_summary_no_numeric_and_local_answer():
    df=pd.DataFrame({"category":["a","b"]})
    assert summarize_dataset(df)["numeric_stats"]=={}
    assert "2 rows" in answer_local_question(df,"what information is available?")

def test_cleaning_non_destructive_and_json_export():
    df=pd.DataFrame({"x":[1,1,None]})
    cleaned,audit=clean_dataset(df,remove_duplicates=True,missing_strategy="median")
    assert df.isna().sum().sum()==1
    assert cleaned.isna().sum().sum()==0
    assert audit["rows_removed"]>=1
    assert b'"trust_score"' in build_json_summary(cleaned)

def test_small_dataset_anomaly_safe():
    assert detect_anomalies(pd.DataFrame({"x":[1,2,3]}),"x").empty
