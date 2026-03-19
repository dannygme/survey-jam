"""
Home.py
-------
Landing page. Run with: streamlit run Home.py
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from utils.styles import apply_global_styles

# ── Survey link redirect ──────────────────────────────────────────────────────
# If someone opens the app with ?survey=... redirect straight to the form
if "survey" in st.query_params:
    st.switch_page("pages/2_Respond.py")

st.set_page_config(
    page_title="Survey Studio",
    page_icon=None,
    layout="wide",
)
apply_global_styles()

st.title("Survey Studio")
st.caption("Build, share, and analyze surveys — your data stays yours.")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 01 — Build")
    st.markdown("""
Design your survey on the **Build** page. Add Likert rating questions
or open-ended questions. Customize scale labels. Save a session file
to resume editing later.
    """)

with col2:
    st.markdown("#### 02 — Share")
    st.markdown("""
Copy the shareable link from the Build page and send it to respondents.
They open it in any browser — no account needed. Download the collected
responses as a CSV when you're ready.
    """)

with col3:
    st.markdown("#### 03 — Analyze")
    st.markdown("""
Upload your responses CSV on the **Analyze** page. See score distributions,
sentiment breakdowns, and extracted themes. Download clean summary CSVs
for reporting.
    """)

st.divider()

st.markdown("""
<div style='font-size:12px; color:#334155; text-align:center; letter-spacing:0.06em; text-transform:uppercase;'>
No database · No accounts · No data leaves your browser
</div>
""", unsafe_allow_html=True)