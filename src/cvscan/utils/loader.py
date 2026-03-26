"""
utils/loader.py
Handles loading resumes and role keyword data.
"""

import json
import importlib.resources as pkg_resources

from cvscan.parser.pdf_parser import extract_text_pdf
from cvscan.parser.docx_parser import extract_text_docx


def load_resume(file: str) -> str:
    """
    Load and return raw text from a resume file.
    Supports: .pdf, .docx, .txt
    """
    if file.endswith(".pdf"):
        return extract_text_pdf(file)
    elif file.endswith(".docx"):
        return extract_text_docx(file)
    elif file.endswith(".txt"):
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"TXT Error: {e}")
            return ""
    else:
        raise ValueError(
            f"Unsupported file format: '{file}'. "
            "Supported formats: .pdf, .docx, .txt"
        )


def load_keywords(role: str) -> dict:
    """Return the keyword data for a given role, or {} if not found."""
    with pkg_resources.files("cvscan.data").joinpath("roles.json").open() as f:
        data = json.load(f)
    return data.get(role.lower(), {})


def load_all_roles() -> list[str]:
    """Return a sorted list of all available role names."""
    with pkg_resources.files("cvscan.data").joinpath("roles.json").open() as f:
        data = json.load(f)
    return sorted(data.keys())
