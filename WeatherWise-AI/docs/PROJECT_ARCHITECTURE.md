# Project architecture

```text
CSV / Excel upload
        |
        v
src/data_loader.py ---> profile + column/type inspection
        |
        v
Pandas DataFrame (session state; original preserved during cleaning preview)
  |           |             |                 |
  v           v             v                 v
analysis   validation   IQR anomalies    clean preview
  |           |             |                 |
  +-----------+-------------+-----------------+
                      |
                      v
                Streamlit UI
                      |
           +----------+-----------+
           v          v           v
        CSV export  JSON/PDF   optional hosted AI
                               (computed context only)
```

The application intentionally does not implement weather forecasting. All statistics are computed locally with Pandas. The optional AI provider explains a compact summary and never executes generated code. Key modules: `src/weather_analysis.py` (summaries/Q&A), `src/trust_score.py` (transparent score), `src/anomaly_detection.py` (IQR flags), `src/report_generator.py` (JSON/PDF), and `app.py` (Streamlit pages).
