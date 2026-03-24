"""Personal information extraction from resumes."""
import re


def get_personal_info(resume_text: str) -> dict:
    """
    Extract personal information from resume text.

    Args:
        resume_text: The resume text to extract from

    Returns:
        Dictionary with score and personal information details
    """
    # Import here to allow test mocking of rating.nlp
    from .. import rating

    doc = rating.nlp(resume_text)
    personal_info = {
        "name": "",
        "email": "",
        "phone": "",
        "address": "",
        "links": []
    }

    # Enhanced email detection
    emails = re.findall(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text)
    if emails:
        personal_info["email"] = emails[0]

    # Enhanced phone detection
    phones = re.findall(
        r'(?:\+?1[-\s]?)?\(?[0-9]{3}\)?[-\s]?[0-9]{3}[-\s]?[0-9]{4}', resume_text)
    if phones:
        personal_info["phone"] = phones[0]

    # Enhanced links detection
    links = re.findall(
        r'(https?://[^\s]+|linkedin\.com/[^\s]+|github\.com/[^\s]+)', resume_text, re.IGNORECASE)
    personal_info["links"] = links

    # Name extraction
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            personal_info["name"] = ent.text
            break

    if not personal_info["name"]:
        lines = resume_text.split('\n')[:5]
        for line in lines:
            name_match = re.search(
                r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', line.strip())
            if name_match:
                personal_info["name"] = name_match.group(0)
                break

    # Scoring
    score = 0
    if personal_info["name"]:
        score += 3
    if personal_info["email"]:
        score += 3
    if personal_info["phone"]:
        score += 2
    if personal_info["links"]:
        score += 2

    return {"score": score, "info": personal_info}
