import re


def extract_name(text: str):
    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if "@" in line:
            continue

        if any(char.isdigit() for char in line):
            continue

        if len(line.split()) > 5:
            continue

        return line.title()

    return None


def extract_email(text: str):
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    match = re.search(pattern, text)

    return match.group() if match else None


def extract_phone(text: str):
    pattern = r"\+?\d[\d\s()-]{8,}\d"

    match = re.search(pattern, text)

    return match.group().strip() if match else None