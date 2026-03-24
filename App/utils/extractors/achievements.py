"""Achievements section extraction from resumes."""
import re


def extract_achievements(resume_text: str) -> dict:
    """
    Extract achievements information from resume text.

    Args:
        resume_text: The resume text to extract from

    Returns:
        Dictionary containing achievements list and count
    """
    achievements = []
    matches = re.findall(
        r'(?:^|\n)[•\-\*]?\s*(Achievements|Awards)\s*:?(.+)?', resume_text, re.IGNORECASE)
    for m in matches:
        if m[1]:
            achievements += [a.strip()
                             for a in re.split(r',|;|\n', m[1]) if len(a.strip()) > 3]

    return {
        "achievements": list(set(achievements)),
        "count": len(achievements)
    }
