# Installation

## Windows (PowerShell)
```powershell
cd path\to\WeatherWise-AI
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```
If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat`, or adjust the current-user execution policy according to your organization's rules. The dashboard works without editing `.env`.

## macOS / Linux
```bash
cd path/to/WeatherWise-AI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```
Open the local URL printed in the terminal (usually `http://localhost:8501`).

## Optional AI provider
Open `.env` in a text editor and set `WEATHERWISE_AI_PROVIDER` to `anthropic` or `openai`, then set the corresponding API key. Keep `.env` private; it is excluded by `.gitignore`. Restart Streamlit after changing environment variables. Provider usage may incur costs and sends the question plus computed summary context to that provider. Never place keys in source code or screenshots.

## Excel support
CSV support is built in. Excel reading uses `openpyxl` for `.xlsx` and `xlrd` for `.xls`.
