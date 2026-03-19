"""
analysis.py
-----------
Quantitative Likert aggregation and qualitative NLP (sentiment + themes).

Usage:
    python scripts/analysis.py
    # or import individual functions from other scripts
"""

import re
import sys
import warnings
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

warnings.filterwarnings("ignore", message=".*tokenizers.*")

sys.path.insert(0, str(Path(__file__).parent))


# ── Sentiment model — loaded once, reused forever ─────────────────────────────
# Defined at module level so caching works correctly

def _load_model():
    """Load DistilBERT sentiment model. Called once per session."""
    try:
        from transformers import pipeline as hf_pipeline
        return hf_pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            truncation=True,
            max_length=512,
        )
    except ImportError:
        sys.exit(
            "[analysis] transformers/torch not installed. "
            "Run: pip install transformers torch"
        )


# Module-level cache — plain Python, no Streamlit dependency
_MODEL_CACHE = {}


def _get_sentiment_pipeline():
    if "model" not in _MODEL_CACHE:
        _MODEL_CACHE["model"] = _load_model()
    return _MODEL_CACHE["model"]


# ── Score labels ──────────────────────────────────────────────────────────────

SCORE_LABELS = {
    (4.5, 5.0): "Strong",
    (3.5, 4.5): "Positive",
    (2.5, 3.5): "Mixed",
    (1.5, 2.5): "Concerning",
    (1.0, 1.5): "Critical",
}


def score_label(mean: float) -> str:
    for (lo, hi), label in SCORE_LABELS.items():
        if lo <= mean <= hi:
            return label
    return "N/A"


# ── 1. Likert aggregation ─────────────────────────────────────────────────────

def likert_summary(
    likert_df: pd.DataFrame,
    config_path: str = None,
    question_labels: dict = None,
) -> pd.DataFrame:
    if question_labels is None:
        if config_path:
            from config import load_config, get_question_labels
            cfg = load_config(config_path)
            question_labels = get_question_labels(cfg)
        else:
            question_labels = {}

    records = []
    for q_num, grp in likert_df.groupby("q_number"):
        scores = grp["likert"]
        dist = scores.value_counts().sort_index().to_dict()
        n = len(scores)
        records.append({
            "q_number": q_num,
            "label": question_labels.get(q_num, f"Q{q_num}"),
            "count": n,
            "mean": round(scores.mean(), 2),
            "median": scores.median(),
            "std": round(scores.std(), 2),
            "pct_positive": round(scores.isin([4, 5]).sum() / n * 100, 1) if n else 0,
            "pct_negative": round(scores.isin([1, 2]).sum() / n * 100, 1) if n else 0,
            "dist_1": dist.get(1, 0),
            "dist_2": dist.get(2, 0),
            "dist_3": dist.get(3, 0),
            "dist_4": dist.get(4, 0),
            "dist_5": dist.get(5, 0),
        })
    summary = pd.DataFrame(records).sort_values("q_number").reset_index(drop=True)
    summary["score_label"] = summary["mean"].apply(score_label)
    return summary


# ── 2. Sentiment analysis ─────────────────────────────────────────────────────

def analyze_sentiment(
    freetext_df: pd.DataFrame,
    batch_size: int = 32,
) -> pd.DataFrame:
    texts = freetext_df["free_text"].tolist()
    if not texts:
        return pd.DataFrame(
            columns=["respondent_id", "q_number", "free_text",
                     "sentiment", "confidence"]
        )
    pipe = _get_sentiment_pipeline()
    results = []
    for i in range(0, len(texts), batch_size):
        results.extend(pipe(texts[i: i + batch_size]))

    out = freetext_df[["respondent_id", "q_number", "free_text"]].copy()
    out = out.reset_index(drop=True)
    out["sentiment"] = [r["label"] for r in results]
    out["confidence"] = [round(r["score"], 4) for r in results]
    return out


def sentiment_summary(sentiment_df: pd.DataFrame) -> pd.DataFrame:
    if sentiment_df.empty:
        return pd.DataFrame()
    grp = sentiment_df.groupby("q_number")
    n = grp["sentiment"].count()
    pos = grp["sentiment"].apply(lambda s: (s == "POSITIVE").sum())
    return pd.DataFrame({
        "count": n,
        "pct_positive": (pos / n * 100).round(1),
        "pct_negative": ((n - pos) / n * 100).round(1),
    }).reset_index()


# ── 3. Theme extraction ───────────────────────────────────────────────────────

_CUSTOM_STOP_WORDS = {
    "work", "also", "make", "feel", "think", "would", "could", "really",
    "like", "just", "get", "us", "one", "company", "team", "people",
}


def extract_themes(
    freetext_df: pd.DataFrame,
    q_number=None,
    top_n: int = 15,
) -> pd.DataFrame:
    subset = (
        freetext_df[freetext_df["q_number"] == q_number]
        if q_number is not None
        else freetext_df
    )
    texts = subset["free_text"].dropna().tolist()
    texts = [t for t in texts if len(t.strip()) > 10]

    if len(texts) < 2:
        return pd.DataFrame(columns=["term", "tfidf_score"])

    def _clean(t):
        t = t.lower()
        t = re.sub(r"[^\w\s]", " ", t)
        return re.sub(r"\s+", " ", t).strip()

    cleaned = [_clean(t) for t in texts]

    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    stop = ENGLISH_STOP_WORDS.union(_CUSTOM_STOP_WORDS)

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words=list(stop),
        max_features=500,
        min_df=2,
        sublinear_tf=True,
    )
    try:
        matrix = vectorizer.fit_transform(cleaned)
    except ValueError:
        return pd.DataFrame(columns=["term", "tfidf_score"])

    scores = matrix.sum(axis=0).A1
    terms = vectorizer.get_feature_names_out()
    top_idx = scores.argsort()[::-1][:top_n]
    return pd.DataFrame({
        "term": terms[top_idx],
        "tfidf_score": scores[top_idx].round(3),
    })


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from preprocess import load_and_clean, split_frames

    csv_arg = sys.argv[1] if len(sys.argv) > 1 else "data/survey_responses.csv"
    df = load_and_clean(csv_arg)
    likert_df, freetext_df = split_frames(df)

    print("\n── Likert summary ──")
    ls = likert_summary(likert_df)
    print(ls[["label", "mean", "pct_positive", "score_label"]].to_string(index=False))

    print("\n── Sentiment (first 5) ──")
    sent = analyze_sentiment(freetext_df)
    print(sent.head())

    print("\n── Top themes ──")
    themes = extract_themes(freetext_df, top_n=10)
    print(themes.to_string(index=False))