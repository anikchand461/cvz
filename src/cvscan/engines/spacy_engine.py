"""
engines/spacy_engine.py
Semantic similarity scoring using spaCy word vectors.
Falls back to 0 gracefully if the model is not installed.
Model is loaded lazily — only when spacy_score() is first called,
so importing this module does NOT slow down startup.

If no model is found, the user is prompted once to download
en_core_web_md (~43 MB). If they decline, semantic scoring is
disabled for the rest of the session.
"""

import subprocess
import sys
import spacy

_nlp = None
_model_warned = False
_load_attempted = False


def _try_download_model() -> bool:
    """
    Prompt the user to download en_core_web_md.
    Returns True if download succeeded, False otherwise.
    """
    try:
        answer = input(
            "\nspaCy model not found. Download en_core_web_md (~43 MB) for semantic scoring? [y/N]: "
        ).strip().lower()
    except (EOFError, KeyboardInterrupt):
        # Non-interactive environment or user cancelled
        return False

    if answer != "y":
        print("Skipping download — semantic scoring will be disabled.")
        return False

    print("Downloading en_core_web_md...")
    result = subprocess.run(
        [sys.executable, "-m", "spacy", "download", "en_core_web_md"],
        capture_output=False,
    )
    return result.returncode == 0


def _load_model():
    """Lazy-load the spaCy model once and cache it."""
    global _nlp, _model_warned, _load_attempted

    if _load_attempted:
        return _nlp

    _load_attempted = True

    # Try loading any already-installed model
    for model in ("en_core_web_md", "en_core_web_lg", "en_core_web_sm"):
        try:
            _nlp = spacy.load(model)
            if model == "en_core_web_sm" and not _model_warned:
                print(
                    "Warning: Using en_core_web_sm — semantic scores will be less accurate. "
                    "Run: python -m spacy download en_core_web_md"
                )
                _model_warned = True
            return _nlp
        except OSError:
            continue

    # No model found — offer to download
    downloaded = _try_download_model()

    if downloaded:
        try:
            _nlp = spacy.load("en_core_web_md")
            return _nlp
        except OSError:
            print("Download may have failed. Semantic scoring disabled.")

    if not _model_warned:
        print("Warning: No spaCy model available — semantic scoring disabled.")
        _model_warned = True

    return None


def spacy_score(resume: str, job_desc: str) -> float:
    """
    Returns 0–100 cosine similarity between the resume and the job description.
    Returns 0 if spaCy is unavailable.
    Model is loaded (and optionally downloaded) on first call only.
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
