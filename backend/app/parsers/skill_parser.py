from app.utils.skills import SKILLS


def extract_skills(text: str):
    skills = []

    lower_text = text.lower()

    for skill in SKILLS:
        if skill.lower() in lower_text:
            skills.append(skill)

    return sorted(set(skills))