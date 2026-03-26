"""
utils/scorer.py
Shared scoring helpers used across CLI commands.
"""

from cvscan.utils.loader import load_keywords, load_all_roles
from cvscan.engines.keyword_engine import keyword_score
from cvscan.engines.spacy_engine import spacy_score
from cvscan.engines.structure_engine import structure_score


def flatten_role(role_data: dict) -> list[str]:
    """Flatten core + secondary keyword groups into a single list."""
    return [
        kw
        for group in (role_data.get("core", []) + role_data.get("secondary", []))
        for kw in group
    ]


def get_best_role_and_score(text: str, return_all: bool = False):
    """
    Score `text` against every role and return the best match.

    Uses the same 50/30/20 weights as the analyze command so that
    auto-detected roles and final scores are always consistent.
    Semantic contribution is gated: if keyword score is very low
    (<20), semantic weight is halved to avoid a weak resume being
    carried by corpus-level vector similarity.

    Args:
        text:        Cleaned resume text.
        return_all:  If True, return the full sorted list instead of just the top result.

    Returns:
        (role, score) tuple  — or list of (role, score) tuples if return_all=True.
    """
    roles = load_all_roles()
    st_score = structure_score(text)
    results = []

    for role in roles:
        role_data = load_keywords(role)
        flat = flatten_role(role_data)

        k_score, _ = keyword_score(text, role_data)
        s_score = spacy_score(text, " ".join(flat))

        # Gate semantic contribution when keyword match is very weak
        s_weight = 0.3 if k_score >= 20 else 0.15
        k_weight = 1.0 - s_weight - 0.2

        final = k_weight * k_score + s_weight * s_score + 0.2 * st_score
        results.append((role, final))

    results.sort(key=lambda x: x[1], reverse=True)

    if return_all:
        return results
    return results[0]
