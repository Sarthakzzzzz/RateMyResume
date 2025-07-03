import spacy


def extract_entities(text):
    # Load the small English model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities


if __name__ == "__main__":
    sample_text = "Sarthak Pujari is a ML Engineer at Microsoft in Seattle."
    entities = extract_entities(sample_text)
    print("Named Entities:", entities)
