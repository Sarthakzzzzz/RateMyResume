"""Content quality scoring."""
import re


def calculate_quality_score(resume_text: str) -> int:
    """
    Calculate content quality score based on various content metrics.

    Args:
        resume_text: The resume text to analyze

    Returns:
        Quality score (0-8 points)
    """
    word_count = len(resume_text.split())
    quality_score = 0

    # Word count check
    if 200 <= word_count <= 600:
        quality_score += 3

    # Quantifiable achievements check
    if re.search(r'\b\d+%|\$\d+|\d+\s*(users|customers|projects|years)', resume_text):
        quality_score += 3

    # Structure check (multiple sections)
    if len(resume_text.split('\n')) > 15:
        quality_score += 2

    return quality_score
