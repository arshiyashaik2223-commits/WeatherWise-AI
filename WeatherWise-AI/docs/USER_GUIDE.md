# User guide

1. Start the app with `streamlit run app.py`.
2. Use the sidebar uploader to select CSV, XLSX, or XLS (25 MB maximum). The bundled sample loads by default.
3. **Overview** shows dimensions, types, missing values, and computed findings.
4. **Explore & Visualize** lets you inspect distributions, time series when a date-like column exists, scatter plots, correlations, and missingness.
5. **Data Quality & Trust** explains the 0–100 score. It measures completeness (60%), uniqueness (20%), and date parseability (20%). With no date-like column, that component is neutral (100%). This is not a scientific validity score.
6. **Anomaly Detection** uses IQR fences. Flagged readings can be legitimate extreme weather and need human review.
7. **AI Assistant** works locally without a key for common questions. Hosted AI is optional and only explains computed context; it can still make language mistakes, so verify important conclusions.
8. **Cleaning & Export** lets you preview duplicate removal and missing-value handling before downloading. The original frame is not mutated by preview operations.
9. **Reports & Help** offers JSON and PDF reports.

Voice: spoken output uses browser speech synthesis where supported. Browser speech-to-text microphone input is not implemented in this version; type or paste questions instead. Browser speech synthesis can vary by installed voices and accessibility settings.

Privacy: uploaded data is processed by the running app. If hosted AI is enabled, question text and computed summary context are sent to the selected AI provider. Avoid sensitive data unless permitted by your policies.
