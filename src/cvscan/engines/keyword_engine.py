"""
engines/keyword_engine.py
Keyword-based resume scoring.

Scoring breakdown:
  core keywords     → 70 pts
  secondary keywords → 30 pts

Keywords are grouped: a group is "matched" if ANY keyword in the group
is found in the resume text (synonym/alias support).

Matching uses whole-word regex to avoid false positives like
"go" matching "django" or "r" matching any word containing "r".
"""

import re


def match_group(text: str, group: list[str]) -> bool:
    """Return True if at least one keyword in the group appears as a whole word in text."""
    return any(re.search(r"\b" + re.escape(k) + r"\b", text) for k in group)


def keyword_score(text: str, role_data: dict) -> tuple[float, list]:
    """
    Score resume text against a role's keyword groups.

    Returns:
        (score: float 0–100, matched_groups: list)
    """
    core = role_data.get("core", [])
    secondary = role_data.get("secondary", [])

    matched_core = [g for g in core if match_group(text, g)]
    matched_secondary = [g for g in secondary if match_group(text, g)]

    core_score = (len(matched_core) / len(core)) * 70 if core else 0
    secondary_score = (len(matched_secondary) / len(secondary)) * 30 if secondary else 0

    return core_score + secondary_score, matched_core + matched_secondary
