"""
pages/1_Build.py
----------------
Survey builder. Creator designs questions and downloads the survey
as JSON (for reimporting) or CSV (to send to respondents to fill in).
"""

import csv
import io
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.styles import apply_global_styles
from scripts.config import make_empty_config

st.set_page_config(page_title="Build — Survey Jam", layout="wide")
apply_global_styles()

# ── Session state bootstrap ───────────────────────────────────────────────────
if "cfg" not in st.session_state:
    st.session_state.cfg = make_empty_config()

cfg = st.session_state.cfg


# ── Helpers ───────────────────────────────────────────────────────────────────
def _ensure_ids():
    for q in cfg["questions"]:
        if "id" not in q:
            q["id"] = str(uuid.uuid4())


def _renumber():
    for i, q in enumerate(cfg["questions"], start=1):
        q["number"] = i


def _move(idx, direction):
    qs = cfg["questions"]
    target = idx + direction
    if 0 <= target < len(qs):
        qs[idx], qs[target] = qs[target], qs[idx]
        _renumber()


def _build_respondent_csv(cfg: dict) -> str:
    """
    Build a clean CSV for respondents to fill in.
    Likert questions get a column with scale options noted.
    Free-text questions get a blank column.
    One blank row is included for each respondent to fill in.
    """
    output = io.StringIO()
    scale = cfg["likert_scale"]["labels"]
    scale_note = "/".join(f"{k}={v}" for k, v in sorted(scale.items()))

    headers = ["respondent_id", "timestamp"]
    for q in cfg["questions"]:
        if q["type"] == "likert":
            headers.append(f"Q{q['number']}. {q['text']} [{scale_note}]")
        else:
            headers.append(f"Q{q['number']}. {q['text']} [open answer]")

    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerow(["your_name_or_id", datetime.now(tz=timezone.utc).isoformat()] + [""] * len(cfg["questions"]))
    return output.getvalue()


_ensure_ids()

# ── Load session file ─────────────────────────────────────────────────────────
st.title("Build")

with st.expander("Resume from a saved session"):
    uploaded = st.file_uploader(
        "Upload your session file (.json)", type="json", key="session_upload"
    )
    if uploaded:
        try:
            loaded = json.load(uploaded)
            st.session_state.cfg = loaded
            cfg = st.session_state.cfg
            _ensure_ids()
            st.success("Session loaded.")
            st.rerun()
        except Exception as e:
            st.error(f"Could not read session file: {e}")

st.divider()

col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.subheader("Survey details")
    cfg["survey_title"] = st.text_input(
        "Survey title", value=cfg.get("survey_title", "")
    )
    cfg["survey_description"] = st.text_area(
        "Description shown to respondents",
        value=cfg.get("survey_description", ""),
        height=80,
    )

    st.divider()
    st.subheader("Likert scale labels")
    scale = cfg["likert_scale"]
    cols = st.columns(5)
    defaults = ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"]
    for col, key, default in zip(cols, ["1", "2", "3", "4", "5"], defaults):
        scale["labels"][key] = col.text_input(
            key, value=scale["labels"].get(key, default)
        )

    st.divider()
    st.subheader("Questions")

    qs = cfg["questions"]
    for idx, q in enumerate(qs):
        qid = q["id"]
        with st.container(border=True):
            hdr, ctrl = st.columns([8, 2])
            with hdr:
                st.markdown(f"**Q{q['number']}** — `{q['type']}`")
            with ctrl:
                c1, c2, c3 = st.columns(3)
                if c1.button("↑", key=f"up_{idx}", disabled=idx == 0):
                    _move(idx, -1)
                    st.rerun()
                if c2.button("↓", key=f"dn_{idx}", disabled=idx == len(qs) - 1):
                    _move(idx, 1)
                    st.rerun()
                if c3.button("✕", key=f"del_{idx}"):
                    qs.pop(idx)
                    _renumber()
                    st.rerun()

            q["text"] = st.text_area(
                "Question text", value=q["text"],
                key=f"text_{qid}", height=72, label_visibility="collapsed",
            )
            la, ty, re = st.columns([3, 2, 1])
            q["label"] = la.text_input(
                "Short label", value=q["label"], key=f"label_{qid}"
            )
            q["type"] = ty.selectbox(
                "Type", options=["likert", "freetext"],
                index=0 if q["type"] == "likert" else 1,
                key=f"type_{qid}",
            )
            q["required"] = re.checkbox(
                "Required", value=q.get("required", True), key=f"req_{qid}"
            )

    st.divider()
    a1, a2 = st.columns(2)
    if a1.button("+ Likert question", use_container_width=True):
        qs.append({
            "id": str(uuid.uuid4()),
            "number": len(qs) + 1,
            "text": "New question…",
            "type": "likert",
            "label": f"Q{len(qs)+1}",
            "required": True,
        })
        st.rerun()
    if a2.button("+ Free-text question", use_container_width=True):
        qs.append({
            "id": str(uuid.uuid4()),
            "number": len(qs) + 1,
            "text": "New open-ended question…",
            "type": "freetext",
            "label": f"Open Q{len(qs)+1}",
            "required": False,
        })
        st.rerun()

# ── Right panel ───────────────────────────────────────────────────────────────
with col_right:
    st.subheader("Preview")
    with st.container(border=True):
        st.markdown(f"### {cfg['survey_title'] or 'Untitled survey'}")
        if cfg.get("survey_description"):
            st.caption(cfg["survey_description"])
        st.divider()

        scale_labels = cfg["likert_scale"]["labels"]
        options = [v for k, v in sorted(scale_labels.items())]

        for q in cfg["questions"]:
            suffix = " *" if q.get("required") else " (optional)"
            st.markdown(f"**{q['number']}.** {q['text']}{suffix}")

            if q["type"] == "likert":
                n = len(options)
                col_ratios = [1.5] + [1] * (n - 2) + [1.5] if n >= 2 else [1] * n
                likert_cols = st.columns(col_ratios)
                for lcol, label in zip(likert_cols, options):
                    lcol.markdown(
                        f"<div style='text-align:center; font-size:13px; "
                        f"line-height:1.2; padding:4px 2px; "
                        f"word-break:break-word; white-space:normal; "
                        f"overflow:visible; color:#94a3b8;'>"
                        f"○<br>{label}</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.text_area(
                    "", key=f"prev_ft_{q['id']}", height=68,
                    label_visibility="collapsed",
                    placeholder="Type your answer here…",
                )
            st.divider()

    # ── Downloads ─────────────────────────────────────────────────────────────
    st.subheader("Download survey")
    if not cfg["questions"]:
        st.info("Add at least one question to download.")
    else:
        cfg_copy = dict(cfg)
        cfg_copy["created_at"] = datetime.now(tz=timezone.utc).isoformat()

        d1, d2 = st.columns(2)
        d1.download_button(
            "Download CSV",
            data=_build_respondent_csv(cfg_copy),
            file_name=f"{cfg_copy.get('survey_title', 'survey').replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
            help="Send this to respondents to fill in.",
        )
        d2.download_button(
            "Download JSON",
            data=json.dumps(cfg_copy, indent=2, ensure_ascii=False),
            file_name=f"{cfg_copy.get('survey_title', 'survey').replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
            help="Use this to reimport or share the survey structure.",
        )
        st.caption(
            "Send the CSV to respondents to fill in and return. "
            "Use the JSON to reload this survey later."
        )

    st.divider()
    st.subheader("Save session")
    cfg_copy2 = dict(cfg)
    cfg_copy2["created_at"] = datetime.now(tz=timezone.utc).isoformat()
    st.download_button(
        "Download session file",
        data=json.dumps(cfg_copy2, indent=2, ensure_ascii=False),
        file_name="survey_session.json",
        mime="application/json",
        use_container_width=True,
        help="Save this to resume editing later.",
    )