"""High-precision work-experience extraction from resume text."""

from __future__ import annotations

import re
import unicodedata

EXPERIENCE_HEADINGS = {
    "experience", "work experience", "professional experience", "employment",
    "employment history", "internship", "internships", "freelance experience",
}

OTHER_SECTION_HEADINGS = {
    "summary", "profile", "objective", "skills", "technical skills", "education",
    "projects", "project experience", "certifications", "certificates", "achievements",
    "awards", "publications", "languages", "interests", "references", "activities",
}

ROLE_HINTS = (
    "developer", "engineer", "intern", "internship", "analyst", "designer", "manager",
    "consultant", "researcher", "architect", "administrator", "lead", "specialist",
    "associate", "scientist", "tester", "technician", "director", "coordinator",
)

DATE_PATTERN = re.compile(
    r"(?:\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\b\s+\d{4}|\b\d{4}\b)"
    r"(?:\s*(?:-|–|—|to)\s*(?:present|current|now|"
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
    r"dec(?:ember)?)\b\s*\d{4}|\d{4}))?",
    re.IGNORECASE,
)

PROSE_MARKERS = (
    "about ", "passionate about", "eager to ", "looking to ", "seeking ",
    "objective", "career goal", "responsible for", "interested in ",
    "building practical", "contribute and grow", "grow as a developer",
)


def _clean(line: str) -> str:
    value = unicodedata.normalize("NFKC", line)
    value = re.sub(r"^[\s•●▪◦‣\-*]+", "", value)
    return re.sub(r"\s+", " ", value).strip(" \t:;|")


def _key(line: str) -> str:
    return re.sub(r"[^a-z ]", "", _clean(line).lower()).strip()


def _is_all_caps_heading(line: str) -> bool:
    clean = _clean(line)
    letters = re.sub(r"[^A-Za-z]", "", clean)
    return len(letters) >= 4 and clean == clean.upper() and len(clean.split()) <= 6


def _is_experience_heading(line: str) -> bool:
    return _key(line) in EXPERIENCE_HEADINGS


def _is_section_heading(line: str) -> bool:
    return _key(line) in OTHER_SECTION_HEADINGS or _is_all_caps_heading(line)


def _is_date(line: str) -> bool:
    clean = _clean(line)
    if not clean or len(clean) > 55:
        return False
    return bool(DATE_PATTERN.fullmatch(clean) or re.fullmatch(r"(?:\d{1,2}[/-])?\d{4}\s*(?:-|–|—|to)\s*(?:present|current|now|(?:\d{1,2}[/-])?\d{4})", clean, re.IGNORECASE))


def _looks_like_role(line: str) -> bool:
    lowered = _clean(line).lower()
    if not lowered or len(lowered) > 90 or any(marker in lowered for marker in PROSE_MARKERS):
        return False
    if any(char in line for char in ".!?;"):
        return False
    return any(re.search(rf"\b{re.escape(hint)}\b", lowered) for hint in ROLE_HINTS)


def _looks_like_company(line: str) -> bool:
    clean = _clean(line)
    lowered = clean.lower()
    if not clean or len(clean) > 90 or _is_date(clean) or _looks_like_role(clean):
        return False
    if any(marker in lowered for marker in PROSE_MARKERS) or any(char in clean for char in ".!?;"):
        return False
    words = re.findall(r"[A-Za-z0-9&'.-]+", clean)
    company_markers = ("inc", "ltd", "llc", "corp", "technologies", "technology", "solutions", "systems", "labs", "company")
    return len(words) >= 2 or any(marker in lowered for marker in company_markers)


def _section_lines(text: str) -> list[str]:
    result: list[str] = []
    active = False
    for raw in text.splitlines():
        line = _clean(raw)
        if not line:
            if active:
                result.append("")
            continue
        if _is_experience_heading(line):
            active = True
            continue
        if active and _is_section_heading(line):
            active = False
        if active:
            result.append(line)
    return result


def _format_entry(role: str, company: str, dates: str | None) -> str:
    value = f"{role} — {company}"
    return f"{value} | {dates}" if dates else value


def extract_experience(text: str) -> list[str]:
    """Return only structured role/company entries from an experience section."""
    lines = [line for line in _section_lines(text or "") if line]
    extracted: list[str] = []
    seen: set[str] = set()

    index = 0
    while index < len(lines):
        role = lines[index]
        if not _looks_like_role(role):
            index += 1
            continue

        next_one = lines[index + 1] if index + 1 < len(lines) else None
        next_two = lines[index + 2] if index + 2 < len(lines) else None
        company = None
        dates = None

        if next_one and _looks_like_company(next_one):
            company = next_one
            if next_two and _is_date(next_two):
                dates = next_two
        elif next_one and _is_date(next_one) and next_two and _looks_like_company(next_two):
            company, dates = next_two, next_one

        # A role alone is not enough: require a company or explicit employment
        # dates to avoid turning summary prose into work history.
        if company or dates:
            value = _format_entry(role, company or "", dates)
            key = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
            if key not in seen:
                seen.add(key)
                extracted.append(value)
            index += 3 if company and next_two and _is_date(next_two) else 2
        else:
            index += 1

    return extracted
