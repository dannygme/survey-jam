"""
pages/1_Build.py
----------------
Survey builder. Creator designs questions, saves a session file,
and generates a shareable respondent link.
"""

import base64
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.styles import apply_global_styles
from scripts.config import make_empty_config, full_question_text

st.set_page_config(page_title="Build — Survey Jam", layout="wide")
apply_global_styles()

# ── Session state bootstrap ───────────────────────────────────────────────────
if "cfg" not in st.session_state:
    st.session_state.cfg = make_empty_config()

cfg = st.session_state.cfg


# ── Helpers ───────────────────────────────────────────────────────────────────
def _ensure_ids():
    """Backfill IDs for any questions loaded from older session files."""
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


def _config_to_url_param(cfg: dict) -> str:
    raw = json.dumps(cfg, separators=(",", ":"), ensure_ascii=False)
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _get_app_base_url() -> str:
    try:
        ctx = st.context
        headers = ctx.headers if hasattr(ctx, "headers") else {}
        host = headers.get("host", "localhost:8501")
        proto = "https" if "streamlit.app" in host else "http"
        return f"{proto}://{host}"
    except Exception:
        return "http://localhost:8501"


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

    st.subheader("Share with respondents")
    if not cfg["questions"]:
        st.info("Add at least one question to generate a link.")
    else:
        cfg_param = _config_to_url_param(cfg)
        base = _get_app_base_url()
        share_url = f"{base}/Respond?survey={cfg_param}"
        st.text_area(
            "Copy this link and send it to respondents",
            value=share_url,
            height=100,
        )
        st.caption(
            "Anyone with this link can fill out your survey. "
            "Their responses will be sent back to you as a file."
        )

    st.subheader("Save your session")
    cfg_copy = dict(cfg)
    cfg_copy["created_at"] = datetime.now(tz=timezone.utc).isoformat()
    st.download_button(
        "Download session file",
        data=json.dumps(cfg_copy, indent=2, ensure_ascii=False),
        file_name="survey_session.json",
        mime="application/json",
        use_container_width=True,
    )
    st.caption("* = required question")