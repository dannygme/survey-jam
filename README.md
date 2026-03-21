# Survey Jam

A lightweight, open-source survey platform. Build custom surveys, distribute them manually, and instantly visualize results. No database, no accounts, no data leaves your hands.

**[Try the live app](https://survey-jam.streamlit.app)**

---

## What it does

**Build**: Design Likert-scale and open-ended questions in a visual editor. Customize scale labels (e.g. "Never" to "Always" for frequency questions). Preview your survey in real time. Download your survey as a CSV (for respondents to fill in) or JSON (to reimport later). Save a session file to resume editing at any time.

**Share**: Send the downloaded CSV to respondents via email, Slack, or any channel you prefer. Respondents fill it in directly and send it back. No app access or account needed on their end.

**Analyze**: Upload one or more response CSVs to see score distributions, sentiment analysis powered by DistilBERT, and theme extraction via TF-IDF. Works as a standalone analysis tool for any compatible survey CSV, not just surveys built in Survey Jam.

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
├── Home.py                   # Landing page with animated header
├── pages/
│   ├── 1_Build.py            # Survey builder + CSV/JSON download
│   └── 3_Analyze.py          # Analysis dashboard
├── scripts/
│   ├── config.py             # Survey config schema and validators
│   ├── preprocess.py         # CSV cleaning and parsing
│   └── analysis.py           # Likert stats + sentiment + themes
├── utils/
│   └── styles.py             # Global dark theme CSS
└── requirements.txt
```

---

## How the survey distribution works

1. Creator builds a survey on the Build page
2. Downloads the survey as a CSV file, pre-formatted with question columns and a blank row for each respondent
3. Sends the file to respondents via any channel
4. Respondents fill in their answers and send the CSV back
5. Creator uploads the CSV(s) on the Analyze page to see results

No server, no database, no third-party data collection at any step.

---

## Privacy

Response data is never stored on any server. Everything is processed locally in the browser session. Closing the tab without downloading discards all data.

---

*Work in progress. Advanced analytics and export features planned for v2.*
