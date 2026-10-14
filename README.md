# 🌦️ WeatherWise AI

### Intelligent Weather Data Analysis & Visualization Assistant

WeatherWise AI is a Python-based interactive dashboard that helps users explore weather datasets, assess data quality, identify statistical anomalies, visualize patterns, and generate analysis reports.

## ✨ Features

- **Interactive Dashboard:** View dataset summaries, column types, and key metrics.
- **Data Visualization:** Explore distributions, trends, and correlations using Plotly.
- **Data Quality & Trust Score:** Inspect missing values, duplicate rows, and validation findings.
- **Anomaly Detection:** Identify unusual numeric observations using the Interquartile Range (IQR) method.
- **AI Assistant:** Ask questions about your dataset using local Pandas-based analysis.
- **Optional Hosted AI:** Generate explanations using a configured AI provider.
- **Data Cleaning:** Preview cleaning operations and export the resulting dataset.
- **Reports & Export:** Download analysis summaries and supported PDF and CSV reports.
- **Voice Output:** Use browser speech synthesis to read the latest assistant answer aloud.

## 🛠️ Technology Stack

- Python
- Streamlit
- Pandas and NumPy
- Plotly
- OpenAI / Anthropic integrations (optional)
- ReportLab
- Git and GitHub

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/arshiyashaik2223-commits/WeatherWise-AI.git
cd WeatherWise-AI
```

### 2. Create and activate a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the application

```powershell
streamlit run WeatherWise-AI/app.py
```

Streamlit will display a local URL in your terminal. Open that URL in your browser.

## 📁 Project Structure

```text
WeatherWise-AI/
├── README.md
├── requirements.txt
└── WeatherWise-AI/
    ├── app.py
    ├── data/
    │   └── sample_weather_data.csv
    ├── docs/
    │   ├── INSTALLATION.md
    │   ├── PROJECT_ARCHITECTURE.md
    │   └── USER_GUIDE.md
    ├── reports/
    ├── src/
    │   ├── ai_assistant.py
    │   ├── anomaly_detection.py
    │   ├── data_cleaning.py
    │   ├── data_loader.py
    │   ├── data_validation.py
    │   ├── report_generator.py
    │   ├── trust_score.py
    │   ├── visualizations.py
    │   └── weather_analysis.py
    └── tests/
```

## 🤖 AI Assistant

The application supports local, dataset-based question answering without an AI API key. Hosted AI explanations are optional and require a configured provider API key.

Do not commit API keys, passwords, or `.env` files to GitHub.

## 📚 Documentation

Detailed documentation is available in the `WeatherWise-AI/docs/` directory:

- [Installation Guide](WeatherWise-AI/docs/INSTALLATION.md)
- [Project Architecture](WeatherWise-AI/docs/PROJECT_ARCHITECTURE.md)
- [User Guide](WeatherWise-AI/docs/USER_GUIDE.md)

## ⚠️ Limitations

WeatherWise AI analyzes the weather data supplied by the user. It does not independently forecast future weather, and statistical anomalies are review candidates rather than confirmed errors.

## 👩‍💻 Author

**B.S. Arshiya**

B.Tech — Computer Science and Engineering

## 📄 License

See the [LICENSE](WeatherWise-AI/LICENSE) file for license details.
