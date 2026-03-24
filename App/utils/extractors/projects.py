"""Projects section extraction from resumes."""
import re


def extract_projects(resume_text: str) -> dict:
    """
    Extract projects information from resume text.

    Args:
        resume_text: The resume text to extract from

    Returns:
        Dictionary containing projects list and count
    """
    matches = re.findall(
        r'(?:^|\n)[•\-\*]?\s*(Projects|Project Experience)\s*:?(.+)?', resume_text, re.IGNORECASE)
    projects = []
    for match in matches:
        text = match[1]
        if text:
            items = re.split(r',|;|\n', text)
            projects.extend([p.strip() for p in items if len(p.strip()) > 3])

    return {
        "projects": list(set(projects)),
        "project_count": len(projects)
    }
