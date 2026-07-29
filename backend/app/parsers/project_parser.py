PROJECT_KEYWORDS = [
    "project",
    "projects",
    "developed",
    "built",
    "implemented",
]


def extract_projects(text: str):
    projects = []

    for line in text.splitlines():
        line = line.strip()

        if any(keyword in line.lower() for keyword in PROJECT_KEYWORDS):
            projects.append(line)

    return list(dict.fromkeys(projects))