"""
preprocess.py
-------------
Loads and cleans the survey CSV. Separates Likert-scale responses from
free-text responses and validates data integrity.

Usage:
    python scripts/preprocess.py
    # or import load_and_clean() directly from other scripts
"""

import pandas as pd
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import load_config, get_likert_questions, get_freetext_questions, full_question_text

LIKERT_RANGE = range(1, 6)


def load_and_clean(
    csv_path: str = "data/survey_responses.csv",
    config_path: str = "data/survey_config.json",
) -> pd.DataFrame:
    """
    Load survey CSV, validate schema, parse types, and add helper columns.

    Returns a DataFrame with columns:
        respondent_id, timestamp, question, response,
        likert (int | NaN), free_text (str | NaN),
        q_number (int), is_optional (bool)
    """
    cfg = load_config(config_path)
    likert_q_numbers = {q["number"] for q in get_likert_questions(cfg)}
    freetext_qs = get_freetext_questions(cfg)
    optional_nums = {q["number"] for q in freetext_qs if not q.get("required", True)}

    path = Path(csv_path)
    if not path.exists():
        sys.exit(f"[preprocess] CSV not found at: {csv_path}")

    df = pd.read_csv(path, dtype=str)

    required_cols = {"respondent_id", "timestamp", "question", "response"}
    missing = required_cols - set(df.columns)
    if missing:
        sys.exit(f"[preprocess] Missing columns: {missing}")

    df = df.apply(lambda col: col.str.strip() if col.dtype == object else col)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    def _parse_likert(val):
        try:
            v = str(val).strip()
            if v.isdigit() and int(v) in LIKERT_RANGE:
                return int(v)
        except (ValueError, AttributeError):
            pass
        return float("nan")

    df["likert"] = df["response"].apply(_parse_likert)
    df["free_text"] = df.apply(
        lambda row: row["response"] if pd.isna(row["likert"]) else float("nan"),
        axis=1,
    )

    def _q_number(q: str) -> int:
        try:
            return int(str(q).split(".")[0].strip())
        except (ValueError, AttributeError):
            return -1

    df["q_number"] = df["question"].apply(_q_number)
    df["is_optional"] = df["q_number"].isin(optional_nums)

    missing_ids = df["respondent_id"].isna() | (df["respondent_id"] == "")
    if missing_ids.any():
        df.loc[missing_ids, "respondent_id"] = [
            f"resp_{uuid.uuid4().hex[:8]}" for _ in range(missing_ids.sum())
        ]

    return df


def split_frames(
    df: pd.DataFrame,
    config_path: str = "data/survey_config.json",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (likert_df, freetext_df) split by question type.
    """
    cfg = load_config(config_path)
    likert_nums = {q["number"] for q in get_likert_questions(cfg)}
    freetext_nums = {q["number"] for q in get_freetext_questions(cfg)}

    likert_df = df[df["q_number"].isin(likert_nums)].dropna(subset=["likert"]).copy()
    freetext_df = (
        df[df["q_number"].isin(freetext_nums)]
        .dropna(subset=["free_text"])
        .query("free_text != ''")
        .copy()
    )
    return likert_df, freetext_df


if __name__ == "__main__":
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else "data/survey_responses.csv"
    data = load_and_clean(csv_arg)
    likert, freetext = split_frames(data)
    print("\nLikert sample:")
    print(likert[["respondent_id", "q_number", "likert"]].head())
    print("\nFree-text sample:")
    print(freetext[["respondent_id", "q_number", "free_text"]].head())