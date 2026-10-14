# 🌦️ WeatherWise AI

**Intelligent Weather Data Analysis & Visualization Assistant** — a beginner-friendly Streamlit application for exploring CSV/Excel datasets, understanding data quality, flagging statistical outliers, asking dataset questions, and exporting reports.

> Repository access note: this package was prepared as a standalone enhancement scaffold because the original GitHub repository could not be cloned from the build environment. It has not yet been merged with or verified against the original notebook/scripts. Upload the original project files to enable a safe preservation/merge pass.

## Features
- Interactive Streamlit dashboard with overview, exploration, data quality, anomaly review, assistant, cleaning/export, and help pages.
- CSV/Excel uploads (25 MB cap), data preview, type/missing/duplicate checks.
- Charts generated only when relevant columns exist; date columns are detected heuristically.
- Explainable Weather Data Trust Score: 60% completeness + 20% uniqueness + 20% date parseability. If no date-like column exists, date score is neutral (100). It is not a meteorological truth score.
- IQR anomaly detection for selected numeric columns. Flags are review candidates, not errors by definition.
- Local Pandas chatbot fallback; optional Anthropic/OpenAI explanation mode.
- Optional browser speech synthesis; typed chat remains available. Browser speech-to-text input is not implemented in this version.
- Non-destructive cleaning preview; CSV, JSON, and PDF downloads.
- Tests and beginner documentation.

## Technology stack
Python, Streamlit, Pandas, NumPy, Plotly, ReportLab, python-dotenv, pytest, and optional Anthropic/OpenAI SDKs.

## Quick start

### Windows PowerShell
```powershell
cd path\to\WeatherWise-AI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

### macOS/Linux
```bash
cd path/to/WeatherWise-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Open the local URL shown by Streamlit, normally `http://localhost:8501`. A demo dataset is bundled so the dashboard can be tried without uploading anything. It is synthetic illustrative data, not live weather.

## Optional hosted AI
Local Pandas analysis works without API credentials. For hosted explanations, edit `.env` (never commit it): set `WEATHERWISE_AI_PROVIDER=anthropic` and `ANTHROPIC_API_KEY=...`, or set provider `openai` and `OPENAI_API_KEY=...`. Optional SDKs are listed in `requirements.txt`. Provider requests may cost money and send your question plus computed context to that provider. Restart Streamlit after changing configuration.

## Dataset behavior
- Accepted extensions: `.csv`, `.xlsx`, `.xls`; maximum upload 25 MB.
- No fixed column schema is required. Numeric columns are inferred by Pandas; date-like columns are detected from names containing date/time/timestamp and then parsed.
- The app does not claim to forecast future weather.
- It does not automatically enforce physical weather limits because units and data sources vary.
- A numeric-looking text column may be treated as categorical until you clean/convert it.

## Tests
```bash
python -m pytest -q
```
Tests cover CSV loading, invalid extension, missing/duplicate/date checks, trust-score bounds, IQR outliers and constant columns, summaries, non-destructive cleaning, and JSON export. Actual execution results are listed in the delivery message; run locally too if your environment differs.

## Folder structure
```text
WeatherWise-AI/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── data_validation.py
│   ├── weather_analysis.py
│   ├── visualizations.py
│   ├── anomaly_detection.py
│   ├── trust_score.py
│   ├── ai_assistant.py
│   ├── voice_assistant.py
│   └── report_generator.py
├── data/sample_weather_data.csv
├── tests/test_core.py
└── docs/{INSTALLATION,USER_GUIDE,PROJECT_ARCHITECTURE}.md
```

## Demo guide
1. Start the app and show the sample data overview.
2. Upload your internship dataset and point out that columns are discovered dynamically.
3. Explore a numeric distribution and, if a date column exists, a trend chart.
4. Explain the Trust Score formula and caveat.
5. Flag unusual values with IQR and explain why these are not automatically errors.
6. Ask the local assistant for missing values or a column average.
7. Preview cleaning and download CSV, JSON, and PDF reports.

## Common evaluator questions
**Why Streamlit?** It gives a Python-first interactive UI with less frontend setup.  
**How is the trust score calculated?** 60% completeness, 20% uniqueness, 20% date parseability; absent date columns are neutral.  
**Are anomalies bad data?** Not necessarily; the method flags statistical extremes for review.  
**Does the assistant hallucinate numbers?** Core statistics are computed with Pandas. Hosted AI receives computed context and is instructed not to invent data, but generated explanations still need review.  
**Does it predict weather?** No. This version analyzes historical observations and makes no forecast claims.  
**Can it work offline?** The local dashboard/analysis works without an AI key, provided dependencies are installed; hosted AI requires internet.

## Future improvements
After the original repository is available: preserve its notebooks and charts, adapt module imports, add source-specific physical range rules, more robust date inference, optional evaluated forecasting, and browser-compatible speech-to-text.
