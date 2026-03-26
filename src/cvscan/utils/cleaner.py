"""
utils/cleaner.py
Text normalisation for resume content before scoring.
"""

import re


def clean_text(text: str) -> str:
    """
    Normalise resume text for keyword and semantic matching.

    Steps:
      1. Lowercase
      2. Replace hyphens and slashes with spaces (e.g. "full-stack" → "full stack")
      3. Strip all non-alphanumeric characters except spaces
      4. Collapse multiple spaces
    """
    text = text.lower()
    text = text.replace("-", " ").replace("/", " ").replace("_", " ")
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()
