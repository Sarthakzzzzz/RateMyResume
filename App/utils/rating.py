import spacy
nlp = spacy.load("en_core_web_sm")
KEYWORDS = ["RESUME", "EXPERIENCE", "EDUCATION", "SKILLS",
            "CERTIFICATIONS", "PROJECTS", "ACHIEVEMENTS", "LANGUAGES"]


def rate_resume(text):
    doc = nlp(text)
    score = 0
    found_keywords = []
    for token in doc:
        if token.text.upper() in KEYWORDS:
            score += 10
            found_keywords.append(token.text.upper())
    score = min(score, 100)  # Cap the score at 100
    found_keywords = list(set(found_keywords))  # Unique keywords
    return {
        "score": score,
        "found_keywords": found_keywords
    }
