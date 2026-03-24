"""Leadership roles extraction from resumes."""


def extract_leadership_roles(resume_text: str) -> dict:
    """
    Extract leadership roles information from resume text.

    Args:
        resume_text: The resume text to extract from

    Returns:
        Dictionary containing leadership roles list and count
    """
    leadership_keywords = ["lead", "president", "organizer",
                           "head", "captain", "coordinator", "manager", "director"]
    found = []

    for line in resume_text.split('\n'):
        for word in leadership_keywords:
            if word in line.lower():
                found.append(line.strip())
                break

    return {
        "leadership_roles": list(set(found)),
        "count": len(found)
    }
