from app.parsers.certification_parser import extract_certifications


def test_extracts_title_and_issuer_from_dash_line():
    assert extract_certifications("CERTIFICATIONS\nPrompt Engineering — GUVI") == [
        "Prompt Engineering — GUVI"
    ]


def test_joins_title_and_issuer_on_wrapped_lines():
    assert extract_certifications("CERTIFICATIONS\nJava Programming\nNPTEL") == [
        "Java Programming — NPTEL"
    ]


def test_rejects_recipient_and_boilerplate_lines():
    text = """CERTIFICATIONS
Ms. Dhanyasri K
Presented to
National Board
"""
    assert extract_certifications(text) == []


def test_rejects_bare_issuer_and_joins_wrapped_title():
    assert extract_certifications("CERTIFICATIONS\nGoogle Cloud") == []
    assert extract_certifications("CERTIFICATIONS\nGoogle Cloud\nFundamentals") == [
        "Google Cloud Fundamentals"
    ]


def test_extracts_multiple_entries_and_deduplicates():
    text = """CERTIFICATIONS
Prompt Engineering — GUVI
Java Programming — NPTEL
Prompt Engineering — GUVI

EXPERIENCE
AWS
"""
    assert extract_certifications(text) == [
        "Prompt Engineering — GUVI",
        "Java Programming — NPTEL",
    ]


def test_does_not_scan_resume_without_certification_section():
    text = """PROFILE
Google Cloud and AWS projects
EXPERIENCE
Completed a Coursera course
"""
    assert extract_certifications(text) == []
