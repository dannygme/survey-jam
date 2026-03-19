"""
builder.py
----------
Streamlit app: design your survey, preview it, export survey_config.json.

Run with:
    streamlit run scripts/builder.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import save_config, make_empty_config, full_question_text

st.set_page_config(page_title="Survey Builder", page_icon=None, layout="wide")

# ── Session state bootstrap ───────────────────────────────────────────────────
if "cfg" not in st.session_state:
    st.session_state.cfg = make_empty_config()

cfg = st.session_state.cfg

# ── Helpers ───────────────────────────────────────────────────────────────────

def _renumber():
    """Keep question numbers contiguous after add/delete/reorder."""
    for i, q in enumerate(cfg["questions"], start=1):
        q["number"] = i


def _move(idx: int, direction: int):
    qs = cfg["questions"]
    target = idx + direction
    if 0 <= target < len(qs):
        qs[idx], qs[target] = qs[target], qs[idx]
        _renumber()


# ── Header ────────────────────────────────────────────────────────────────────
st.title("Survey builder")
st.caption("Design your survey. Export the config to use it with the analysis pipeline.")

col_left, col_right = st.columns([3, 2], gap="large")

# ── Left: survey metadata + question editor ───────────────────────────────────
with col_left:
    st.subheader("Survey details")
    cfg["survey_title"] = st.text_input(
        "Survey title", value=cfg.get("survey_title", "New Survey")
    )
    cfg["survey_description"] = st.text_area(
        "Description shown to respondents",
        value=cfg.get("survey_description", ""),
        height=80,
    )

    st.divider()
    st.subheader("Likert scale labels")
    scale = cfg["likert_scale"]
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    for col, key, default in zip(
        [sc1, sc2, sc3, sc4, sc5],
        ["1", "2", "3", "4", "5"],
        ["Strongly disagree", "Disagree", "Neutral", "Agree", "Strongly agree"],
    ):
        scale["labels"][key] = col.text_input(
            key, value=scale["labels"].get(key, default), label_visibility="visible"
        )

    st.divider()
    st.subheader("Questions")

    qs = cfg["questions"]

    for idx, q in enumerate(qs):
        with st.container(border=True):
            hdr, ctrl = st.columns([8, 2])
            with hdr:
                st.markdown(f"**Q{q['number']}** — `{q['type']}`")
            with ctrl:
                c1, c2, c3 = st.columns(3)
                if c1.button("↑", key=f"up_{idx}", help="Move up", disabled=idx == 0):
                    _move(idx, -1)
                    st.rerun()
                if c2.button("↓", key=f"dn_{idx}", help="Move down", disabled=idx == len(qs) - 1):
                    _move(idx, 1)
                    st.rerun()
                if c3.button("✕", key=f"del_{idx}", help="Delete"):
                    qs.pop(idx)
                    _renumber()
                    st.rerun()

            q["text"] = st.text_area(
                "Question text",
                value=q["text"],
                key=f"text_{idx}",
                height=72,
                label_visibility="collapsed",
            )
            la, ty, re = st.columns([3, 2, 1])
            q["label"] = la.text_input(
                "Short label (for charts)",
                value=q["label"],
                key=f"label_{idx}",
            )
            q["type"] = ty.selectbox(
                "Type",
                options=["likert", "freetext"],
                index=0 if q["type"] == "likert" else 1,
                key=f"type_{idx}",
            )
            q["required"] = re.checkbox(
                "Required", value=q.get("required", True), key=f"req_{idx}"
            )

    st.divider()
    add_col1, add_col2 = st.columns(2)
    if add_col1.button("+ Add Likert question", use_container_width=True):
        qs.append(
            {
                "number": len(qs) + 1,
                "text": "New question…",
                "type": "likert",
                "label": f"Q{len(qs)+1}",
                "required": True,
            }
        )
        st.rerun()
    if add_col2.button("+ Add free-text question", use_container_width=True):
        qs.append(
            {
                "number": len(qs) + 1,
                "text": "New open-ended question…",
                "type": "freetext",
                "label": f"Open Q{len(qs)+1}",
                "required": False,
            }
        )
        st.rerun()

# ── Right: preview + export ───────────────────────────────────────────────────
with col_right:
    st.subheader("Preview")
    with st.container(border=True):
        st.markdown(f"### {cfg['survey_title']}")
        if cfg.get("survey_description"):
            st.caption(cfg["survey_description"])
        st.divider()
        scale_labels = cfg["likert_scale"]["labels"]
        options = [f"{k} – {v}" for k, v in sorted(scale_labels.items())]
        for q in cfg["questions"]:
            st.markdown(
                f"**{q['number']}.** {q['text']}"
                + (" *" if q.get("required") else "")
            )
            if q["type"] == "likert":
                st.radio(
                    label="",
                    options=options,
                    key=f"prev_{q['number']}",
                    label_visibility="collapsed",
                    horizontal=True,
                )
            else:
                st.text_area(
                    label="",
                    key=f"prev_ft_{q['number']}",
                    height=80,
                    label_visibility="collapsed",
                    placeholder="Type your answer here…",
                )
            st.divider()

    st.subheader("Export")
    out_path = st.text_input("Save path", value="data/survey_config.json")

    if st.button("Save config to disk", type="primary", use_container_width=True):
        cfg["created_at"] = datetime.now(tz=timezone.utc).isoformat()
        try:
            save_config(cfg, out_path)
            st.success(f"Saved to `{out_path}`")
        except SystemExit as e:
            st.error(str(e))

    # Also offer raw JSON download (no disk write needed)
    cfg_copy = dict(cfg)
    cfg_copy["created_at"] = datetime.now(tz=timezone.utc).isoformat()
    st.download_button(
        "Download config JSON",
        data=json.dumps(cfg_copy, indent=2, ensure_ascii=False),
        file_name="survey_config.json",
        mime="application/json",
        use_container_width=True,
    )

    st.caption("* = required question")