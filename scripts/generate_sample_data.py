"""
generate_sample_data.py
-----------------------
Generates a realistic synthetic CSV for immediate testing.
Produces realistic Likert patterns (correlated dimensions, a few outlier
respondents) and varied free-text responses.

Usage:
    python scripts/generate_sample_data.py
    python scripts/generate_sample_data.py --n 100 --seed 99 --out data/survey_responses.csv
"""

import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import numpy as np

LIKERT_QUESTIONS = [
    "1. I feel engaged and motivated by my daily work responsibilities.",
    "2. I receive useful feedback that helps me grow professionally.",
    "3. My workload is manageable and sustainable.",
    "4. My contributions are recognized and appreciated.",
    "5. I maintain a healthy balance between work and personal life.",
    "6. Our team culture is inclusive, supportive, and collaborative.",
    "7. I have access to learning opportunities that support my development.",
    "8. I feel psychologically safe to share ideas and raise concerns.",
]

FREE_TEXT_Q9 = (
    "9. What is one specific change that would most improve your engagement or satisfaction?"
)
FREE_TEXT_Q10 = (
    "10. Any additional comments or suggestions? (Optional)"
)

Q9_RESPONSES = [
    "More frequent one-on-one meetings with my manager would help.",
    "Clearer goals and OKRs at the start of each quarter.",
    "Flexible remote work options would improve my work-life balance significantly.",
    "Better cross-team communication channels and async updates.",
    "Recognition programs like peer shoutouts would go a long way.",
    "Access to an annual learning budget for courses and conferences.",
    "Reducing the number of unnecessary status meetings.",
    "A mentorship pairing program would accelerate my growth.",
    "More transparency from leadership on company direction.",
    "Improved onboarding documentation for new tools.",
    "Regular team retrospectives to surface and address friction early.",
    "Dedicated focus time blocks protected from interruptions.",
    "Salary benchmarking review — I feel underpaid relative to market.",
    "Clearer promotion criteria and career ladder documentation.",
    "Better project management tooling to reduce context switching.",
]

Q10_RESPONSES = [
    "Overall I enjoy working here but there is room to improve transparency.",
    "The team is great. The tooling could be modernised.",
    "Happy with my role but growth opportunities are limited.",
    "",  # blank — some respondents skip this
    "",
    "Management is supportive. Would appreciate more async-friendly processes.",
    "The culture is positive. Would like to see more DEI initiatives.",
    "Nothing to add for now.",
    "",
    "Please consider a four-day work week pilot.",
]


def _clamp(v: float, lo=1, hi=5) -> int:
    return int(np.clip(round(v), lo, hi))


def generate(n: int = 50, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    random.seed(seed)
    rows = []
    base_time = datetime(2026, 3, 1, 9, 0, 0, tzinfo=timezone.utc)

    for i in range(n):
        respondent_id = f"resp_{uuid.UUID(int=rng.integers(0, 2**128)).hex[:8]}"
        ts = base_time + timedelta(
            days=rng.integers(0, 17).item(),
            hours=rng.integers(0, 8).item(),
            minutes=rng.integers(0, 60).item(),
        )
        timestamp = ts.isoformat()

        # Each respondent has a latent "satisfaction level" ~ N(3.2, 0.6)
        # with some dispersion per question
        baseline = float(rng.normal(3.2, 0.6))

        # Q3 (workload) and Q5 (balance) tend to score lower
        offsets = [0.0, 0.1, -0.4, 0.1, -0.3, 0.2, 0.0, 0.0]

        for j, q in enumerate(LIKERT_QUESTIONS):
            score = _clamp(float(rng.normal(baseline + offsets[j], 0.7)))
            rows.append(
                {
                    "respondent_id": respondent_id,
                    "timestamp": timestamp,
                    "question": q,
                    "response": str(score),
                }
            )

        # Q9 — everyone answers
        rows.append(
            {
                "respondent_id": respondent_id,
                "timestamp": timestamp,
                "question": FREE_TEXT_Q9,
                "response": random.choice(Q9_RESPONSES),
            }
        )

        # Q10 — ~60% answer
        q10_response = random.choice(Q10_RESPONSES)
        if q10_response:
            rows.append(
                {
                    "respondent_id": respondent_id,
                    "timestamp": timestamp,
                    "question": FREE_TEXT_Q10,
                    "response": q10_response,
                }
            )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic survey data.")
    parser.add_argument("--n", type=int, default=50, help="Number of respondents")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", default="data/survey_responses.csv", help="Output path")
    args = parser.parse_args()

    df = generate(n=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Generated {args.n} respondents → {len(df)} rows → {out}")