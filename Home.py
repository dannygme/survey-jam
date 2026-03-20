
"""
Home.py
-------
Landing page. Run with: streamlit run Home.py
"""

import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent))
from utils.styles import apply_global_styles

st.set_page_config(
    page_title="Survey Jam",
    page_icon=None,
    layout="wide",
)

apply_global_styles()

# ── Title with rolodex effect ─────────────────────────────────────────────────
components.html("""
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
  body { margin:0; background:transparent; }
  .title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: 0.08em;
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
  }
  .flap-char { display: inline-block; }
</style>
<div class="title" id="title"></div>
<script>
const CHARS='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@!%&';
const word='SURVEY JAM';
let it=0;
const total=10*word.length;
const iv=setInterval(()=>{
  document.getElementById('title').innerHTML=word.split('').map((c,i)=>{
    if(c===' ') return '&nbsp;';
    if(it>i*10) return c==='&nbsp;'?'&nbsp;':c;
    return '<span style="color:#00f5d4;opacity:0.6">'+CHARS[Math.floor(Math.random()*CHARS.length)]+'</span>';
  }).join('');
  it++;
  if(it>total){
    clearInterval(iv);
    document.getElementById('title').innerHTML=word.replace(/ /g,'&nbsp;');
  }
},40);
</script>
""", height=90)

st.markdown(
    "<div style='text-align:center; color:#475569; font-size:0.95rem; "
    "letter-spacing:0.04em; margin-bottom:1rem;'>"
    "Build, share, and analyze surveys. Your data stays yours."
    "</div>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

HAMMER = """\
██████████████
██████████████
██████████████
     ███
     ███
     ███
     ███
     ███
    █████
"""

DOCUMENT = """\
┌─────────────┐
│  Survey     │
│  ────────── │
│  ────────── │
│  ────────── │
│             │
│  ────────── │
│  ────────── │
│  ────────── │
└─────────────┘
"""

CHART = """\
Positive ██████████ 52%
Neutral  ███████    31%
Negative ████       17%

┌─────────────────┐
│  Score  3.8/5.0 │
│  Responses  ●24 │
│  Themes  ●●●  7 │
└─────────────────┘
"""

CARD_HEIGHT = 420

def card_html(num, word, delay_ms, description, ascii_art):
    escaped = ascii_art.replace("\\", "\\\\").replace("`", "\\`")
    return f"""
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
  body {{ margin:0; background:transparent; }}
  .card {{
    display: flex;
    flex-direction: column;
    height: {CARD_HEIGHT}px;
    align-items: center;
  }}
  .step-header {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.05rem;
    font-weight: 600;
    color: #00f5d4;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
    width: 100%;
  }}
  .flap {{
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #e2e8f0;
  }}
  .desc {{
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: #94a3b8;
    line-height: 1.6;
    margin-bottom: 12px;
    width: 100%;
  }}
  .ascii-wrap {{
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    flex-grow: 1;
    background: rgba(0,245,212,0.03);
    border: 1px solid rgba(0,245,212,0.08);
    border-radius: 8px;
    padding: 12px 8px;
  }}
  .ascii {{
    display: inline-block;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', monospace;
    font-variant-ligatures: none;
    font-size: 0.78rem;
    line-height: 1.4;
    color: #00f5d4;
    white-space: pre;
    text-align: left;
    margin: 0;
    padding: 0;
  }}
</style>
<div class="card">
  <div class="step-header">{num} — <span class="flap" id="lbl-{num}"></span></div>
  <div class="desc">{description}</div>
  <div class="ascii-wrap"><pre class="ascii">{ascii_art.strip()}</pre></div>
</div>
<script>
const CHARS='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@!%&';
const word='{word}';
let it=0;
const total=10*word.length;
setTimeout(()=>{{
  const el=document.getElementById('lbl-{num}');
  const iv=setInterval(()=>{{
    el.innerHTML=word.split('').map((c,i)=>{{
      if(it>i*10) return c;
      return '<span style="color:#00f5d4;opacity:0.5">'+CHARS[Math.floor(Math.random()*CHARS.length)]+'</span>';
    }}).join('');
    it++;
    if(it>total){{ clearInterval(iv); el.innerText=word; }}
  }},40);
}},{delay_ms});
</script>
"""

with col1:
    components.html(
        card_html("01", "BUILD", 0,
            "Design your survey. Add Likert or open-ended questions. Customize scale labels. Download as CSV or JSON to send to respondents.",
            HAMMER),
        height=CARD_HEIGHT + 10
    )
    if st.button("Go to Build →", key="nav_build", use_container_width=True):
        st.switch_page("pages/1_Build.py")

with col2:
    components.html(
        card_html("02", "SHARE", 350,
            "Send the downloaded file to respondents via email, Slack, or any channel. They fill it in and send it back. No app access needed.",
            DOCUMENT),
        height=CARD_HEIGHT + 10
    )
    st.markdown("<div style='height:38px'></div>", unsafe_allow_html=True)

with col3:
    components.html(
        card_html("03", "ANALYZE", 700,
            "Upload response CSVs to see score distributions, sentiment breakdowns, and extracted themes. Works with any compatible survey CSV.",
            CHART),
        height=CARD_HEIGHT + 10
    )
    if st.button("Go to Analyze →", key="nav_analyze", use_container_width=True):
        st.switch_page("pages/3_Analyze.py")

st.divider()

st.markdown("""
<div style='font-size:12px; color:#334155; text-align:center;
letter-spacing:0.06em; text-transform:uppercase;'>
No database · No accounts · No data leaves your hands
</div>
""", unsafe_allow_html=True)
