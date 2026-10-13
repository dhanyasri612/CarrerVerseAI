try:
    import fitz
except ImportError:
    fitz = None

from app.schemas.parsed_resume import ParsedResume

from app.parsers.contact_parser import (
    extract_name,
    extract_email,
    extract_phone,
)

from app.parsers.skill_parser import extract_skills

from app.parsers.education_parser import extract_education
from app.parsers.experience_parser import extract_experience
from app.parsers.project_parser import extract_projects
from app.parsers.certification_parser import extract_certifications


# Bump whenever deterministic resume extraction semantics change. A cached
# file must be parsed again after a parser upgrade.
RESUME_PARSER_VERSION = "2026-10-03-data-quality-v3"


def extract_text_from_pdf(pdf_path: str) -> str:
    if fitz is not None:
        document = fitz.open(pdf_path)
        text = ""
        for page in document:
            text += page.get_text()
        document.close()
        return text
    try:
        with open(pdf_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""


def parse_resume(pdf_path: str):
    text = extract_text_from_pdf(pdf_path)

    return ParsedResume(
        name=extract_name(text),
        email=extract_email(text),
        phone=extract_phone(text),
        skills=extract_skills(text),
        education=extract_education(text),
        experience=extract_experience(text),
        projects=extract_projects(text),
        certifications=extract_certifications(text),
    )
