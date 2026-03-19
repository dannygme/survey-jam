"""
responder.py
------------
Streamlit app: renders the survey defined in survey_config.json and
appends each submission to survey_responses.csv in long format.

Share this app with respondents (locally or via Streamlit Community Cloud).

Run with:
    streamlit run scripts/responder.py
    streamlit run scripts/responder.py -- --config data/survey_config.json
"""

import csv
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    load_config,
    get_likert_questions,
    get_freetext_questions,
    full_question_text,
)

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG_PATH  = "data/survey_config.json"
RESPONSE_CSV = "data/survey_responses.csv"
CSV_HEADERS  = ["respondent_id", "timestamp", "question", "response"]

cfg = load_config(CONFIG_PATH)
scale = cfg["likert_scale"]
likert_options = [
    scale["labels"][str(k)]
    for k in range(scale["min"], scale["max"] + 1)
]
# Map label → numeric string for storage ("Agree" → "4")
label_to_score = {v: str(k) for k, v in scale["labels"].items()}

st.set_page_config(
    page_title=cfg["survey_title"],
    page_icon=None,
    layout="centered",
)


# ── CSV append helper ─────────────────────────────────────────────────────────

def append_responses(rows: list[dict]) -> None:
    path = Path(RESPONSE_CSV)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


# ── Session state ─────────────────────────────────────────────────────────────
if "submitted" not in st.session_state:
    st.session_state.submitted = False


# ── Thank-you screen ──────────────────────────────────────────────────────────
if st.session_state.submitted:
    st.title("Thank you!")
    st.success("Your response has been recorded anonymously.")
    if st.button("Submit another response"):
        st.session_state.submitted = False
        st.rerun()
    st.stop()


# ── Survey form ───────────────────────────────────────────────────────────────
st.title(cfg["survey_title"])
if cfg.get("survey_description"):
    st.info(cfg["survey_description"])
st.divider()

answers: dict[int, str] = {}
validation_errors: list[str] = []

with st.form("survey_form", border=False):
    for q in cfg["questions"]:
        label_suffix = " *" if q.get("required") else " (optional)"
        st.markdown(f"**{q['number']}.** {q['text']}{label_suffix}")

        if q["type"] == "likert":
            chosen = st.radio(
                label="",
                options=["— select —"] + likert_options,
                key=f"q_{q['number']}",
                label_visibility="collapsed",
                horizontal=True,
            )
            answers[q["number"]] = chosen

        else:  # freetext
            text = st.text_area(
                label="",
                key=f"q_{q['number']}",
                height=100,
                label_visibility="collapsed",
                placeholder="Type your answer here…",
            )
            answers[q["number"]] = text.strip()

        st.divider()

    submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)

if submitted:
    # ── Validate ──────────────────────────────────────────────────────────────
    for q in cfg["questions"]:
        if not q.get("required"):
            continue
        val = answers.get(q["number"], "")
        if q["type"] == "likert" and val == "— select —":
            validation_errors.append(f"Q{q['number']} requires a selection.")
        elif q["type"] == "freetext" and not val:
            validation_errors.append(f"Q{q['number']} requires a written answer.")

    if validation_errors:
        for err in validation_errors:
            st.warning(err)
    else:
        # ── Build rows ────────────────────────────────────────────────────────
        respondent_id = f"resp_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        rows = []
        for q in cfg["questions"]:
            val = answers[q["number"]]
            if q["type"] == "likert":
                if val == "— select —":
                    continue  # optional unanswered
                stored = label_to_score.get(val, val)
            else:
                if not val:
                    continue  # optional empty freetext
                stored = val
            rows.append(
                {
                    "respondent_id": respondent_id,
                    "timestamp": timestamp,
                    "question": full_question_text(q),
                    "response": stored,
                }
            )
        append_responses(rows)
        st.session_state.submitted = True
        st.rerun()