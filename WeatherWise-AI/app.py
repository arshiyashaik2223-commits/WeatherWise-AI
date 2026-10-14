
"""WeatherWise AI — Interactive, Dataset-First Analysis Dashboard."""

from pathlib import Path
import json

import pandas as pd
import streamlit as st
import plotly.express as px
import streamlit.components.v1 as components
from dotenv import load_dotenv

from src.data_loader import load_dataset
from src.data_cleaning import clean_dataset
from src.data_validation import validate_dataset
from src.trust_score import calculate_trust_score
from src.anomaly_detection import detect_anomalies
from src.weather_analysis import summarize_dataset, answer_local_question
from src.ai_assistant import explain_with_ai
from src.report_generator import build_json_summary, build_pdf_report
from src.visualizations import detect_date_columns


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="WeatherWise AI",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg,
            rgba(15, 118, 110, 0.10),
            rgba(14, 165, 233, 0.06)
        );
        border: 1px solid rgba(15, 118, 110, 0.18);
        padding: 14px;
        border-radius: 14px;
    }

    .ww-hero {
        padding: 1.4rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #0f766e, #0e7490);
        color: white;
        margin-bottom: 1rem;
    }

    .ww-hero h1 {
        color: white;
        margin: 0;
    }

    .ww-hero p {
        margin: 0.4rem 0 0;
        color: #e6fffb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE AND SAMPLE DATASET
# --------------------------------------------------

SAMPLE = Path(__file__).parent / "data" / "sample_weather_data.csv"

if "original_df" not in st.session_state:
    try:
        st.session_state.original_df = pd.read_csv(SAMPLE)
    except Exception:
        st.session_state.original_df = None

if "chat" not in st.session_state:
    st.session_state.chat = []

if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = "sample_weather_data.csv"


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="ww-hero">
        <h1>🌦️ WeatherWise AI</h1>
        <p>
            Intelligent Weather Data Analysis & Visualization Assistant
            · Explore your data, validate quality, discover patterns.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SIDEBAR AND DATASET UPLOAD
# --------------------------------------------------

with st.sidebar:
    st.markdown("### 🧭 Workspace")

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "Explore & Visualize",
            "Data Quality & Trust",
            "Anomaly Detection",
            "AI Assistant",
            "Cleaning & Export",
            "Reports & Help",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.caption(
        "📁 Upload CSV / Excel · 📊 Local analytics · 🤖 Optional hosted AI"
    )

    uploaded = st.file_uploader(
        "Load a dataset",
        type=["csv", "xlsx", "xls"],
        help="Maximum 25 MB. Your file is analyzed in this app session.",
    )

    if uploaded is not None:
        try:
            new_df = load_dataset(uploaded, uploaded.name)

            st.session_state.original_df = new_df
            st.session_state.dataset_name = uploaded.name

            st.success(f"Loaded {len(new_df):,} rows")

        except Exception as exc:
            st.error(f"Could not load dataset: {exc}")

    if st.button("↺ Reset to bundled sample", use_container_width=True):
        try:
            st.session_state.original_df = pd.read_csv(SAMPLE)
            st.session_state.dataset_name = "sample_weather_data.csv"
            st.session_state.chat = []

            st.session_state.pop("cleaned_preview", None)
            st.session_state.pop("clean_audit", None)

            st.rerun()

        except Exception as exc:
            st.error(f"Could not load sample dataset: {exc}")

    st.caption(
        "Current source: "
        + st.session_state.get(
            "dataset_name",
            "bundled sample dataset",
        )
    )


# --------------------------------------------------
# DATASET PREPARATION
# --------------------------------------------------

df = st.session_state.original_df

if df is None:
    st.info("Upload a CSV or Excel dataset to get started.")
    st.stop()

if df.empty:
    st.warning("This dataset has no rows. Upload a non-empty file to continue.")
    st.stop()

summary = summarize_dataset(df)
trust = calculate_trust_score(df)
validation = validate_dataset(df)

numeric_cols = list(df.select_dtypes(include="number").columns)
date_cols = detect_date_columns(df)


# --------------------------------------------------
# REUSABLE FUNCTIONS
# --------------------------------------------------

def overview_metrics():
    """Display basic dataset indicators."""

    a, b, c, d = st.columns(4)

    a.metric("Rows", f"{len(df):,}")
    b.metric("Columns", len(df.columns))
    c.metric("Missing cells", f"{int(df.isna().sum().sum()):,}")
    d.metric("Trust Score", f"{trust['score']}/100")


def chart_filters(frame):
    """Apply an optional date filter to a dataframe."""

    if date_cols:
        chosen = st.selectbox(
            "Date column",
            date_cols,
            key="datecol",
        )

        dates = pd.to_datetime(frame[chosen], errors="coerce")

        if dates.notna().any():
            low = dates.min().date()
            high = dates.max().date()

            date_range = st.date_input(
                "Date range",
                value=(low, high),
                min_value=low,
                max_value=high,
                key="daterange",
            )

            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date, end_date = date_range

                mask = dates.dt.date.between(start_date, end_date)
                frame = frame.loc[mask].copy()

    return frame


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":
    st.subheader("Your dataset at a glance")

    overview_metrics()

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("#### Dataset preview")

        st.dataframe(
            df.head(12),
            use_container_width="stretch",
            hide_index=True,
        )

    with right:
        st.markdown("#### Column types")

        types = pd.DataFrame(
            {
                "Column": df.columns.astype(str),
                "Type": df.dtypes.astype(str).values,
                "Missing": df.isna().sum().values,
            }
        )

        st.dataframe(
            types,
            use_container_width=True,
            hide_index=True,
            height=350,
        )

    st.markdown("#### Automatic findings")

    findings = [
        f"The dataset contains **{len(df):,} rows** and "
        f"**{len(df.columns)} columns**."
    ]

    missing_count = int(df.isna().sum().sum())

    if missing_count:
        findings.append(
            f"**{missing_count} missing cells** need review."
        )
    else:
        findings.append("No missing cells were detected.")

    duplicate_count = int(df.duplicated().sum())

    if duplicate_count:
        findings.append(
            f"**{duplicate_count} duplicate rows** were detected."
        )

    if summary.get("date_coverage"):
        for date_info in summary["date_coverage"]:
            findings.append(
                f"Date coverage in **{date_info['column']}**: "
                f"{date_info['start'][:10]} to "
                f"{date_info['end'][:10]} "
                f"({date_info['valid_dates']} valid dates)."
            )

    for col in numeric_cols[:5]:
        values = df[col].dropna()

        if not values.empty:
            findings.append(
                f"**{col}** ranges from {values.min():g} to "
                f"{values.max():g}; mean {values.mean():.4g} "
                f"({len(values)} valid values)."
            )

    for finding in findings:
        st.markdown("- " + finding)

    st.caption(
        "Findings are calculated from the current dataset. "
        "No forecast is generated."
    )


# --------------------------------------------------
# EXPLORE AND VISUALIZE PAGE
# --------------------------------------------------

elif page == "Explore & Visualize":
    st.subheader("Explore & visualize")

    frame = chart_filters(df.copy())

    st.caption(
        f"Showing {len(frame):,} of {len(df):,} rows after current filters."
    )

    st.dataframe(
        frame.head(100),
        use_container_width=True,
    )

    if numeric_cols:
        col = st.selectbox("Numeric variable", numeric_cols)

        c1, c2 = st.columns(2)

        with c1:
            st.plotly_chart(
                px.histogram(
                    frame,
                    x=col,
                    title=f"Distribution of {col}",
                    marginal="box",
                ),
                use_container_width=True,
            )

        with c2:
            st.plotly_chart(
                px.box(
                    frame,
                    y=col,
                    title=f"Spread of {col}",
                ),
                use_container_width=True,
            )

        if date_cols:
            datecol = st.selectbox(
                "Date axis",
                date_cols,
                key="trend_date",
            )

            trend = frame.copy()

            trend[datecol] = pd.to_datetime(
                trend[datecol],
                errors="coerce",
            )

            trend[col] = pd.to_numeric(
                trend[col],
                errors="coerce",
            )

            trend = trend.dropna(
                subset=[datecol, col]
            ).sort_values(datecol)

            if not trend.empty:
                st.plotly_chart(
                    px.line(
                        trend,
                        x=datecol,
                        y=col,
                        title=f"{col} over time",
                        markers=True,
                    ),
                    use_container_width=True,
                )
            else:
                st.info(
                    "No valid date/value pairs for a time-series chart."
                )

        other = st.selectbox(
            "Compare with another numeric variable",
            ["(none)"] + [c for c in numeric_cols if c != col],
        )

        if other != "(none)":
            st.plotly_chart(
                px.scatter(
                    frame,
                    x=col,
                    y=other,
                    title=f"{col} vs {other}",
                ),
                use_container_width=True,
            )

        if len(numeric_cols) >= 2:
            st.markdown("#### Numeric correlation matrix")

            corr = frame[numeric_cols].corr(min_periods=2)

            st.plotly_chart(
                px.imshow(
                    corr,
                    text_auto=True,
                    color_continuous_scale="RdBu_r",
                    zmin=-1,
                    zmax=1,
                    title="Pearson correlation (not causation)",
                ),
                use_container_width=True,
            )

    else:
        st.info(
            "No numeric columns were detected. Numeric charts are unavailable."
        )

    missing = (
        df.isna()
        .sum()
        .rename("Missing cells")
        .rename_axis("Column")
        .reset_index()
    )

    if missing["Missing cells"].sum():
        st.plotly_chart(
            px.bar(
                missing[missing["Missing cells"] > 0],
                x="Column",
                y="Missing cells",
                title="Missing values by column",
            ),
            use_container_width=True,
        )


# --------------------------------------------------
# DATA QUALITY AND TRUST PAGE
# --------------------------------------------------

elif page == "Data Quality & Trust":
    st.subheader("Data quality & Weather Data Trust Score")

    st.metric(
        "Weather Data Trust Score",
        f"{trust['score']}/100",
        help=(
            "Structural data quality indicator, "
            "not proof of meteorological accuracy."
        ),
    )

    a, b, c, d = st.columns(4)

    a.metric("Completeness", f"{trust['completeness_pct']:.2f}%")
    b.metric("Missing cells", trust["missing_cells"])
    c.metric("Duplicate rows", trust["duplicate_rows"])
    d.metric("Invalid date values", trust["invalid_date_values"])

    st.markdown("#### Transparent score formula")

    st.code(
        trust["formula"]
        + "\n= 60% completeness + 20% uniqueness + 20% date parseability"
    )

    st.dataframe(
        pd.DataFrame(
            [
                {"Check": key, "Score": value, "Weight": weight}
                for (key, value), weight in zip(
                    trust["components"].items(),
                    [0.6, 0.2, 0.2],
                )
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "When no date-like column exists, date parseability is neutral (100). "
        "Extreme weather values are not automatically penalized."
    )

    st.markdown("#### Validation findings")

    if validation["issues"]:
        for issue in validation["issues"]:
            if issue["severity"] == "error":
                st.error(issue["message"])
            elif issue["severity"] == "warning":
                st.warning(issue["message"])
            else:
                st.info(issue["message"])
    else:
        st.success(
            "No structural validation warnings from the configured checks."
        )

    st.markdown("#### Missingness map")

    miss = df.isna().astype(int)

    if miss.to_numpy().sum():
        st.plotly_chart(
            px.imshow(
                miss.T,
                aspect="auto",
                title="Missing cells by column and row",
                labels={
                    "x": "Row position",
                    "y": "Column",
                    "color": "Missing",
                },
            ),
            use_container_width=True,
        )
    else:
        st.success("No missing values to visualize.")

    st.markdown("#### Recommendations")

    for item in trust["recommendations"]:
        st.markdown("- " + item)


# --------------------------------------------------
# ANOMALY DETECTION PAGE
# --------------------------------------------------

elif page == "Anomaly Detection":
    st.subheader("Explainable anomaly detection")

    if not numeric_cols:
        st.info(
            "No numeric columns are available for anomaly detection."
        )

    else:
        col = st.selectbox(
            "Select a numeric column",
            numeric_cols,
        )

        multiplier = st.slider(
            "IQR fence multiplier",
            1.0,
            3.0,
            1.5,
            0.25,
            help=(
                "Smaller values flag more observations. "
                "1.5 is a common exploratory setting."
            ),
        )

        anomalies = detect_anomalies(
            df,
            col,
            multiplier,
        )

        st.caption(
            "IQR flags values below Q1 − multiplier×IQR or above "
            "Q3 + multiplier×IQR. Flags are review candidates, "
            "not confirmed errors."
        )

        if anomalies.empty:
            st.info(
                "No anomalies flagged, or there are too few valid "
                "observations or no spread for this method."
            )

        else:
            st.metric(
                "Flagged observations",
                len(anomalies),
            )

            st.dataframe(
                anomalies,
                use_container_width=True,
                hide_index=True,
            )

            chart = df.copy()
            chart["__row__"] = chart.index.astype(str)
            chart["__value__"] = pd.to_numeric(
                chart[col],
                errors="coerce",
            )

            flagged_indices = pd.to_numeric(
                anomalies["row_index"],
                errors="coerce",
            ).dropna().astype(int)

            chart["__flag__"] = chart.index.isin(
                flagged_indices
            )

            st.plotly_chart(
                px.scatter(
                    chart,
                    x="__row__",
                    y="__value__",
                    color="__flag__",
                    title=f"IQR anomaly review: {col}",
                    labels={
                        "__row__": "Row index",
                        "__value__": col,
                        "__flag__": "Flagged",
                    },
                ),
                use_container_width=True,
            )

            st.download_button(
                "Download flagged rows CSV",
                anomalies.to_csv(index=False).encode("utf-8"),
                "weatherwise_anomalies.csv",
                "text/csv",
            )


# --------------------------------------------------
# AI ASSISTANT PAGE
# --------------------------------------------------

elif page == "AI Assistant":
    st.subheader("🤖 WeatherWise AI Assistant")

    st.write(
        "Ask questions about the uploaded dataset. Local answers use "
        "Pandas calculations. Hosted AI is optional."
    )

    examples = [
        "What information is available in this dataset?",
        "Are there missing values?",
        "Summarize the numeric columns",
        "Which values are highest and lowest?",
        "What correlations are present?",
    ]

    cols = st.columns(len(examples))

    for i, example in enumerate(examples):
        if cols[i].button(
            example,
            key=f"example_{i}",
            use_container_width=True,
        ):
            st.session_state.pending_question = example

    question = st.text_area(
        "Your question",
        value=st.session_state.pop("pending_question", ""),
        placeholder="For example: What is the average temperature?",
        height=90,
    )

    ai_mode = st.toggle(
        "Use hosted AI to explain computed results (optional API key)",
        value=False,
    )

    if st.button("Ask WeatherWise", type="primary") and question.strip():
        with st.spinner("Analyzing the current dataset…"):
            # Always calculate a local answer first.
            local_answer = answer_local_question(df, question)

            # Local Pandas analysis is the reliable fallback.
            answer = (
                "🌦️ Local AI Mode\n\n"
                f"{local_answer}"
            )

            if ai_mode:
                try:
                    hosted_answer = explain_with_ai(
                        question,
                        {
                            "summary": summary,
                            "validation": validation,
                            "trust_score": trust,
                            "local_answer": local_answer,
                        },
                    )

                    # Do not replace the local answer with a fallback notice.
                    if (
                        hosted_answer
                        and "Local AI Mode" not in hosted_answer
                        and "API key not configured" not in hosted_answer
                        and "API_KEY is not configured" not in hosted_answer
                    ):
                        answer = hosted_answer

                except Exception:
                    # If hosted AI fails, keep the useful local answer.
                    pass

            st.session_state.chat.append((question, answer))

    # Display recent conversation.
    for q, a in reversed(st.session_state.chat[-10:]):
        with st.chat_message("user"):
            st.write(q)

        with st.chat_message("assistant"):
            st.markdown(a)

    c1, c2 = st.columns(2)

    if c1.button("Clear chat"):
        st.session_state.chat = []
        st.rerun()

    if c2.button("🔊 Speak latest answer"):
        if st.session_state.chat:
            spoken = (
                st.session_state.chat[-1][1]
                .replace("`", "")
                .replace("\n", " ")
            )

            spoken_json = json.dumps(spoken, ensure_ascii=False)

            components.html(
                f"""
                <div style="font-family: sans-serif; padding: 4px;">
                    <button id="play" style="
                        padding: 10px 16px;
                        margin-right: 8px;
                        cursor: pointer;
                        border-radius: 8px;
                    ">▶ Play speech</button>

                    <button id="stop" style="
                        padding: 10px 16px;
                        cursor: pointer;
                        border-radius: 8px;
                    ">⏹ Stop</button>

                    <p id="status">
                        Click Play speech to hear the latest answer.
                    </p>
                </div>

                <script>
                    const answerText = {spoken_json};
                    const status = document.getElementById("status");
                    const playButton = document.getElementById("play");
                    const stopButton = document.getElementById("stop");

                    playButton.onclick = () => {{
                        if (!("speechSynthesis" in window)) {{
                            status.textContent =
                                "Speech is not supported by this browser.";
                            return;
                        }}

                        window.speechSynthesis.cancel();

                        const utterance =
                            new SpeechSynthesisUtterance(answerText);

                        utterance.lang = "en-IN";
                        utterance.rate = 1;

                        utterance.onstart = () => {{
                            status.textContent = "Speaking...";
                        }};

                        utterance.onend = () => {{
                            status.textContent = "Finished speaking.";
                        }};

                        utterance.onerror = (event) => {{
                            status.textContent =
                                "Speech error: " + event.error;
                        }};

                        window.speechSynthesis.speak(utterance);
                    }};

                    stopButton.onclick = () => {{
                        window.speechSynthesis.cancel();
                        status.textContent = "Speech stopped.";
                    }};
                </script>
                """,
                height=115,
            )
        else:
            st.info("Ask a question first.")

    st.caption(
        "Local mode calculates answers from your currently loaded dataset "
        "using Pandas. When enabled and configured, hosted AI receives the "
        "question and computed context. Avoid sending sensitive data to "
        "external providers unless you accept their terms."
    )


# --------------------------------------------------
# CLEANING AND EXPORT PAGE
# --------------------------------------------------

elif page == "Cleaning & Export":
    st.subheader("Optional cleaning — original data stays unchanged")

    st.info(
        "Choose operations explicitly. The current original dataset remains "
        "available until you apply changes in this session."
    )

    remove = st.checkbox("Remove exact duplicate rows")

    strategy = st.selectbox(
        "Missing-value handling",
        ["keep", "drop rows", "median", "mean", "mode"],
        help=(
            "Mean/median apply to numeric columns; "
            "mode is used for categorical columns."
        ),
    )

    selected = st.multiselect(
        "Columns to apply missing-value handling to",
        list(df.columns),
        default=list(df.columns),
    )

    if st.button("Preview cleaning", type="primary"):
        cleaned, audit = clean_dataset(
            df,
            remove,
            strategy,
            selected,
        )

        st.session_state.cleaned_preview = cleaned
        st.session_state.clean_audit = audit

    if "cleaned_preview" in st.session_state:
        cleaned = st.session_state.cleaned_preview

        st.write(st.session_state.clean_audit)

        before, after = st.columns(2)

        with before:
            st.markdown("**Before**")
            st.dataframe(
                df.head(10),
                use_container_width=True,
            )

        with after:
            st.markdown("**After preview**")
            st.dataframe(
                cleaned.head(10),
                use_container_width=True,
            )

        st.download_button(
            "Download cleaned CSV",
            cleaned.to_csv(index=False).encode("utf-8"),
            "weatherwise_cleaned.csv",
            "text/csv",
        )

        if st.button("Use cleaned data for this session"):
            st.session_state.original_df = cleaned.copy()
            st.session_state.dataset_name = "cleaned session dataset"
            st.rerun()

    st.download_button(
        "Download current dataset as CSV",
        df.to_csv(index=False).encode("utf-8"),
        "weatherwise_current_dataset.csv",
        "text/csv",
    )


# --------------------------------------------------
# REPORTS AND HELP PAGE
# --------------------------------------------------

else:
    st.subheader("Reports, help & project information")

    st.markdown("#### Download reports based on the current dataset")

    st.download_button(
        "Download JSON analysis summary",
        build_json_summary(df),
        "weatherwise_analysis.json",
        "application/json",
    )

    try:
        pdf = build_pdf_report(df)

        st.download_button(
            "Download PDF report",
            pdf,
            "weatherwise_report.pdf",
            "application/pdf",
        )

    except Exception as exc:
        st.warning(f"PDF report unavailable: {exc}")

    st.markdown("#### Voice support")

    st.write(
        "Typed chat is always available. Browser speech synthesis may read "
        "the latest answer aloud. Voice input is not currently implemented "
        "in this version."
    )

    st.markdown("#### Architecture")

    st.code(
        "Upload CSV/Excel → Data loader → Pandas validation & summaries "
        "→ Streamlit dashboard\n"
        "    ↘ IQR anomaly review\n"
        "    ↘ Optional hosted AI explanation (computed context only)\n"
        "    ↘ CSV / JSON / PDF exports"
    )

    st.markdown("#### Important limitations")

    st.markdown(
        "- This application analyzes historical observations; it does not forecast future weather.\n"
        "- Trust Score measures selected structural quality checks, not scientific correctness.\n"
        "- Statistical anomalies may be legitimate extreme events.\n"
        "- Hosted AI requires a provider key and may transmit question/context to that provider.\n"
        "- Excel support may require `openpyxl`."
    )

    st.markdown("#### Demo checklist")

    st.markdown(
        "1. Load the bundled sample or upload your own CSV.\n"
        "2. Show overview metrics and automatic findings.\n"
        "3. Explore one numeric variable and its distribution/time trend.\n"
        "4. Explain the transparent Trust Score.\n"
        "5. Run IQR anomaly detection.\n"
        "6. Ask the assistant a question with AI disabled, then optionally enable hosted AI.\n"
        "7. Preview a cleaning operation and download JSON/PDF/CSV reports.\n"
        "8. Test the speaker button in the AI Assistant."
    )

    st.markdown("#### Common evaluator questions")

    st.markdown(
        "**How is the Trust Score calculated?** "
        "60% completeness, 20% row uniqueness, 20% date parseability; "
        "no date column is neutral.\n\n"
        "**Are anomalies errors?** No. They are statistical flags for review.\n\n"
        "**Does it predict weather?** No, it analyzes historical data only.\n\n"
        "**Does the chatbot calculate statistics?** Pandas computes statistics; "
        "optional AI explains calculated context.\n\n"
        "**Can it work without an API key?** Yes, local analysis and the "
        "dashboard work without one."
    )
