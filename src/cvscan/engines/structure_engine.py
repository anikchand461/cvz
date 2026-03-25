def structure_score(text):
    sections = ["education", "experience", "skills", "projects"]

    found = sum(1 for s in sections if s in text)

    length_score = min(len(text.split()) / 500, 1)

    score = (found / len(sections)) * 70 + length_score * 30
    return score
