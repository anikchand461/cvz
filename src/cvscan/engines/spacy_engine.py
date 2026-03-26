"""
engines/spacy_engine.py
Semantic similarity scoring using spaCy word vectors.

en_core_web_md is downloaded automatically on the very first cvz run
if not already present — no prompts, no manual steps needed.
Model is loaded lazily; importing this module does NOT slow startup.
"""

import subprocess
import sys
import spacy

_nlp = None
_load_attempted = False


def _ensure_model() -> bool:
    """
    Check if en_core_web_md is available; download it silently if not.
    Returns True if a usable model is available after this call.
    """
    for model in ("en_core_web_md", "en_core_web_lg"):
        try:
            spacy.load(model)
            return True
        except OSError:
            continue

    # Not found — download silently
    print("⬇  First run: downloading spaCy model en_core_web_md (~43 MB)...")
    result = subprocess.run(
        [sys.executable, "-m", "spacy", "download", "en_core_web_md"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        print("✔  Model ready.\n")
        return True

    print(
        "⚠  Auto-download failed. Run manually:\n"
        "   python -m spacy download en_core_web_md\n"
    )
    return False


def _load_model():
    """Lazy-load the spaCy model once and cache it."""
    global _nlp, _load_attempted

    if _load_attempted:
        return _nlp

    _load_attempted = True
    _ensure_model()

    for model in ("en_core_web_md", "en_core_web_lg", "en_core_web_sm"):
        try:
            _nlp = spacy.load(model)
            if model == "en_core_web_sm":
                print(
                    "Warning: Using en_core_web_sm — scores will be less accurate.\n"
                    "Run: python -m spacy download en_core_web_md"
                )
            return _nlp
        except OSError:
            continue

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
