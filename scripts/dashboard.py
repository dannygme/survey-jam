"""
dashboard.py
------------
Streamlit dashboard for the Employee Listening pipeline.

Run with:
    streamlit run scripts/dashboard.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import load_config, get_question_labels, get_freetext_questions
from preprocess import load_and_clean, split_frames
from analysis import (
    likert_summary,
    analyze_sentiment,
    sentiment_summary,
    extract_themes,
)

# ── Page config ───────────────────────────────────────────────────────────────
cfg = load_config("data/survey_config.json")
freetext_qs = get_freetext_questions(cfg)
question_labels = get_question_labels(cfg)

st.set_page_config(
    page_title=cfg["survey_title"],
    page_icon=None,
    layout="wide",
)

# ── Colour palette ────────────────────────────────────────────────────────────
SCORE_COLORS = {
    1: "#E24B4A",
    2: "#EF9F27",
    3: "#888780",
    4: "#1D9E75",
    5: "#0F6E56",
}

SENTIMENT_COLORS = {
    "POSITIVE": "#1D9E75",
    "NEGATIVE": "#E24B4A",
}


# ── Data loading (cached) ─────────────────────────────────────────────────────

@st.cache_data(show_spinner="Loading survey data…")
def load_data(csv_path: str):
    df = load_and_clean(csv_path)
    likert_df, freetext_df = split_frames(df)
    return df, likert_df, freetext_df


@st.cache_data(show_spinner="Running analysis…")
def run_analysis(_likert_df, _freetext_df):
    ls = likert_summary(_likert_df)
    sent = analyze_sentiment(_freetext_df)
    sent_sum = sentiment_summary(sent)
    themes_per_q = {
        q["number"]: extract_themes(_freetext_df, q_number=q["number"], top_n=15)
        for q in freetext_qs
    }
    themes_all = extract_themes(_freetext_df, top_n=15)
    return ls, sent, sent_sum, themes_per_q, themes_all


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Settings")
    csv_path = st.text_input(
        "CSV path",
        value="data/survey_responses.csv",
    )

# ── Load ──────────────────────────────────────────────────────────────────────
try:
    df, likert_df, freetext_df = load_data(csv_path)
except SystemExit as e:
    st.error(str(e))
    st.stop()

n_respondents = df["respondent_id"].nunique()
ls, sent, sent_sum, themes_per_q, themes_all = run_analysis(likert_df, freetext_df)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Overview
# ─────────────────────────────────────────────────────────────────────────────
st.title(cfg["survey_title"])
st.markdown("---")
st.header("Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Respondents", n_respondents)
col2.metric("Total responses", len(df))
col3.metric("Overall mean score", f"{ls['mean'].mean():.2f} / 5.00")
col4.metric("Avg % positive (4–5)", f"{ls['pct_positive'].mean():.1f}%")

fig_heat = px.imshow(
    ls[["mean"]].T,
    x=ls["label"],
    y=["Mean score"],
    color_continuous_scale=["#E24B4A", "#EF9F27", "#1D9E75"],
    zmin=1, zmax=5,
    text_auto=".2f",
    title="Mean score by dimension",
    aspect="auto",
)
fig_heat.update_layout(
    coloraxis_colorbar=dict(title="Score"),
    margin=dict(l=0, r=0, t=40, b=100),
    height=220,
)
fig_heat.update_xaxes(tickangle=-35, tickfont=dict(size=11))
st.plotly_chart(fig_heat, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Likert distributions
# ─────────────────────────────────────────────────────────────────────────────
st.header("Likert distributions")

tab_bar, tab_diverge, tab_table = st.tabs(
    ["Bar chart", "Diverging (agree vs disagree)", "Summary table"]
)

with tab_bar:
    selected_q = st.selectbox(
        "Question",
        options=ls["q_number"].tolist(),
        format_func=lambda n: f"Q{n}: {question_labels.get(n, '')}",
        key="bar_q",
    )
    q_row = ls[ls["q_number"] == selected_q].iloc[0]
    dist_data = pd.DataFrame({
        "Score": [1, 2, 3, 4, 5],
        "Count": [q_row["dist_1"], q_row["dist_2"], q_row["dist_3"],
                  q_row["dist_4"], q_row["dist_5"]],
    })
    fig_bar = px.bar(
        dist_data, x="Score", y="Count",
        color="Score",
        color_discrete_map=SCORE_COLORS,
        title=f"Q{selected_q}: {question_labels.get(selected_q, '')}",
        text="Count",
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(showlegend=False, margin=dict(t=50, b=0))
    c1, c2, c3 = st.columns(3)
    c1.metric("Mean", f"{q_row['mean']:.2f}")
    c2.metric("% Positive (4–5)", f"{q_row['pct_positive']}%")
    c3.metric("Rating", q_row["score_label"])
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
        fig_div.add_bar(y=labels, x=vals, name=name,
                        orientation="h", marker_color=color)
    fig_div.update_layout(
        barmode="relative",
        title="Agreement distribution (all questions)",
        xaxis_title="← Disagree | Agree →",
        height=400,
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=0, r=0, t=50, b=80),
    )
    st.plotly_chart(fig_div, use_container_width=True)

with tab_table:
    display_cols = ["label", "count", "mean", "median", "std",
                    "pct_positive", "pct_negative", "score_label"]
    st.dataframe(
        ls[display_cols].rename(columns={
            "label": "Dimension", "count": "N", "mean": "Mean",
            "median": "Median", "std": "SD", "pct_positive": "% Positive",
            "pct_negative": "% Negative", "score_label": "Rating",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download Likert summary CSV",
        data=ls.to_csv(index=False),
        file_name="likert_summary.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Sentiment analysis
# ─────────────────────────────────────────────────────────────────────────────
st.header("Sentiment analysis")

if sent.empty:
    st.info("No free-text responses found for sentiment analysis.")
else:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        n_pos = (sent["sentiment"] == "POSITIVE").sum()
        n_neg = len(sent) - n_pos
        fig_pie = px.pie(
            values=[n_pos, n_neg],
            names=["Positive", "Negative"],
            color_discrete_sequence=[SENTIMENT_COLORS["POSITIVE"],
                                     SENTIMENT_COLORS["NEGATIVE"]],
            title="Overall sentiment split",
        )
        fig_pie.update_layout(margin=dict(t=40, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        if not sent_sum.empty:
            fig_sent_bar = px.bar(
                sent_sum, x="q_number",
                y=["pct_positive", "pct_negative"],
                barmode="group",
                title="Sentiment by question",
                labels={"q_number": "Question", "value": "%",
                        "variable": "Sentiment"},
                color_discrete_map={
                    "pct_positive": SENTIMENT_COLORS["POSITIVE"],
                    "pct_negative": SENTIMENT_COLORS["NEGATIVE"],
                },
            )
            st.plotly_chart(fig_sent_bar, use_container_width=True)

    sent_filter = st.selectbox(
        "Filter by sentiment",
        options=["All", "POSITIVE", "NEGATIVE"],
    )
    sent_view = sent if sent_filter == "All" else sent[sent["sentiment"] == sent_filter]
    st.dataframe(
        sent_view[["respondent_id", "q_number", "free_text",
                   "sentiment", "confidence"]],
        use_container_width=True,
        hide_index=True,
    )
    st.download_button(
        "Download sentiment CSV",
        data=sent.to_csv(index=False),
        file_name="sentiment_out.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Theme extraction
# ─────────────────────────────────────────────────────────────────────────────
st.header("Theme extraction")

tab_labels = [f"Q{q['number']} — {q['label']}" for q in freetext_qs] + ["All free-text"]
theme_tabs = st.tabs(tab_labels)

for i, q in enumerate(freetext_qs):
    with theme_tabs[i]:
        themes_df = themes_per_q.get(q["number"], pd.DataFrame())
        if themes_df.empty:
            st.info("Not enough responses for theme extraction (min 2 required).")
        else:
            fig_theme = px.bar(
                themes_df.sort_values("tfidf_score"),
                x="tfidf_score", y="term", orientation="h",
                title=f"Top themes: Q{q['number']} — {q['label']}",
                labels={"tfidf_score": "TF-IDF score", "term": "Theme"},
                color="tfidf_score",
                color_continuous_scale=["#B5D4F4", "#185FA5"],
            )
            fig_theme.update_layout(
                showlegend=False, coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=40, b=0), height=420,
            )
            st.plotly_chart(fig_theme, use_container_width=True)

with theme_tabs[-1]:
    if themes_all.empty:
        st.info("Not enough responses for theme extraction (min 2 required).")
    else:
        fig_all = px.bar(
            themes_all.sort_values("tfidf_score"),
            x="tfidf_score", y="term", orientation="h",
            title="Top themes: all free-text",
            labels={"tfidf_score": "TF-IDF score", "term": "Theme"},
            color="tfidf_score",
            color_continuous_scale=["#B5D4F4", "#185FA5"],
        )
        fig_all.update_layout(
            showlegend=False, coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=40, b=0), height=420,
        )
        st.plotly_chart(fig_all, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: Raw responses
# ─────────────────────────────────────────────────────────────────────────────
st.header("Raw responses")

with st.expander("Show raw data"):
    q_filter = st.multiselect(
        "Filter by question number",
        options=sorted(df["q_number"].unique().tolist()),
    )
    view = df[df["q_number"].isin(q_filter)] if q_filter else df
    st.dataframe(view, use_container_width=True, hide_index=True)