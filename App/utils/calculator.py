"""Main resume scoring calculator - Orchestrates all scoring logic."""

from .extractors import (
    get_personal_info,
    extract_experience,
    extract_projects,
    extract_education_section,
    extract_achievements,
    extract_certifications,
    extract_leadership_roles,
)
from .scorers import (
    tech_skills_score,
    calculate_quality_score,
)
from .validators import detect_red_flags
from . import common


def calculate_resume_score(resume_text: str) -> dict:
    """
    Calculate comprehensive resume score combining all metrics.

    Args:
        resume_text: The resume text to analyze

    Returns:
        Dictionary with detailed score breakdown and final score (0-100)
    """
    final_score = 0
    details = {}

    # 1. Personal Info (0-10 points)
    personal_result = get_personal_info(resume_text)
    personal_score = personal_result["score"]
    details["personal_info_score"] = personal_score
    details["personal_info"] = personal_result["info"]
    final_score += personal_score

    # 2. Experience (0-15 points)
    exp = extract_experience(resume_text)
    exp_score = min(15, len(exp["experience_entries"]) * 2)
    details["experience_score"] = exp_score
    details["experience_entries"] = exp["experience_entries"]
    final_score += exp_score

    # 3. Technical Skills (0-20 points)
    tech = tech_skills_score(resume_text)
    tech_score = tech["score"]
    details["tech_skills_score"] = tech_score
    details["tech_skills"] = tech
    details["tech_sections"] = tech.get("skills_by_category", {})
    final_score += tech_score

    # 4. Projects (0-10 points)
    proj = extract_projects(resume_text)
    proj_score = min(10, proj["project_count"] * 3)
    details["project_score"] = proj_score
    details["projects"] = proj["projects"]
    final_score += proj_score

    # 5. Education (0-8 points)
    edu = extract_education_section(resume_text)
    edu_score = min(8, len(edu["degrees"]) * 4 + len(edu["universities"]) * 2)
    details["education_score"] = edu_score
    details["education"] = edu
    details["education_info"] = edu  # For test compatibility
    final_score += edu_score

    # 6. Achievements (0-8 points)
    ach = extract_achievements(resume_text)
    ach_score = min(8, ach["count"] * 2)
    details["achievements_score"] = ach_score
    details["achievements"] = ach["achievements"]
    final_score += ach_score

    # 7. Certifications (0-6 points)
    cert = extract_certifications(resume_text)
    cert_score = min(6, cert["count"] * 2)
    details["certifications_score"] = cert_score
    details["certifications"] = cert["certifications"]
    final_score += cert_score

    # 8. Leadership (0-5 points)
    lead = extract_leadership_roles(resume_text)
    lead_score = min(5, lead["count"] * 2)
    details["leadership_score"] = lead_score
    details["leadership_roles"] = lead["leadership_roles"]
    final_score += lead_score

    # 9. Content Quality (0-8 points)
    quality_score = calculate_quality_score(resume_text)
    details["content_quality_score"] = quality_score
    final_score += quality_score

    # 10. Red Flags (penalties)
    red_flags = detect_red_flags(resume_text)
    red_flag_penalty = len(red_flags) * 2
    details["red_flags"] = red_flags
    details["red_flag_penalty"] = red_flag_penalty
    final_score -= red_flag_penalty

    # Grammar issues (for test compatibility)
    # Import here to get the mocked tool if available
    from . import rating
    grammar_issues = rating.tool.check(resume_text)
    details["grammar_issues"] = len(grammar_issues)

    # Final calculations
    max_score = 90  # 10+15+20+10+8+8+6+5+8 = 90
    details["final_score"] = max(0, min(max_score, final_score))
    details["max_possible_score"] = max_score
    details["percentage"] = (details["final_score"] / max_score) * 100

    return details
