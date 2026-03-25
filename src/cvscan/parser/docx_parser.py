from docx import Document

def extract_text_docx(file):
    text = ""
    try:
        doc = Document(file)
        for p in doc.paragraphs:
            text += p.text + "\n"
    except Exception as e:
        print(f"DOCX Error: {e}")
    return text
