# Survey Jam

A lightweight, open-source survey platform. Build custom surveys, collect responses via shareable link, and instantly visualize results — no database, no accounts, no data leaves your hands.

**[Try the live app →](https://survey-jam.streamlit.app)**

---

## What it does

**Build** — Design Likert-scale and open-ended questions in a visual editor. Customize scale labels. Save your survey as a session file to resume later.

**Share** — Generate a shareable link that encodes your survey config directly in the URL. Respondents open it in any browser with no login required.

**Analyze** — Upload your collected responses CSV to see score distributions, sentiment analysis, and theme extraction powered by DistilBERT and TF-IDF.

---

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | Streamlit |
| Charts | Plotly |
| NLP | HuggingFace Transformers (DistilBERT) |
| Theme extraction | Scikit-learn TF-IDF |
| Data | Pandas, NumPy |

---

## Run locally

```bash
git clone https://github.com/dannygme/survey-jam.git
cd survey-jam
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run Home.py
```

---

## Project structure

```
survey-jam/
├── Home.py               # Landing page
├── pages/
│   ├── 1_Build.py        # Survey builder
│   ├── 2_Respond.py      # Respondent form
│   └── 3_Analyze.py      # Analysis dashboard
├── scripts/
│   ├── config.py         # Survey config schema
│   ├── preprocess.py     # CSV cleaning and parsing
│   └── analysis.py       # Likert stats + NLP
├── utils/
│   └── styles.py         # Global CSS
└── requirements.txt
```

---

## Privacy

Responses are held in the browser session and only saved when the creator downloads the CSV. No server storage, no third-party data collection.

---

*Work in progress — advanced analytics and export features coming soon.*