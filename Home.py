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

<<<<<<< HEAD
=======
st.title("Survey Jam")
st.caption("Build, share, and analyze surveys. Your data stays yours.")
>>>>>>> 8f2a0c7bedd337044b7118e2572924637b376f5d
st.divider()

# ── Three columns ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

HAMMER = """\
        ████          
      ██▒▒░░██        
        ██▒▒████      
          ██▒▒▒▒██    
          ██▒▒▓▓████  
        ██▒▒████▒▒░░██
      ██▒▒██    ██▒▒██
    ██▒▒██        ██  
  ██▒▒██              
  ████                
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
  Positive  ██████████  52%
  Neutral   ███████     31%
  Negative  ████        17%
                            
  ┌──────────────────┐  
  │  Score  3.8/5.0  │  
  │  Responses  ●24  │  
  │  Themes  ●●●  7  │  
  └──────────────────┘  
                            
"""

with col1:
    components.html(f"""
<style>
  body {{ margin:0; background:transparent; }}
  .step-header {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 1.05rem;
    font-weight: 600;
    color: #00f5d4;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
  }}
  .flap {{
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #e2e8f0;
  }}
</style>
<div class="step-header">01 — <span class="flap" id="lbl"></span></div>
<script>
const CHARS='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@!%&';
const word='BUILD';
let it=0;
const total=10*word.length;
const iv=setInterval(()=>{{
  document.getElementById('lbl').innerHTML=word.split('').map((c,i)=>{{
    if(it>i*10) return c;
    return '<span style="color:#00f5d4;opacity:0.5">'+CHARS[Math.floor(Math.random()*CHARS.length)]+'</span>';
  }}).join('');
  it++;
  if(it>total){{ clearInterval(iv); document.getElementById('lbl').innerText=word; }}
}},40);
</script>
""", height=36)
    st.markdown("Design your survey. Add Likert or open-ended questions. Customize scale labels. Download as CSV or JSON to send to respondents.")
    st.code(HAMMER, language=None)
    if st.button("Go to Build →", key="nav_build", use_container_width=True):
        st.switch_page("pages/1_Build.py")

with col2:
<<<<<<< HEAD
    components.html(f"""
<style>
  body {{ margin:0; background:transparent; }}
  .step-header {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 1.05rem;
    font-weight: 600;
    color: #00f5d4;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
  }}
  .flap {{
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #e2e8f0;
  }}
</style>
<div class="step-header">02 — <span class="flap" id="lbl"></span></div>
<script>
const CHARS='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@!%&';
const word='SHARE';
let it=0;
const total=10*word.length;
setTimeout(()=>{{
  const iv=setInterval(()=>{{
    document.getElementById('lbl').innerHTML=word.split('').map((c,i)=>{{
      if(it>i*10) return c;
      return '<span style="color:#00f5d4;opacity:0.5">'+CHARS[Math.floor(Math.random()*CHARS.length)]+'</span>';
    }}).join('');
    it++;
    if(it>total){{ clearInterval(iv); document.getElementById('lbl').innerText=word; }}
  }},40);
}},350);
</script>
""", height=36)
    st.markdown("Send the downloaded file to respondents via email, Slack, or any channel. They fill it in and send it back. No app access needed.")
    st.code(DOCUMENT, language=None)
=======
    st.markdown("#### 02 — Share")
    st.markdown("""
Copy the shareable link from the Build page and send it to respondents.
They open it in any browser. No account needed. Download the collected
responses as a CSV when you're ready.
    """)
>>>>>>> 8f2a0c7bedd337044b7118e2572924637b376f5d

with col3:
    components.html(f"""
<style>
  body {{ margin:0; background:transparent; }}
  .step-header {{
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 1.05rem;
    font-weight: 600;
    color: #00f5d4;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
  }}
  .flap {{
    display: inline-block;
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #e2e8f0;
  }}
</style>
<div class="step-header">03 — <span class="flap" id="lbl"></span></div>
<script>
const CHARS='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@!%&';
const word='ANALYZE';
let it=0;
const total=10*word.length;
setTimeout(()=>{{
  const iv=setInterval(()=>{{
    document.getElementById('lbl').innerHTML=word.split('').map((c,i)=>{{
      if(it>i*10) return c;
      return '<span style="color:#00f5d4;opacity:0.5">'+CHARS[Math.floor(Math.random()*CHARS.length)]+'</span>';
    }}).join('');
    it++;
    if(it>total){{ clearInterval(iv); document.getElementById('lbl').innerText=word; }}
  }},40);
}},700);
</script>
""", height=36)
    st.markdown("Upload response CSVs to see score distributions, sentiment breakdowns, and extracted themes. Works with any compatible survey CSV.")
    st.code(CHART, language=None)
    if st.button("Go to Analyze →", key="nav_analyze", use_container_width=True):
        st.switch_page("pages/3_Analyze.py")

st.divider()

st.markdown("""
<div style='font-size:12px; color:#334155; text-align:center;
letter-spacing:0.06em; text-transform:uppercase;'>
<<<<<<< HEAD
No database · No accounts · No data leaves your hands
=======
No database · No accounts · No data leaves your browser
>>>>>>> 8f2a0c7bedd337044b7118e2572924637b376f5d
</div>
""", unsafe_allow_html=True)
