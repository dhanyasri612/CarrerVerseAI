from app.parsers.experience_parser import extract_experience


def test_rejects_resume_objective_prose():
    text = """OBJECTIVE
about building practical applications and eager to learn, contribute, and grow as a developer
"""
    assert extract_experience(text) == []


def test_extracts_internship_with_company_and_dates():
    text = """EXPERIENCE
Software Developer Intern
ABC Technologies
June 2025 - August 2025
"""
    assert extract_experience(text) == [
        "Software Developer Intern — ABC Technologies | June 2025 - August 2025"
    ]


def test_extracts_employment_with_company():
    text = """WORK EXPERIENCE
Backend Developer
XYZ Technologies
"""
    assert extract_experience(text) == ["Backend Developer — XYZ Technologies"]


def test_does_not_scan_other_resume_sections():
    text = """PROFILE
Software Developer passionate about building applications
PROJECTS
Backend Developer API project
"""
    assert extract_experience(text) == []
