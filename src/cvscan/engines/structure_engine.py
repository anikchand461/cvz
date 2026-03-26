"""
engines/structure_engine.py
Scores a resume based on the presence of standard sections and overall length.
"""

# Weighted sections: (keyword, weight)
# Core sections are worth more; supplementary sections add a small bonus.
SECTIONS = [
    # core — expected in almost every resume
    ("education", 2.0),
    ("experience", 2.0),
    ("skills", 2.0),
    ("projects", 1.5),
    # supplementary — good to have
    ("summary", 1.0),
    ("objective", 0.5),
    ("certifications", 1.0),
    ("achievements", 1.0),
    ("awards", 0.5),
    ("contact", 0.5),
    ("publications", 0.5),
    ("languages", 0.5),
    ("volunteer", 0.5),
    ("internship", 0.5),
]

MAX_SECTION_SCORE = sum(w for _, w in SECTIONS)
TARGET_WORD_COUNT = 650   # resumes shorter than this are penalised


def structure_score(text: str) -> float:
    """
    Returns a 0–100 score based on:
      - 70 pts: weighted presence of standard resume sections
      - 30 pts: resume length (normalised against TARGET_WORD_COUNT)
    """
    section_score = sum(w for kw, w in SECTIONS if kw in text)
    normalised_section = min(section_score / MAX_SECTION_SCORE, 1.0)

    word_count = len(text.split())
    length_score = min(word_count / TARGET_WORD_COUNT, 1.0)

    return normalised_section * 70 + length_score * 30
