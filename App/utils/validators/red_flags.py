"""Resume validation - Detect red flags."""
import re
from ..common import normalize_text


def detect_red_flags(resume_text: str) -> list:
    """
    Detect red flags and issues in resume text.

    Args:
        resume_text: The resume text to analyze

    Returns:
        List of red flag messages
    """
    # Import here to allow test mocking of rating.tool
    from .. import rating

    red_flags = []
    text = normalize_text(resume_text)
    word_count = len(resume_text.split())

    # Length issues
    if word_count < 150:
        red_flags.append("Resume too short (< 150 words)")
    elif word_count > 800:
        red_flags.append("Resume too long (> 800 words)")

    # Action verbs
    action_verbs = ["managed", "developed", "built", "led", "created", "analyzed", "designed",
                    "initiated", "collaborated", "implemented", "achieved", "improved", "optimized"]
    if not any(verb in text for verb in action_verbs):
        red_flags.append("Lacks strong action verbs")

    # Quantifiable achievements
    if not re.search(r'\b\d+%|\$\d+|\d+\s*(users|customers|projects|years)', text):
        red_flags.append("Missing quantified achievements")

    # Contact information
    if not re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text):
        red_flags.append("Missing email address")

    # Grammar issues (basic)
    # Check first 500 chars for performance
    grammar_issues = rating.tool.check(resume_text[:500])
    if len(grammar_issues) > 3:
        red_flags.append(
            f"Multiple grammar issues detected ({len(grammar_issues)})")

    # Formatting issues
    if resume_text.count('\n\n') < 2:
        red_flags.append("Poor formatting - lacks proper spacing")

    return red_flags
