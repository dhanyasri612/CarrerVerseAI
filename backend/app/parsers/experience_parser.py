EXPERIENCE_KEYWORDS = [
    "experience",
    "intern",
    "internship",
    "software engineer",
    "developer",
    "research",
]


def extract_experience(text: str):
    experience = []

    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        if any(keyword in line.lower() for keyword in EXPERIENCE_KEYWORDS):
            experience.append(line)

    return list(dict.fromkeys(experience))