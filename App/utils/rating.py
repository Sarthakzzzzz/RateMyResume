import re
import spacy
import language_tool_python

# Load spaCy model and grammar tool
nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageToolPublicAPI('en-US')


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
        "links": ""
    }

    email = re.search(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text)
    phone = re.search(r'\+?\d[\d\s\-]{8,}\d', resume_text)
    address = re.search(r'\d{1,5}\s\w+\s\w+,\s\w+,\s\w+\s\d{5}', resume_text)
    link = re.search(r'(https?://[^\s]+)', resume_text)

    if email:
        personal_info["email"] = email.group(0)
    if phone:
        personal_info["phone"] = phone.group(0)
    if address:
        personal_info["address"] = address.group(0)
    if link:
        personal_info["links"] = link.group(0)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            personal_info["name"] = ent.text
            break

    if not personal_info["name"]:
        name_guess = re.search(r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)', resume_text)
        if name_guess:
            personal_info["name"] = name_guess.group(0)

    score = 10 if all(personal_info.values()) else -10
    return score


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
    sections = extract_sections(resume_text)
    doc = nlp(resume_text)

    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    if orgs:
        sections.setdefault("organizations", []).extend(orgs)

    score = sum(len(items) for items in sections.values()) * 2
    sections["score"] = score
    return sections


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

    if len(resume_text.split()) < 100:
        red_flags.append("Resume is too short.")
    if not re.search(r'\b(managed|developed|built|led|created|analyzed|designed|initiated|collaborated|implemented)\b', text):
        red_flags.append("Lacks strong action verbs.")
    if not re.search(r'\b(python|java|sql|git|aws|docker|react|tensorflow|linux)\b', text):
        red_flags.append("Missing common tech stack mentions.")
    if not re.search(r'\b(experience|project|certification|education|internship)\b', text):
        red_flags.append("Missing major resume sections.")

    return red_flags

# ---------- Calculate Resume Score --------


def calculate_resume_score(resume_text: str) -> dict:
    final_score = 0
    details = {}

    # 1. Personal Info
    personal_score = get_personal_info(resume_text)
    details["personal_info_score"] = personal_score
    final_score += personal_score

    # 2. Grammar Score
    grammar_issues = tool.check(resume_text)
    grammar_penalty = len(grammar_issues)
    details["grammar_issues"] = grammar_penalty
    final_score -= grammar_penalty

    # 3. Length Bonus
    lines = resume_text.split("\n")
    if len(lines) > 30:
        final_score += 5
        details["length_bonus"] = 5
    elif len(lines) < 10:
        final_score -= 5
        details["length_penalty"] = -5

    # 4. Experience
    exp = extract_experience(resume_text)
    exp_score = min(10, exp["years_of_experience_estimate"] * 2)
    final_score += exp_score
    details["experience_score"] = exp_score
    details["experience_entries"] = exp["experience_entries"]

    # 5. Projects
    proj = extract_projects(resume_text)
    proj_score = min(10, proj["project_count"] * 2)
    final_score += proj_score
    details["projects_score"] = proj_score
    details["projects"] = proj["projects"]

    # 6. Achievements
    ach = extract_achievements(resume_text)
    ach_score = min(5, ach["count"] * 1)
    final_score += ach_score
    details["achievements_score"] = ach_score
    details["achievements"] = ach["achievements"]

    # 7. Certifications
    cert = extract_certifications(resume_text)
    cert_score = min(5, cert["count"] * 1)
    final_score += cert_score
    details["certifications_score"] = cert_score
    details["certifications"] = cert["certifications"]

    # 8. Leadership
    leader = extract_leadership_roles(resume_text)
    leader_score = min(5, leader["count"] * 2)
    final_score += leader_score
    details["leadership_score"] = leader_score
    details["leadership_roles"] = leader["leadership_roles"]

    # 9. Education
    edu = extract_education_section(resume_text)
    edu_score = 5 if edu["degrees"] else 0
    final_score += edu_score
    details["education_score"] = edu_score
    details["education_info"] = edu

    # 10. Technical Skills
    tech = tech_skills_score(resume_text)
    tech_score = min(10, tech["score"])
    final_score += tech_score
    details["tech_skills_score"] = tech_score
    details["tech_sections"] = {k: v for k, v in tech.items() if k != "score"}

    # 11. Red Flags
    red_flags = detect_red_flags(resume_text)
    red_flag_penalty = len(red_flags) * 3
    final_score -= red_flag_penalty
    details["red_flags"] = red_flags
    details["red_flag_penalty"] = -red_flag_penalty

    # 12. Extra / Unknown Content Penalty
    known_sections = ["experience", "projects", "achievements", "certifications",
                      "education", "skills", "personal", "summary", "leadership"]
    extra_sections = []
    for line in resume_text.lower().split('\n'):
        if ":" in line:
            section_name = line.split(":")[0].strip()
            if section_name not in known_sections and len(section_name) < 25:
                extra_sections.append(section_name)
    extra_penalty = len(set(extra_sections))
    final_score -= extra_penalty
    details["extra_sections_penalty"] = -extra_penalty
    details["unrecognized_sections"] = list(set(extra_sections))

    # 13. Bonus: Balanced Sections
    section_diversity = len([
        s for s in [
            exp["experience_entries"],
            proj["projects"],
            ach["achievements"],
            cert["certifications"],
            edu["education_entries"]
        ] if s
    ])
    if section_diversity >= 4:
        final_score += 5
        details["balance_bonus"] = 5

    # 14. Final Score Normalization
    final_score = max(0, min(100, final_score))
    details["final_score"] = final_score
    return details
