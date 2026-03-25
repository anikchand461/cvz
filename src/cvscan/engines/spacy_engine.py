import spacy

try:
    nlp = spacy.load("en_core_web_md")  # ✅ upgraded
except:
    nlp = None


def spacy_score(resume, job_desc):
    if not nlp:
        return 0

    try:
        doc1 = nlp(resume[:100000])
        doc2 = nlp(job_desc)
        return doc1.similarity(doc2) * 100
    except:
        return 0
