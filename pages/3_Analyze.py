"""
pages/3_Analyze.py
------------------
Analysis dashboard. Creator uploads their responses CSV and
optionally their session file to restore question labels.
"""

import io
import json
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.styles import apply_global_styles
from scripts.config import make_empty_config, get_question_labels, get_freetext_questions
from scripts.preprocess import load_and_clean, split_frames
from scripts.analysis import (
    likert_summary,
    analyze_sentiment,
    sentiment_summary,
    extract_themes,
)

st.set_page_config(page_title="Analyze — Survey Studio", layout="wide")
apply_global_styles()

SCORE_COLORS = {1: "#ef4444", 2: "#f97316", 3: "#334155", 4: "#06b6d4", 5: "#00f5d4"}
SENTIMENT_COLORS = {"POSITIVE": "#00f5d4", "NEGATIVE": "#ef4444"}

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", size=12),
    title_font=dict(color="#e2e8f0", size=14),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.08)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.08)",
    ),
    margin=dict(l=0, r=0, t=40, b=0),
)

st.title("Analysis")

# ── Upload panel ──────────────────────────────────────────────────────────────
with st.expander("Upload your files", expanded=True):
    u1, u2 = st.columns(2)
    with u1:
        csv_file = st.file_uploader(
            "Responses CSV (required)",
            type="csv",
            help="Download this from the Respond page.",
        )
    with u2:
        session_file = st.file_uploader(
            "Session file (optional — restores question labels)",
            type="json",
            help="The survey_session.json you saved from the Build page.",
        )

if not csv_file:
    st.info("Upload your responses CSV above to get started.")
    st.stop()

# ── Load config ───────────────────────────────────────────────────────────────
if session_file:
    try:
        cfg = json.load(session_file)
    except Exception:
        st.warning("Could not read session file — labels will be auto-generated.")
        cfg = make_empty_config()
else:
    cfg = make_empty_config()


# ── Process data ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Processing responses…")
def process(csv_bytes: bytes, cfg_str: str):
    cfg = json.loads(cfg_str)
    csv_str = csv_bytes.decode("utf-8")
    df_raw = pd.read_csv(io.StringIO(csv_str), dtype=str)

    if not cfg.get("questions"):
        seen = {}
        for full_text in df_raw["question"].dropna().unique():
            try:
                num = int(str(full_text).split(".")[0].strip())
                text = (
                    str(full_text).split(".", 1)[1].strip()
                    if "." in str(full_text)
                    else full_text
                )
                seen[num] = text
            except (ValueError, IndexError):
                pass
        for num in sorted(seen):
            sample = df_raw[
                df_raw["question"].str.startswith(str(num) + ".")
            ]["response"].dropna()
            is_likert = sample.apply(lambda x: str(x).strip().isdigit()).mean() > 0.7
            cfg["questions"].append({
                "number": num,
                "text": seen[num],
                "type": "likert" if is_likert else "freetext",
                "label": f"Q{num}",
                "required": True,
            })
        cfg["likert_scale"] = make_empty_config()["likert_scale"]

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tf:
        json.dump(cfg, tf)
        cfg_path = tf.name

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as tf2:
        tf2.write(csv_str)
        csv_path = tf2.name

    try:
        df = load_and_clean(csv_path, cfg_path)
        likert_df, freetext_df = split_frames(df, cfg_path)
    finally:
        os.unlink(cfg_path)
        os.unlink(csv_path)

    return df, likert_df, freetext_df, cfg


cfg_str = json.dumps(cfg)
try:
    df, likert_df, freetext_df, cfg = process(csv_file.read(), cfg_str)
except SystemExit as e:
    st.error(str(e))
    st.stop()

question_labels = get_question_labels(cfg)
freetext_qs = get_freetext_questions(cfg)
n_respondents = df["respondent_id"].nunique()


# ── Run analysis ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Running analysis…")
def run_analysis(likert_json: str, freetext_json: str, cfg_str: str):
    ldf = pd.read_json(io.StringIO(likert_json))
    fdf = pd.read_json(io.StringIO(freetext_json))
    cfg = json.loads(cfg_str)
    freetext_qs = get_freetext_questions(cfg)
    q_labels = get_question_labels(cfg)

    ls = likert_summary(ldf, question_labels=q_labels) if not ldf.empty else pd.DataFrame()
    sent = analyze_sentiment(fdf) if not fdf.empty else pd.DataFrame()
    sent_sum = sentiment_summary(sent) if not sent.empty else pd.DataFrame()
    themes_per_q = {
        q["number"]: extract_themes(fdf, q_number=q["number"], top_n=15)
        for q in freetext_qs
    }
    themes_all = extract_themes(fdf, top_n=15) if not fdf.empty else pd.DataFrame()
    return ls, sent, sent_sum, themes_per_q, themes_all


ls, sent, sent_sum, themes_per_q, themes_all = run_analysis(
    likert_df.to_json(), freetext_df.to_json(), cfg_str
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Overview
# ─────────────────────────────────────────────────────────────────────────────
survey_title = cfg.get("survey_title") or "Survey Results"
st.header(survey_title)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Respondents", n_respondents)
c2.metric("Total responses", len(df))
if not ls.empty:
    c3.metric("Overall mean", f"{ls['mean'].mean():.2f} / 5.00")
    c4.metric("Avg % positive", f"{ls['pct_positive'].mean():.1f}%")

if not ls.empty:
    fig_heat = px.imshow(
        ls[["mean"]].T,
        x=ls["label"], y=["Mean score"],
        color_continuous_scale=["#ef4444", "#f97316", "#00f5d4"],
        zmin=1, zmax=5, text_auto=".2f",
        title="Mean score by dimension", aspect="auto",
    )
    fig_heat.update_layout(
        coloraxis_colorbar=dict(title="Score"),
        height=220,
    )
    fig_heat.update_layout(**CHART_LAYOUT)
    fig_heat.update_xaxes(tickangle=-35, tickfont=dict(size=11))
    st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Likert distributions
# ─────────────────────────────────────────────────────────────────────────────
if not ls.empty:
    st.header("Likert distributions")
    tab_bar, tab_diverge, tab_table = st.tabs(
        ["Bar chart", "Diverging", "Summary table"]
    )

    with tab_bar:
        selected_q = st.selectbox(
            "Question",
            options=ls["q_number"].tolist(),
            format_func=lambda n: f"Q{n}: {question_labels.get(n, '')}",
        )
        q_row = ls[ls["q_number"] == selected_q].iloc[0]
        dist_data = pd.DataFrame({
            "Score": [1, 2, 3, 4, 5],
            "Count": [q_row[f"dist_{i}"] for i in range(1, 6)],
        })
        fig_bar = px.bar(
            dist_data, x="Score", y="Count",
            color="Score", color_discrete_map=SCORE_COLORS,
            title=f"Q{selected_q}: {question_labels.get(selected_q, '')}",
            text="Count",
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(showlegend=False)
        fig_bar.update_layout(**CHART_LAYOUT)
        bc1, bc2, bc3 = st.columns(3)
        bc1.metric("Mean", f"{q_row['mean']:.2f}")
        bc2.metric("% Positive (4–5)", f"{q_row['pct_positive']}%")
        bc3.metric("Rating", q_row["score_label"])
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab_diverge:
        labels = ls["label"].tolist()
        fig_div = go.Figure()
        for vals, name, color in [
            (-ls["dist_1"].values, "Strongly disagree (1)", SCORE_COLORS[1]),
            (-ls["dist_2"].values, "Disagree (2)",          SCORE_COLORS[2]),
            (ls["dist_3"].values,  "Neutral (3)",           SCORE_COLORS[3]),
            (ls["dist_4"].values,  "Agree (4)",             SCORE_COLORS[4]),
            (ls["dist_5"].values,  "Strongly agree (5)",    SCORE_COLORS[5]),
        ]:
            fig_div.add_bar(
                y=labels, x=vals, name=name,
                orientation="h", marker_color=color,
            )
        fig_div.update_layout(
            barmode="relative",
            title="Agreement distribution (all questions)",
            xaxis_title="← Disagree | Agree →",
            height=400,
            legend=dict(orientation="h", y=-0.2),
        )
        fig_div.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_div, use_container_width=True)

    with tab_table:
        st.dataframe(
            ls[["label", "count", "mean", "median", "std",
                "pct_positive", "pct_negative", "score_label"]].rename(columns={
                "label": "Dimension", "count": "N", "mean": "Mean",
                "median": "Median", "std": "SD",
                "pct_positive": "% Positive", "pct_negative": "% Negative",
                "score_label": "Rating",
            }),
            use_container_width=True, hide_index=True,
        )
        st.download_button(
            "Download Likert summary CSV",
            data=ls.to_csv(index=False),
            file_name="likert_summary.csv", mime="text/csv",
        )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Sentiment
# ─────────────────────────────────────────────────────────────────────────────
st.header("Sentiment analysis")

if sent.empty:
    st.info("No free-text responses found.")
else:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        n_pos = (sent["sentiment"] == "POSITIVE").sum()
        fig_pie = px.pie(
            values=[n_pos, len(sent) - n_pos],
            names=["Positive", "Negative"],
            color_discrete_sequence=[
                SENTIMENT_COLORS["POSITIVE"],
                SENTIMENT_COLORS["NEGATIVE"],
            ],
            title="Overall sentiment",
        )
        fig_pie.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        if not sent_sum.empty:
            fig_sb = px.bar(
                sent_sum, x="q_number",
                y=["pct_positive", "pct_negative"],
                barmode="group",
                title="Sentiment by question",
                labels={
                    "q_number": "Question", "value": "%",
                    "variable": "Sentiment",
                },
                color_discrete_map={
                    "pct_positive": SENTIMENT_COLORS["POSITIVE"],
                    "pct_negative": SENTIMENT_COLORS["NEGATIVE"],
                },
            )
            fig_sb.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig_sb, use_container_width=True)

    filt = st.selectbox("Filter", ["All", "POSITIVE", "NEGATIVE"])
    view = sent if filt == "All" else sent[sent["sentiment"] == filt]
    st.dataframe(
        view[["respondent_id", "q_number", "free_text",
              "sentiment", "confidence"]],
        use_container_width=True, hide_index=True,
    )
    st.download_button(
        "Download sentiment CSV",
        data=sent.to_csv(index=False),
        file_name="sentiment_out.csv", mime="text/csv",
    )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Themes
# ─────────────────────────────────────────────────────────────────────────────
st.header("Theme extraction")

if not freetext_qs:
    st.info("No free-text questions detected.")
else:
    tab_labels = (
        [f"Q{q['number']} — {q['label']}" for q in freetext_qs] + ["All free-text"]
    )
    theme_tabs = st.tabs(tab_labels)

    for i, q in enumerate(freetext_qs):
        with theme_tabs[i]:
            tdf = themes_per_q.get(q["number"], pd.DataFrame())
            if tdf.empty:
                st.info("Not enough responses yet for theme extraction (need 10+).")
            else:
                fig_t = px.bar(
                    tdf.sort_values("tfidf_score"),
                    x="tfidf_score", y="term", orientation="h",
                    title=f"Top themes: Q{q['number']} — {q['label']}",
                    labels={"tfidf_score": "TF-IDF score", "term": "Theme"},
                    color="tfidf_score",
                    color_continuous_scale=["#06b6d4", "#00f5d4"],
                )
                fig_t.update_layout(
                    showlegend=False, coloraxis_showscale=False, height=420
                )
                fig_t.update_layout(**CHART_LAYOUT)
                st.plotly_chart(fig_t, use_container_width=True)

    with theme_tabs[-1]:
        if themes_all.empty:
            st.info("Not enough responses yet for theme extraction (need 10+).")
        else:
            fig_all = px.bar(
                themes_all.sort_values("tfidf_score"),
                x="tfidf_score", y="term", orientation="h",
                title="Top themes: all free-text",
                labels={"tfidf_score": "TF-IDF score", "term": "Theme"},
                color="tfidf_score",
                color_continuous_scale=["#06b6d4", "#00f5d4"],
            )
            fig_all.update_layout(
                showlegend=False, coloraxis_showscale=False, height=420
            )
            fig_all.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig_all, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Raw data
# ─────────────────────────────────────────────────────────────────────────────
st.header("Raw responses")
with st.expander("Show raw data"):
    q_filter = st.multiselect(
        "Filter by question number",
        options=sorted(df["q_number"].unique().tolist()),
    )
    view = df[df["q_number"].isin(q_filter)] if q_filter else df
    st.dataframe(view, use_container_width=True, hide_index=True)