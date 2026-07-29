import re

EDUCATION_KEYWORDS = [
    "b.e",
    "b.tech",
    "bachelor",
    "m.e",
    "m.tech",
    "master",
    "phd",
    "diploma",
    "higher secondary",
    "hsc",
    "sslc",
]


def extract_education(text: str):
    education = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        if any(keyword in line.lower() for keyword in EDUCATION_KEYWORDS):
            education.append(line)

    return list(dict.fromkeys(education))