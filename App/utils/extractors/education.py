"""Education section extraction from resumes."""
import re


def extract_education_section(resume_text: str) -> dict:
    """
    Extract education information from resume text.

    Args:
        resume_text: The resume text to extract from

    Returns:
        Dictionary containing degrees, universities, years, and entries
    """
    # Import here to allow test mocking of rating.nlp
    from .. import rating

    education_pattern = r"(?:^|\n)[•\-\*]?\s*Education\s*:\s*([^\n]+)"
    matches = re.findall(education_pattern, resume_text, re.IGNORECASE)

    education_entries = []
    for match in matches:
        education_entries += [item.strip()
                              for item in re.split(r",|;", match) if item.strip()]

    doc = rating.nlp(resume_text)
    degrees, universities, years = [], [], []

    degree_keywords = [
        "bachelor", "master", "phd", "b.sc", "m.sc", "b.tech", "m.tech",
        "mba", "bachelors", "masters", "doctor", "ba", "ma", "bs", "ms"
    ]

    for ent in doc.ents:
        if ent.label_ == "ORG":
            universities.append(ent.text)
        if ent.label_ == "DATE" or re.search(r"\b(19|20)\d{2}\b", ent.text):
            years.append(ent.text)
        if any(deg in ent.text.lower() for deg in degree_keywords):
            degrees.append(ent.text)

    return {
        "education_entries": list(set(education_entries)),
        "degrees": list(set(degrees)),
        "universities": list(set(universities)),
        "years": list(set(years))
    }
