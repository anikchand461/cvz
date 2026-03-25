import json
import importlib.resources as pkg_resources

from cvscan.parser.pdf_parser import extract_text_pdf
from cvscan.parser.docx_parser import extract_text_docx


def load_resume(file):
    if file.endswith(".pdf"):
        return extract_text_pdf(file)
    elif file.endswith(".docx"):
        return extract_text_docx(file)
    else:
        raise ValueError("Unsupported file format")


def load_keywords(role):
    with pkg_resources.files("cvscan.data").joinpath("roles.json").open() as f:
        data = json.load(f)
    return data.get(role.lower(), [])


def load_all_roles():
    with pkg_resources.files("cvscan.data").joinpath("roles.json").open() as f:
        data = json.load(f)
    return list(data.keys())
