import re

def clean_text(text):
    text = text.lower()
    text = text.replace("-", " ")
    text = text.replace("/", " ")
    text = re.sub(r'[^a-z0-9 ]', ' ', text)
    return text
