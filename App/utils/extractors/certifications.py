"""Certifications section extraction from resumes."""
import re


def extract_certifications(resume_text: str) -> dict:
    """
    Extract certifications information from resume text.

    Args:
        resume_text: The resume text to extract from

    Returns:
        Dictionary containing certifications list and count
    """
    certs = []
    matches = re.findall(
        r'(?:^|\n)[•\-\*]?\s*(Certifications|Courses)\s*:?(.+)?', resume_text, re.IGNORECASE)
    for m in matches:
        if m[1]:
            certs += [c.strip()
                      for c in re.split(r',|;|\n', m[1]) if len(c.strip()) > 3]

    return {
        "certifications": list(set(certs)),
        "count": len(certs)
    }
