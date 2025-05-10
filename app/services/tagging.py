import spacy
nlp = spacy.load("en_core_web_sm")

def auto_tag(text: str):
    doc = nlp(text)
    return list(set(ent.label_ for ent in doc.ents))