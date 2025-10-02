import re
import spacy

# Load spaCy model and grammar tool
nlp = spacy.load("en_core_web_sm")
class _ToolStub:
    def check(self, text):
        return []
tool = _ToolStub()  # Disable grammar checking to avoid rate limits


def normalize_text(text):
    return text.lower().replace('\r', '').strip()


# ----------- 1. Personal Info Extraction -----------

def get_personal_info(resume_text: str) -> dict:
    doc = nlp(resume_text)
    personal_info = {
        "name": "",
        "email": "",
        "phone": "",
        "address": "",
        "links": []
    }

    # Enhanced email detection
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text)
    if emails:
        personal_info["email"] = emails[0]

    # Enhanced phone detection
    phones = re.findall(r'(?:\+?1[-\s]?)?\(?[0-9]{3}\)?[-\s]?[0-9]{3}[-\s]?[0-9]{4}', resume_text)
    if phones:
        personal_info["phone"] = phones[0]

    # Enhanced links detection
    links = re.findall(r'(https?://[^\s]+|linkedin\.com/[^\s]+|github\.com/[^\s]+)', resume_text, re.IGNORECASE)
    personal_info["links"] = links

    # Name extraction
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            personal_info["name"] = ent.text
            break

    if not personal_info["name"]:
        lines = resume_text.split('\n')[:5]
        for line in lines:
            name_match = re.search(r'^([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', line.strip())
            if name_match:
                personal_info["name"] = name_match.group(0)
                break

    # Scoring
    score = 0
    if personal_info["name"]: score += 3
    if personal_info["email"]: score += 3
    if personal_info["phone"]: score += 2
    if personal_info["links"]: score += 2
    
    return {"score": score, "info": personal_info}


# ----------- 2. Grammar + Length Scoring -----------

def get_resume_score(resume_text: str) -> int:
    score = 0
    score += get_personal_info(resume_text)

    grammar_issues = tool.check(resume_text)
    score -= len(grammar_issues)

    lines = resume_text.split('\n')
    if len(lines) < 10:
        score -= 5
    elif len(lines) > 30:
        score += 5

    return score


# ----------- 3. Resume Section Extraction -----------

def extract_sections(resume_text: str) -> dict:
    section_pattern = r"(?:^|\n)[•\-\*]?\s*([A-Za-z ]+)\s*:\s*([^\n]+)"
    matches = re.findall(section_pattern, resume_text)
    sections = {}

    for section, items in matches:
        section_key = section.strip().lower().replace(" ", "_")
        item_list = [item.strip() for item in items.split(",") if item.strip()]
        sections.setdefault(section_key, []).extend(item_list)

    return sections


# ----------- 4. Tech Skills Scoring -----------

def tech_skills_score(resume_text: str) -> dict:
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
                total_score += 2 if category in ["programming", "database"] else 1
    
    # Bonus for skill diversity
    categories_with_skills = sum(1 for skills in found_skills.values() if skills)
    if categories_with_skills >= 4:
        total_score += 5
    
    return {
        "score": min(20, total_score),
        "skills_by_category": found_skills,
        "total_skills_found": sum(len(skills) for skills in found_skills.values())
    }


# ----------- 5. Education Section Extraction -----------

def extract_education_section(resume_text: str) -> dict:
    education_pattern = r"(?:^|\n)[•\-\*]?\s*Education\s*:\s*([^\n]+)"
    matches = re.findall(education_pattern, resume_text, re.IGNORECASE)

    education_entries = []
    for match in matches:
        education_entries += [item.strip()
                              for item in re.split(r",|;", match) if item.strip()]

    doc = nlp(resume_text)
    degrees, universities, years = [], [], []

    degree_keywords = [
        "bachelor", "master", "phd", "b.sc", "m.sc", "b.tech", "m.tech",
        "mba", "bachelors", "masters", "doctor", "ba", "ma", "bs", "ms"
    ]

    for ent in doc.ents:
        if ent.label_ == "ORG":
            universities.append(ent.text)
        if ent.label_ == "DATE" or re.search(r"\b(19|20)\d{2}\b", ent.text):
            years.append(ent.text)
        if any(deg in ent.text.lower() for deg in degree_keywords):
            degrees.append(ent.text)

    return {
        "education_entries": list(set(education_entries)),
        "degrees": list(set(degrees)),
        "universities": list(set(universities)),
        "years": list(set(years))
    }


# --------- Extract Experience Section ---------

def extract_experience(resume_text: str) -> dict:
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


# --------- Extract Projects Section ---------

def extract_projects(resume_text: str) -> dict:
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


# --------- Extract Achievements ---------

def extract_achievements(resume_text: str) -> dict:
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


# --------- Extract Certifications ---------

def extract_certifications(resume_text: str) -> dict:
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


# --------- Extract Leadership Roles ---------

def extract_leadership_roles(resume_text: str) -> dict:
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


# --------- Red Flags Detection ---------

def detect_red_flags(resume_text: str) -> list:
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
    grammar_issues = tool.check(resume_text[:500])  # Check first 500 chars for performance
    if len(grammar_issues) > 3:
        red_flags.append(f"Multiple grammar issues detected ({len(grammar_issues)})")
    
    # Formatting issues
    if resume_text.count('\n\n') < 2:
        red_flags.append("Poor formatting - lacks proper spacing")
    
    return red_flags

# ---------- Calculate Resume Score --------


def calculate_resume_score(resume_text: str) -> dict:
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
    details["tech_sections"] = tech.get("skills_by_category", {})  # Only the dict, not the full object
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
    details["education_info"] = edu  # Ensure key is always present for test compatibility
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
    word_count = len(resume_text.split())
    quality_score = 0
    if 200 <= word_count <= 600: quality_score += 3
    if re.search(r'\b\d+%|\$\d+|\d+\s*(users|customers|projects|years)', resume_text): quality_score += 3
    if len(resume_text.split('\n')) > 15: quality_score += 2
    details["content_quality_score"] = quality_score
    final_score += quality_score

    # 10. Red Flags (penalties)
    red_flags = detect_red_flags(resume_text)
    red_flag_penalty = len(red_flags) * 2
    details["red_flags"] = red_flags
    details["red_flag_penalty"] = red_flag_penalty
    final_score -= red_flag_penalty

    # Grammar issues (for test compatibility)
    grammar_issues = tool.check(resume_text)
    details["grammar_issues"] = len(grammar_issues)

    # Final calculations
    max_score = 90  # 10+15+20+10+8+8+6+5+8 = 90
    details["final_score"] = max(0, min(max_score, final_score))
    details["max_possible_score"] = max_score
    details["percentage"] = (details["final_score"] / max_score) * 100

    return details
