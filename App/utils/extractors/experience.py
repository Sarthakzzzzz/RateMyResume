"""Experience section extraction from resumes."""
import re


def extract_experience(resume_text: str) -> dict:
    """
    Extract experience information from resume text.

    Args:
        resume_text: The resume text to extract from

    Returns:
        Dictionary containing experience entries and years estimate
    """
    experience = []
    lines = resume_text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'\bexperience\b', line, re.IGNORECASE):
            for j in range(i + 1, min(i + 10, len(lines))):
                if lines[j].strip() == "":
                    break
                experience.append(lines[j].strip())
            break

    return {
        "experience_entries": experience,
        "years_of_experience_estimate": len(experience) // 2
    }
