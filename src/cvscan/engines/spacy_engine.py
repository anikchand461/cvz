"""
engines/spacy_engine.py
Semantic similarity scoring using spaCy word vectors.

en_core_web_md is downloaded automatically at install time (see setup.py),
so no runtime prompts or download logic is needed here.
Falls back to 0 gracefully if the model is somehow unavailable.
Model is loaded lazily — only when spacy_score() is first called.
"""

import spacy

_nlp = None
_load_attempted = False


def _load_model():
    """Lazy-load the spaCy model once and cache it."""
    global _nlp, _load_attempted

    if _load_attempted:
        return _nlp

    _load_attempted = True

    for model in ("en_core_web_md", "en_core_web_lg", "en_core_web_sm"):
        try:
            _nlp = spacy.load(model)
            if model == "en_core_web_sm":
                print(
                    "Warning: Using en_core_web_sm — scores will be less accurate. "
                    "Run: python -m spacy download en_core_web_md"
                )
            return _nlp
        except OSError:
            continue

    print("Warning: No spaCy model found — semantic scoring disabled.")
    return None


def spacy_score(resume: str, job_desc: str) -> float:
    """
    Returns 0–100 cosine similarity between resume and job description.
    Returns 0.0 if spaCy is unavailable.
    """
    nlp = _load_model()
    if nlp is None:
        return 0.0

    try:
        doc1 = nlp(resume[:100_000])
        doc2 = nlp(job_desc[:10_000])
        if not doc1.has_vector or not doc2.has_vector:
            return 0.0
        return doc1.similarity(doc2) * 100
    except Exception:
        return 0.0
