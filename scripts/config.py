"""
config.py
---------
Single source of truth for loading and validating survey_config.json.
Imported by preprocess.py, analysis.py, dashboard.py, builder.py,
and responder.py — no script should define question lists itself.
"""

import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATH = "data/survey_config.json"

# ── Schema validation ──────────────────────────────────────────────────────────

REQUIRED_TOP_KEYS = {"survey_title", "questions", "likert_scale"}
REQUIRED_Q_KEYS   = {"number", "text", "type", "label", "required"}
VALID_Q_TYPES     = {"likert", "freetext"}


def _validate(cfg: dict) -> None:
    missing = REQUIRED_TOP_KEYS - cfg.keys()
    if missing:
        sys.exit(f"[config] survey_config.json missing keys: {missing}")
    if not isinstance(cfg["questions"], list) or not cfg["questions"]:
        sys.exit("[config] 'questions' must be a non-empty list.")
    for i, q in enumerate(cfg["questions"]):
        missing_q = REQUIRED_Q_KEYS - q.keys()
        if missing_q:
            sys.exit(f"[config] Question {i} missing keys: {missing_q}")
        if q["type"] not in VALID_Q_TYPES:
            sys.exit(
                f"[config] Question {i} has invalid type '{q['type']}'. "
                f"Must be one of {VALID_Q_TYPES}."
            )
    nums = [q["number"] for q in cfg["questions"]]
    if len(nums) != len(set(nums)):
        sys.exit("[config] Question numbers must be unique.")


# ── Public API ─────────────────────────────────────────────────────────────────

def load_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    """Load and validate survey_config.json. Returns the config dict."""
    p = Path(path)
    if not p.exists():
        sys.exit(
            f"[config] Config file not found: {path}\n"
            "Run builder.py to create one, or copy data/survey_config.json."
        )
    with open(p, encoding="utf-8") as f:
        cfg = json.load(f)
    _validate(cfg)
    return cfg


def save_config(cfg: dict, path: str = DEFAULT_CONFIG_PATH) -> None:
    """Validate and write config to disk."""
    _validate(cfg)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# ── Convenience accessors ──────────────────────────────────────────────────────

def get_likert_questions(cfg: dict) -> list[dict]:
    return [q for q in cfg["questions"] if q["type"] == "likert"]


def get_freetext_questions(cfg: dict) -> list[dict]:
    return [q for q in cfg["questions"] if q["type"] == "freetext"]


def get_question_labels(cfg: dict) -> dict[int, str]:
    """Returns {q_number: label} for all questions."""
    return {q["number"]: q["label"] for q in cfg["questions"]}


def get_question_texts(cfg: dict) -> dict[int, str]:
    """Returns {q_number: full question text} for all questions."""
    return {q["number"]: q["text"] for q in cfg["questions"]}


def get_likert_scale(cfg: dict) -> dict[str, Any]:
    return cfg["likert_scale"]


def full_question_text(q: dict) -> str:
    """Canonical text stored in CSV: '3. My workload is manageable...'"""
    return f"{q['number']}. {q['text']}"


def make_empty_config() -> dict:
    """Return a blank config template for builder.py to populate."""
    return {
        "survey_title": "New Survey",
        "survey_description": "",
        "created_at": "",
        "questions": [],
        "likert_scale": {
            "min": 1,
            "max": 5,
            "labels": {
                "1": "Strongly disagree",
                "2": "Disagree",
                "3": "Neutral",
                "4": "Agree",
                "5": "Strongly agree",
            },
        },
    }