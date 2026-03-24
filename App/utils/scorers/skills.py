"""Technical skills extraction and scoring."""


def tech_skills_score(resume_text: str) -> dict:
    """
    Score technical skills found in resume text.

    Args:
        resume_text: The resume text to analyze

    Returns:
        Dictionary with score, skills by category, and total count
    """
    text_lower = resume_text.lower()

    # Comprehensive skill categories
    skill_categories = {
        "programming": ["python", "java", "javascript", "c++", "c#", "go", "rust", "swift", "kotlin", "php", "ruby", "scala", "r", "matlab"],
        "web": ["html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "laravel"],
        "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "oracle", "sqlite"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "gitlab", "github actions"],
        "data_science": ["pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "matplotlib", "seaborn", "tableau", "power bi"],
        "tools": ["git", "jira", "confluence", "slack", "trello", "figma", "photoshop", "excel", "powerpoint"]
    }

    found_skills = {}
    total_score = 0

    for category, skills in skill_categories.items():
        found_skills[category] = []
        for skill in skills:
            if skill in text_lower:
                found_skills[category].append(skill)
                total_score += 2 if category in [
                    "programming", "database"] else 1

    # Bonus for skill diversity
    categories_with_skills = sum(
        1 for skills in found_skills.values() if skills)
    if categories_with_skills >= 4:
        total_score += 5

    return {
        "score": min(20, total_score),
        "skills_by_category": found_skills,
        "total_skills_found": sum(len(skills) for skills in found_skills.values())
    }
