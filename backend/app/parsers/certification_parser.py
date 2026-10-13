"""Conservative certification extraction for resume text."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional

from app.parsers.certificate_extractor import ISSUER_SIGNATURES, is_invalid_or_generic_title

CERTIFICATION_SECTION_HEADINGS = {
    "certification", "certifications", "certificate", "certificates",
    "professional certification", "professional certifications",
    "courses & certifications", "course & certifications",
    "certifications & courses", "certificates & courses",
}

RESUME_SECTION_HEADINGS = {
    "summary", "profile", "objective", "skills", "technical skills",
    "education", "experience", "work experience", "professional experience",
    "employment", "projects", "project experience", "achievements", "awards",
    "publications", "languages", "interests", "references", "activities", "volunteering",
}

BOILERPLATE_PATTERNS = (
    r"presented\s+to", r"this\s+is\s+to\s+(?:proudly\s+)?certif",
    r"has\s+successfully\s+completed", r"successfully\s+completed",
    r"certificate\s+of\s+(?:completion|achievement|participation|training)",
    r"awarded\s+to", r"authorized\s+(?:signatory|signature)",
    r"national\s+board(?:\s+of\s+\w+)*",
    r"(?:date|issued|issue\s+date|date\s+of\s+issue)\s*[:\-]",
    r"credential\s+(?:id|url)", r"verification\s+(?:id|url|code)", r"signature",
)

ORGANIZATION_WORDS = (
    "institute", "institution", "university", "college", "academy", "school",
    "department", "ministry", "government", "board of", "organization",
)

TITLE_HINTS = (
    "certified", "certification", "programming", "fundamentals", "specialization",
    "professional", "associate", "administrator", "developer", "engineer", "architect",
    "security", "cloud", "analytics", "course", "training", "bootcamp", "communication",
    "writing", "engineering", "language",
)


def _clean_line(line: str) -> str:
    line = unicodedata.normalize("NFKC", line)
    line = line.replace("\u2013", "—").replace("\u2014", "—")
    line = re.sub(r"^[\s•●▪◦‣\-*]+", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip(" \t:;|")


def _heading_key(line: str) -> str:
    return re.sub(r"[^a-z& ]", "", _clean_line(line).lower()).strip()


def _is_all_caps_heading(line: str) -> bool:
    clean = _clean_line(line)
    letters = re.sub(r"[^A-Za-z]", "", clean)
    return len(letters) >= 4 and clean == clean.upper() and len(clean.split()) <= 7


def _is_certification_heading(line: str) -> bool:
    return _heading_key(line) in CERTIFICATION_SECTION_HEADINGS


def _is_section_heading(line: str) -> bool:
    key = _heading_key(line)
    return key in RESUME_SECTION_HEADINGS or _is_all_caps_heading(line)


def _extract_certification_sections(text: str) -> list[str]:
    lines = text.splitlines()
    section_lines: list[str] = []
    in_section = False
    for raw_line in lines:
        line = _clean_line(raw_line)
        if not line:
            if in_section:
                section_lines.append("")
            continue
        if _is_certification_heading(line):
            in_section = True
            continue
        if in_section and _is_section_heading(line) and not _is_issuer_only(line):
            in_section = False
        if in_section:
            section_lines.append(line)
    return section_lines


def _issuer_name(value: str) -> Optional[str]:
    clean = _clean_line(value)
    if not clean:
        return None
    for issuer, patterns in ISSUER_SIGNATURES.items():
        if any(re.fullmatch(pattern, clean, re.IGNORECASE) for pattern in patterns):
            return issuer
    return None


def _contains_issuer(value: str) -> Optional[tuple[str, str]]:
    clean = _clean_line(value)
    for separator in ("—", "|", "–"):
        if separator in clean:
            left, right = [part.strip() for part in clean.split(separator, 1)]
            issuer = _issuer_name(right)
            if issuer:
                return left, issuer
    match = re.match(r"^(.+?)\s+-\s+(.+)$", clean)
    if match:
        issuer = _issuer_name(match.group(2))
        if issuer:
            return match.group(1).strip(), issuer
    lowered = clean.lower()
    for issuer, patterns in ISSUER_SIGNATURES.items():
        for pattern in patterns:
            found = re.search(pattern, lowered, re.IGNORECASE)
            if found:
                before = clean[:found.start()].strip(" —–-|:,;")
                after = clean[found.end():].strip(" —–-|:,;")
                if before and not after and len(before) >= 3:
                    return before, issuer
    return None


def _is_boilerplate(value: str) -> bool:
    lowered = value.lower().strip()
    if not lowered:
        return True
    return any(re.search(pattern, lowered, re.IGNORECASE) for pattern in BOILERPLATE_PATTERNS)


def _is_issuer_only(value: str) -> bool:
    return _issuer_name(value) is not None


def _looks_like_title(value: str) -> bool:
    clean = _clean_line(value)
    lowered = clean.lower()
    if len(clean) < 4 or _is_boilerplate(clean) or _is_issuer_only(clean):
        return False
    if is_invalid_or_generic_title(clean) or any(word in lowered for word in ORGANIZATION_WORDS):
        return False
    if re.fullmatch(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+", clean) and not any(hint in lowered for hint in TITLE_HINTS):
        # Reject plain personal names without skill hints
        return False
    if re.fullmatch(r"[A-Z]{1,5}\.?\s*[A-Z]{1,5}\.?", clean):
        return False
    words = re.findall(r"[A-Za-z0-9+#.]+", clean)
    return len(words) >= 2 or any(hint in lowered for hint in TITLE_HINTS)


def _looks_like_wrapped_prefix(value: str) -> bool:
    return _clean_line(value).lower() in {
        "google cloud", "aws", "amazon web services", "microsoft azure",
        "deep learning", "machine learning",
    }


def _candidate_lines(lines: Iterable[str]) -> list[str]:
    clean_lines = [line for line in lines if line]
    candidates: list[str] = []
    index = 0
    while index < len(clean_lines):
        current = clean_lines[index]
        next_line = clean_lines[index + 1] if index + 1 < len(clean_lines) else None
        if _is_boilerplate(current):
            index += 1
            continue
        if next_line and _is_issuer_only(next_line) and _looks_like_title(current):
            candidates.append(f"{current} — {next_line}")
            index += 2
            continue
        if next_line and _looks_like_wrapped_prefix(current) and not _is_boilerplate(next_line):
            candidates.append(f"{current} {next_line}")
            index += 2
            continue
        candidates.append(current)
        index += 1
    return candidates


def _normalize_title(value: str) -> str:
    title = _clean_line(value)
    title = re.sub(r"^(?:certificate|certification)\s+(?:in|on|for)\s+", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+(?:certificate|certification|course completion)$", "", title, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", title).strip(" .,:;—–-|")


def _parse_candidate(candidate: str) -> Optional[str]:
    parsed = _contains_issuer(candidate)
    title, issuer = parsed if parsed else (candidate, None)
    title = _normalize_title(title)
    if not _looks_like_title(title):
        return None
    return f"{title} — {issuer}" if issuer else title


def _semantic_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def extract_certifications(text: str) -> list[str]:
    """Extract high-precision certification entries from resume sections."""
    sections = _extract_certification_sections(text or "")
    if not sections:
        return []
    extracted: list[str] = []
    seen: set[str] = set()
    for candidate in _candidate_lines(sections):
        parsed = _parse_candidate(candidate)
        if not parsed:
            continue
        key = _semantic_key(parsed)
        if key not in seen:
            seen.add(key)
            extracted.append(parsed)
    return extracted
