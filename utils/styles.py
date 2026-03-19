import streamlit as st


def apply_global_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 18px !important;
    }

    .stApp { background-color: #0a0a0f; }

    section[data-testid="stSidebar"] {
        background-color: #0d0d14 !important;
        border-right: 1px solid rgba(0,245,212,0.12) !important;
        min-width: 260px !important;
    }
    section[data-testid="stSidebar"] * {
        font-size: 17px !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        font-size: 16px !important;
        color: #64748b;
        padding: 0 1rem;
        line-height: 1.6;
    }
    section[data-testid="stSidebar"] a {
        font-size: 17px !important;
        font-weight: 500 !important;
        color: #94a3b8 !important;
        letter-spacing: 0.02em;
    }
    section[data-testid="stSidebar"] a:hover { color: #00f5d4 !important; }

    h1 { font-size: 2.25rem !important; font-weight: 600 !important; color: #f1f5f9 !important; letter-spacing: -0.02em; }
    h2 { font-size: 1.35rem !important; font-weight: 500 !important; color: #00f5d4 !important; text-transform: uppercase; letter-spacing: 0.08em; }
    h3 { font-size: 1.2rem !important;  font-weight: 500 !important; color: #e2e8f0 !important; }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #00f5d4 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.7rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #475569 !important;
    }

    .stButton > button {
        background: transparent !important;
        border: 1px solid rgba(0,245,212,0.4) !important;
        color: #00f5d4 !important;
        border-radius: 6px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        letter-spacing: 0.04em;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: rgba(0,245,212,0.08) !important;
        border-color: #00f5d4 !important;
        box-shadow: 0 0 12px rgba(0,245,212,0.15);
    }
    button[kind="primary"] {
        background: rgba(0,245,212,0.12) !important;
        border-color: #00f5d4 !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #0d0d14 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 6px !important;
        color: #e2e8f0 !important;
        font-size: 16px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(0,245,212,0.4) !important;
        box-shadow: 0 0 0 2px rgba(0,245,212,0.08) !important;
    }

    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: #0d0d14 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 6px !important;
    }
    .stRadio > div { gap: 0.5rem; }
    .stRadio label { font-size: 15px !important; color: #94a3b8 !important; }

    [data-testid="stFileUploader"] {
        background: #0d0d14 !important;
        border: 1px dashed rgba(0,245,212,0.2) !important;
        border-radius: 8px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.06) !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: #64748b !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.5rem 1.25rem !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00f5d4 !important;
        border-bottom: 2px solid #00f5d4 !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 8px !important;
    }

    div[data-testid="stExpander"] {
        background: #111118 !important;
        border: 1px solid rgba(0,245,212,0.1) !important;
        border-radius: 10px !important;
    }

    hr { border-color: rgba(255,255,255,0.06) !important; }

    .stCaption, small { color: #475569 !important; font-size: 13px !important; }
    .stInfo {
        background: rgba(0,245,212,0.05) !important;
        border: 1px solid rgba(0,245,212,0.15) !important;
        border-radius: 8px !important;
        color: #94a3b8 !important;
    }
    .stSuccess {
        background: rgba(0,245,212,0.08) !important;
        border: 1px solid rgba(0,245,212,0.2) !important;
        border-radius: 8px !important;
    }
    .stWarning {
        background: rgba(239,159,39,0.08) !important;
        border: 1px solid rgba(239,159,39,0.2) !important;
        border-radius: 8px !important;
    }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0a0a0f; }
    ::-webkit-scrollbar-thumb { background: rgba(0,245,212,0.2); border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0,245,212,0.4); }

    div[role="radiogroup"] label {
        white-space: normal !important;
        line-height: 1.3;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 90px;
    }
    </style>
    """, unsafe_allow_html=True)