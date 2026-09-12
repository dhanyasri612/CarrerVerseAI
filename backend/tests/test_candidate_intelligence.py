import os
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.candidate_profile import CandidateProfile
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.github_profile import GitHubProfile
from app.models.github_repository import GitHubRepository
from app.models.linkedin_profile import LinkedInProfile
from app.models.leetcode_profile import LeetCodeProfile
from app.models.hackerrank_profile import HackerRankProfile
from app.models.certification import Certification
from app.utils.security import hash_password
from app.utils.jwt import create_access_token
from app.parsers.skill_normalizer import normalize_skill, deduplicate_and_group_skills

client = TestClient(app)


def setup_test_environment():
    db: Session = SessionLocal()
    # 1. Ensure CANDIDATE role exists
    role = db.query(Role).filter(Role.name == "CANDIDATE").first()
    if not role:
        role = Role(name="CANDIDATE")
        db.add(role)
        db.commit()
        db.refresh(role)

    # 2. User 1: Complete data user
    user1 = db.query(User).filter(User.email == "intel_user1@careerverse.ai").first()
    if not user1:
        user1 = User(
            name="Alice Intelligence",
            email="intel_user1@careerverse.ai",
            phone="+1-555-0100",
            college="Stanford University",
            degree="B.S. Computer Science",
            graduation_year=2024,
            location="San Francisco, CA",
            bio="Passionate Full Stack & AI Engineer",
            hashed_password=hash_password("Pass123!"),
            role_id=role.id,
            is_active=True
        )
        db.add(user1)
        db.commit()
        db.refresh(user1)

    # 3. User 2: User with Resume only
    user2 = db.query(User).filter(User.email == "intel_user2@careerverse.ai").first()
    if not user2:
        user2 = User(
            name="Bob ResumeOnly",
            email="intel_user2@careerverse.ai",
            hashed_password=hash_password("Pass123!"),
            role_id=role.id,
            is_active=True
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

    # 4. User 3: Zero state user (no integrations or extra data)
    user3 = db.query(User).filter(User.email == "intel_user3@careerverse.ai").first()
    if not user3:
        user3 = User(
            name="Charlie Empty",
            email="intel_user3@careerverse.ai",
            hashed_password=hash_password("Pass123!"),
            role_id=role.id,
            is_active=True
        )
        db.add(user3)
        db.commit()
        db.refresh(user3)

    # 5. User 4: User with partial integrations (missing GitHub, LinkedIn, etc.)
    user4 = db.query(User).filter(User.email == "intel_user4@careerverse.ai").first()
    if not user4:
        user4 = User(
            name="Diana Partial",
            email="intel_user4@careerverse.ai",
            hashed_password=hash_password("Pass123!"),
            role_id=role.id,
            is_active=True
        )
        db.add(user4)
        db.commit()
        db.refresh(user4)

    # Clean old records for test repeatability
    test_user_ids = [user1.id, user2.id, user3.id, user4.id]

    db.query(Certification).filter(Certification.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    db.query(ParsedResume).filter(ParsedResume.resume_id.in_(
        db.query(Resume.id).filter(Resume.user_id.in_(test_user_ids))
    )).delete(synchronize_session=False)
    db.query(Resume).filter(Resume.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    db.query(CandidateProfile).filter(CandidateProfile.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    db.query(GitHubRepository).filter(GitHubRepository.github_profile_id.in_(
        db.query(GitHubProfile.id).filter(GitHubProfile.user_id.in_(test_user_ids))
    )).delete(synchronize_session=False)
    db.query(GitHubProfile).filter(GitHubProfile.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    db.query(LinkedInProfile).filter(LinkedInProfile.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    db.query(LeetCodeProfile).filter(LeetCodeProfile.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    db.query(HackerRankProfile).filter(HackerRankProfile.user_id.in_(test_user_ids)).delete(synchronize_session=False)
    db.commit()

    # ----------------------------------------------------
    # Seed Complete Data for User 1
    # ----------------------------------------------------
    # CandidateProfile
    cp1 = CandidateProfile(
        user_id=user1.id,
        summary="Experienced software engineer specializing in Python, React, and Machine Learning.",
        skills=["Python 3", "ReactJS", "Docker-compose", "FastAPI"],
        experience=[{
            "company": "Tech Corp",
            "role": "Software Engineer Intern",
            "duration": "Jun 2023 - Aug 2023",
            "description": "Developed REST APIs in FastAPI and PostgreSQL.",
            "technologies": ["FastAPI", "Postgres"]
        }],
        education=[{
            "institution": "Stanford University",
            "degree": "B.S.",
            "field_of_study": "Computer Science",
            "start_date": "2020",
            "end_date": "2024",
            "grade": "3.9 GPA"
        }],
        projects=[{
            "title": "AI Roadmap Generator",
            "description": "Built automated roadmap system with LLMs.",
            "technologies": ["Python", "GenAI"]
        }]
    )
    db.add(cp1)

    # Resume & ParsedResume
    r1 = Resume(
        user_id=user1.id,
        file_name="alice_resume.pdf",
        file_path="uploads/resumes/alice_resume.pdf",
        file_type="application/pdf",
        file_size=2048,
        parsed_status=True
    )
    db.add(r1)
    db.commit()
    db.refresh(r1)

    pr1 = ParsedResume(
        resume_id=r1.id,
        name="Alice Intelligence",
        email="intel_user1@careerverse.ai",
        phone="+1-555-0100",
        skills=["Python", "PostgreSQL Database", "Kubernetes", "Generative AI", "Public Speaking"],
        education=[{
            "institution": "Stanford University",
            "degree": "Bachelor of Science",
            "field_of_study": "CS"
        }],
        experience=[{
            "company": "Tech Corp",
            "role": "Software Engineer Intern",
            "technologies": ["Python", "PostgreSQL"]
        }],
        projects=[{
            "title": "CareerVerse Assistant",
            "description": "Interactive AI bot for career planning.",
            "technologies": ["Python", "React"]
        }]
    )
    db.add(pr1)

    # GitHub Profile & Repos
    gh1 = GitHubProfile(
        user_id=user1.id,
        username="alice_dev",
        profile_url="https://github.com/alice_dev",
        total_repositories=5,
        total_stars=24,
        total_forks=8,
        languages={"Python": 4, "TypeScript": 1},
        topics=["machine-learning", "fastapi", "ai"]
    )
    db.add(gh1)
    db.commit()
    db.refresh(gh1)

    repo1 = GitHubRepository(
        github_profile_id=gh1.id,
        github_repo_id=987654321,
        name="carrer-ai-engine",
        url="https://github.com/alice_dev/carrer-ai-engine",
        language="Python",
        stars=15,
        forks=4,
        topics=["ai", "fastapi", "ml"],
        selected_for_analysis=True
    )
    db.add(repo1)

    # LinkedIn Profile
    li1 = LinkedInProfile(
        user_id=user1.id,
        linkedin_id="li_alice_12345",
        name="Alice Intelligence",
        email="intel_user1@careerverse.ai",
        email_verified=True,
        profile_picture="https://media.licdn.com/dms/image/alice.jpg",
        locale="en_US",
        access_token="SECRET_OAUTH_TOKEN_NEVER_EXPOSE"
    )
    db.add(li1)

    # LeetCode Profile
    lc1 = LeetCodeProfile(
        user_id=user1.id,
        username="alice_codes",
        profile_url="https://leetcode.com/alice_codes",
        ranking=12400,
        total_solved=350,
        easy_solved=150,
        medium_solved=160,
        hard_solved=40,
        acceptance_rate=68.5,
        contest_rating=1820.0,
        languages=[{"languageName": "Python", "problemsSolved": 280}, {"languageName": "C++", "problemsSolved": 70}],
        skills=[{"tagName": "Dynamic Programming", "problemsSolved": 80}]
    )
    db.add(lc1)

    # HackerRank Profile
    hr1 = HackerRankProfile(
        user_id=user1.id,
        username="alice_hr",
        profile_url="https://hackerrank.com/alice_hr",
        display_name="Alice Intelligence",
        country="United States",
        total_solved=120,
        badges=[{"badge_name": "Python", "stars": 5}, {"badge_name": "Problem Solving", "stars": 6}],
        certificates=[{"title": "Python (Basic)"}, {"title": "SQL (Advanced)"}]
    )
    db.add(hr1)

    # Certifications
    cert1 = Certification(
        user_id=user1.id,
        certification_name="AWS Certified Solutions Architect - Associate",
        issuing_organization="Amazon Web Services",
        issue_date=date(2024, 1, 15),
        credential_id="AWS-SAA-9921",
        credential_url="https://credly.com/badges/aws-saa-9921",
        source="PLATFORM_SYNC",
        verification_status="VERIFIED",
        extracted_skills=["AWS", "Cloud Architecture", "Docker"],
        confidence_score=0.95
    )
    cert2 = Certification(
        user_id=user1.id,
        certification_name="Deep Learning Specialization",
        issuing_organization="Coursera",
        issue_date=date(2024, 3, 10),
        credential_id="COURSERA-DL-441",
        credential_url="https://coursera.org/verify/COURSERA-DL-441",
        source="FILE_UPLOAD",
        verification_status="VERIFICATION_PENDING",
        extracted_skills=["Deep Learning", "TensorFlow", "Neural Networks"],
        confidence_score=0.85
    )
    db.add_all([cert1, cert2])
    db.commit()

    # ----------------------------------------------------
    # Seed Resume Only for User 2
    # ----------------------------------------------------
    r2 = Resume(
        user_id=user2.id,
        file_name="bob_resume.pdf",
        file_path="uploads/resumes/bob_resume.pdf",
        file_type="application/pdf",
        file_size=1024,
        parsed_status=True
    )
    db.add(r2)
    db.commit()
    db.refresh(r2)

    pr2 = ParsedResume(
        resume_id=r2.id,
        name="Bob ResumeOnly",
        email="intel_user2@careerverse.ai",
        skills=["Golang", "Docker", "Postgres"],
        experience=[{"company": "Startup X", "role": "Backend Intern", "technologies": ["Golang"]}]
    )
    db.add(pr2)
    db.commit()

    # ----------------------------------------------------
    # User 3 has NO data seeded (Zero-state)
    # ----------------------------------------------------

    # ----------------------------------------------------
    # User 4 has GitHub and Certifications only (Missing LinkedIn, LeetCode, HackerRank)
    # ----------------------------------------------------
    gh4 = GitHubProfile(
        user_id=user4.id,
        username="diana_dev",
        profile_url="https://github.com/diana_dev",
        total_repositories=2,
        languages={"Rust": 2}
    )
    db.add(gh4)

    cert4 = Certification(
        user_id=user4.id,
        certification_name="Rust Fundamentals",
        issuing_organization="Udemy",
        source="MANUAL",
        verification_status="UNVERIFIED",
        extracted_skills=["Rust"],
        confidence_score=0.7
    )
    db.add(cert4)
    db.commit()

    # Generate Auth Tokens
    token1 = create_access_token({"sub": user1.email, "id": user1.id})
    token2 = create_access_token({"sub": user2.email, "id": user2.id})
    token3 = create_access_token({"sub": user3.email, "id": user3.id})
    token4 = create_access_token({"sub": user4.email, "id": user4.id})

    db.close()
    return (user1, token1), (user2, token2), (user3, token3), (user4, token4)


# =========================================================================
# 1. TEST SKILL NORMALIZATION & DEDUPLICATION (STANDALONE PARSER TESTS)
# =========================================================================
def test_skill_normalizer_unit():
    """Verify alias normalization, category classification, and deduplication."""
    # Test normalization cases
    assert normalize_skill("Python 3") == ("Python", "Programming Languages")
    assert normalize_skill("python programming") == ("Python", "Programming Languages")
    assert normalize_skill("Postgres") == ("PostgreSQL", "Databases")
    assert normalize_skill("PostgreSQL Database") == ("PostgreSQL", "Databases")
    assert normalize_skill("ReactJS") == ("React", "Frameworks & Libraries")
    assert normalize_skill("Docker-compose") == ("Docker Compose", "Cloud & DevOps")
    assert normalize_skill("GenAI") == ("Generative AI", "Data Science & AI")
    assert normalize_skill("Business Email") == ("Email Writing", "Soft & Professional Skills")

    # Test deduplication and grouping
    raw_list = ["Python 3", "python", "Postgres", "PostgreSQL Database", "ReactJS", "React", "UnknownCustomTool"]
    deduped = deduplicate_and_group_skills(raw_list)
    assert "Programming Languages" in deduped
    assert "Python" in deduped["Programming Languages"]
    assert "PostgreSQL" in deduped["Databases"]
    assert "React" in deduped["Frameworks & Libraries"]
    assert "UnknownCustomTool" in deduped["Tools & Technologies"]
    # Check that Python is not duplicated
    assert deduped["Programming Languages"].count("Python") == 1


# =========================================================================
# 2. TEST UNIFIED PROFILE FOR COMPLETE DATA USER
# =========================================================================
def test_unified_profile_complete_user():
    (u1, t1), _, _, _ = setup_test_environment()
    headers = {"Authorization": f"Bearer {t1}"}

    res = client.get("/candidate-intelligence/unified-profile", headers=headers)
    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()

    # User Profile
    assert data["user_profile"]["name"] == "Alice Intelligence"
    assert data["user_profile"]["college"] == "Stanford University"

    # Summaries
    assert data["resume_summary"]["uploaded"] is True
    assert data["github_summary"]["connected"] is True
    assert data["github_summary"]["username"] == "alice_dev"
    assert data["linkedin_summary"]["connected"] is True
    assert data["linkedin_summary"]["name"] == "Alice Intelligence"
    # Security check: Never expose access_token
    assert "access_token" not in data["linkedin_summary"]
    assert "SECRET_OAUTH_TOKEN_NEVER_EXPOSE" not in str(data)

    assert data["leetcode_summary"]["connected"] is True
    assert data["leetcode_summary"]["total_solved"] == 350
    assert data["hackerrank_summary"]["connected"] is True
    assert data["hackerrank_summary"]["total_solved"] == 120
    assert data["certifications_summary"]["total_certifications"] == 2
    assert data["certifications_summary"]["verified_count"] == 1

    # Multi-source skill intelligence
    unified_skills = {s["name"]: s for s in data["unified_skills"]}
    assert "Python" in unified_skills
    python_skill = unified_skills["Python"]
    assert python_skill["category"] == "Programming Languages"
    # Python is present in candidate_profile, resume, github, leetcode, hackerrank (5 sources!)
    assert python_skill["supporting_sources_count"] >= 4
    assert len(python_skill["evidence"]) >= 4
    assert python_skill["confidence_score"] >= 0.85

    # Categories
    categories = [c["category"] for c in data["skills_by_category"]]
    assert "Programming Languages" in categories
    assert "Databases" in categories
    assert "Cloud & DevOps" in categories

    # Profile Completeness
    completeness = data["completeness"]
    assert completeness["score"] >= 80
    assert completeness["section_scores"]["basic_profile"] == 10
    assert completeness["section_scores"]["education"] == 10
    assert completeness["section_scores"]["github"] == 10
    assert completeness["section_scores"]["linkedin"] == 5
    assert len(completeness["data_quality_warnings"]) >= 0


# =========================================================================
# 3. TEST USER WITH RESUME ONLY
# =========================================================================
def test_unified_profile_resume_only_user():
    _, (u2, t2), _, _ = setup_test_environment()
    headers = {"Authorization": f"Bearer {t2}"}

    res = client.get("/candidate-intelligence/unified-profile", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["resume_summary"]["uploaded"] is True
    assert data["github_summary"]["connected"] is False
    assert data["linkedin_summary"]["connected"] is False
    assert data["leetcode_summary"]["connected"] is False
    assert data["hackerrank_summary"]["connected"] is False
    assert data["certifications_summary"]["total_certifications"] == 0

    # Skills from resume only
    skill_names = [s["name"] for s in data["unified_skills"]]
    assert "Go" in skill_names
    assert "Docker" in skill_names

    go_skill = next(s for s in data["unified_skills"] if s["name"] == "Go")
    assert go_skill["supporting_sources_count"] == 1
    # Single source has conservative confidence (e.g. 0.65 * 0.85 = ~0.55)
    assert 0.40 <= go_skill["confidence_score"] <= 0.65

    # Missing sections should include external integrations
    missing = data["completeness"]["missing_sections"]
    assert "GitHub Profile" in missing
    assert "LinkedIn Profile" in missing
    assert "Certifications" in missing


# =========================================================================
# 4. TEST USER WITH ZERO AVAILABLE DATA (ZERO-STATE RESPONSE)
# =========================================================================
def test_unified_profile_zero_state():
    _, _, (u3, t3), _ = setup_test_environment()
    headers = {"Authorization": f"Bearer {t3}"}

    res = client.get("/candidate-intelligence/unified-profile", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Graceful empty response
    assert data["user_profile"]["name"] == "Charlie Empty"
    assert data["education"] == []
    assert data["experience"] == []
    assert data["projects"] == []
    assert data["resume_summary"]["uploaded"] is False
    assert data["github_summary"]["connected"] is False
    assert data["linkedin_summary"]["connected"] is False
    assert data["leetcode_summary"]["connected"] is False
    assert data["hackerrank_summary"]["connected"] is False
    assert data["certifications_summary"]["total_certifications"] == 0
    assert data["unified_skills"] == []
    assert data["skills_by_category"] == []

    # Completeness
    completeness = data["completeness"]
    assert completeness["score"] < 30
    assert len(completeness["missing_sections"]) >= 5
    assert len(completeness["actionable_recommendations"]) >= 5


# =========================================================================
# 5. TEST PARTIAL INTEGRATIONS (MISSING GITHUB / LINKEDIN / CODING PLATFORMS)
# =========================================================================
def test_unified_profile_partial_integrations():
    _, _, _, (u4, t4) = setup_test_environment()
    headers = {"Authorization": f"Bearer {t4}"}

    res = client.get("/candidate-intelligence/unified-profile", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Connected: GitHub (Rust repo), Certifications (Rust)
    assert data["github_summary"]["connected"] is True
    assert data["certifications_summary"]["total_certifications"] == 1
    assert data["linkedin_summary"]["connected"] is False
    assert data["leetcode_summary"]["connected"] is False
    assert data["hackerrank_summary"]["connected"] is False

    # Rust skill appears in both GitHub and Certification (2 sources)
    rust_skill = next((s for s in data["unified_skills"] if s["name"] == "Rust"), None)
    assert rust_skill is not None
    assert rust_skill["supporting_sources_count"] == 2
    assert "github" in rust_skill["sources"]
    assert "certification" in rust_skill["sources"]
    assert len(rust_skill["evidence"]) == 2


# =========================================================================
# 6. TEST UNAUTHORIZED ACCESS AND USER ISOLATION
# =========================================================================
def test_unified_profile_security_and_isolation():
    (u1, t1), (u2, t2), _, _ = setup_test_environment()

    # 1. No auth header -> 401
    res_no_auth = client.get("/candidate-intelligence/unified-profile")
    assert res_no_auth.status_code == 401

    # 2. Invalid auth token -> 401
    res_bad_auth = client.get("/candidate-intelligence/unified-profile", headers={"Authorization": "Bearer invalid_token"})
    assert res_bad_auth.status_code == 401

    # 3. User isolation: User 2's request MUST NOT return User 1's data
    res_u2 = client.get("/candidate-intelligence/unified-profile", headers={"Authorization": f"Bearer {t2}"})
    assert res_u2.status_code == 200
    data2 = res_u2.json()
    assert data2["user_profile"]["name"] == "Bob ResumeOnly"
    assert data2["github_summary"]["connected"] is False
    assert "alice_dev" not in str(data2)


# =========================================================================
# 7. TEST FAULT TOLERANCE (HANDLES CORRUPT/MALFORMED JSON IN DB)
# =========================================================================
def test_fault_tolerance_with_corrupted_data():
    (u1, t1), _, _, _ = setup_test_environment()
    db: Session = SessionLocal()

    # Inject corrupt non-standard structure in CandidateProfile
    cp = db.query(CandidateProfile).filter(CandidateProfile.user_id == u1.id).first()
    if cp:
        cp.education = "String instead of list"
        cp.experience = [{"invalid_key": "val"}]
        cp.skills = ["InvalidSkillName!!!###"]
        db.commit()
    db.close()

    headers = {"Authorization": f"Bearer {t1}"}
    res = client.get("/candidate-intelligence/unified-profile", headers=headers)
    assert res.status_code == 200, "Service should gracefully handle malformed data without crashing"
    data = res.json()
    assert data["user_profile"]["name"] == "Alice Intelligence"


# =========================================================================
# 8. TEST EXISTING ENDPOINTS CONTINUE WORKING (NON-REGRESSION)
# =========================================================================
def test_existing_endpoints_non_regression():
    (u1, t1), _, _, _ = setup_test_environment()
    headers = {"Authorization": f"Bearer {t1}"}

    # Root
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert root_res.json()["message"] == "CarrerVerseAI API"

    # Profile
    prof_res = client.get("/profile", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["name"] == "Alice Intelligence"

    # Certifications
    cert_res = client.get("/certifications", headers=headers)
    assert cert_res.status_code == 200
    assert len(cert_res.json()) >= 1


# =========================================================================
# 9. TEST DATA QUALITY & EXTRACTION PRECISION
# =========================================================================
def test_certificate_ocr_data_quality():
    """Verify that recipient names and boilerplate phrases are filtered and skills are precise."""
    from app.parsers.certificate_extractor import (
        is_invalid_or_generic_title,
        extract_certification_name,
        extract_skills_from_text,
    )

    # 1. Recipient names and boilerplate blacklist
    assert is_invalid_or_generic_title("Ms. DHANYASRI K") is True
    assert is_invalid_or_generic_title("DHANYASRI K") is True
    assert is_invalid_or_generic_title("Presented to") is True
    assert is_invalid_or_generic_title("for successfully completing the course") is True
    assert is_invalid_or_generic_title("23AM018") is True
    assert is_invalid_or_generic_title("Prompt Engineering") is False

    # 2. Extract title from certificate text containing recipient and boilerplate
    sample_text = """
    KPR Institute of Engineering and Technology
    Certificate of Completion
    Presented to
    Ms. DHANYASRI K
    for successfully completing the course on
    C Programming
    Date: 2024-03-01
    """
    extracted_title = extract_certification_name(sample_text, filename="23AM018_C_Programming.pdf")
    assert "C Programming" in extracted_title
    assert "DHANYASRI" not in extracted_title
    assert "Presented" not in extracted_title

    # 3. Test skill extraction precision: "C test organized at KPR Institute" should extract "C", not "Java" or "C++"
    c_test_text = "Certificate of Achievement for participating in C test organized at KPR Institute of Engineering."
    skills = extract_skills_from_text(c_test_text, "C test")
    assert "C" in skills
    assert "C++" not in skills
    assert "Java" not in skills


def test_skill_normalization_html_css():
    """Verify that HTML, CSS, and compound variants normalize consistently."""
    assert normalize_skill("HTML")[0] == "HTML"
    assert normalize_skill("HTML5")[0] == "HTML"
    assert normalize_skill("CSS")[0] == "CSS"
    assert normalize_skill("CSS3")[0] == "CSS"
    assert normalize_skill("HTML5 / CSS3")[0] == "HTML / CSS"
    assert normalize_skill("HTML5 / CSS")[0] == "HTML / CSS"
    assert normalize_skill("HTML / CSS")[0] == "HTML / CSS"


def test_confidence_formula_transparency():
    """Verify confidence formula: 1 source matches evidence weight; multi-source gets clear boost."""
    from app.services.unified_profile_service import _collect_unified_skills
    from app.models.hackerrank_profile import HackerRankProfile

    # Single HackerRank certificate (evidence weight = 0.88)
    hr_profile = HackerRankProfile(
        username="hr_user",
        certificates=[{"title": "Problem Solving (Advanced)"}]
    )
    unified_skills, _ = _collect_unified_skills(
        candidate_profile=None,
        parsed_resumes=[],
        github_profile=None,
        github_repositories=[],
        leetcode_profile=None,
        hackerrank_profile=hr_profile,
        certifications=[]
    )
    assert len(unified_skills) > 0
    ps_skill = next((s for s in unified_skills if "Problem Solving" in s.name), None)
    assert ps_skill is not None
    assert ps_skill.supporting_sources_count == 1
    # Single source confidence matches evidence weight directly (0.88), not discounted to 0.75
    assert ps_skill.confidence_score == 0.88


if __name__ == "__main__":
    print("Running Candidate Intelligence & Unified Profile Tests...")
    test_skill_normalizer_unit()
    print("✓ test_skill_normalizer_unit passed")
    test_unified_profile_complete_user()
    print("✓ test_unified_profile_complete_user passed")
    test_unified_profile_resume_only_user()
    print("✓ test_unified_profile_resume_only_user passed")
    test_unified_profile_zero_state()
    print("✓ test_unified_profile_zero_state passed")
    test_unified_profile_partial_integrations()
    print("✓ test_unified_profile_partial_integrations passed")
    test_unified_profile_security_and_isolation()
    print("✓ test_unified_profile_security_and_isolation passed")
    test_fault_tolerance_with_corrupted_data()
    print("✓ test_fault_tolerance_with_corrupted_data passed")
    test_existing_endpoints_non_regression()
    print("✓ test_existing_endpoints_non_regression passed")
    test_certificate_ocr_data_quality()
    print("✓ test_certificate_ocr_data_quality passed")
    test_skill_normalization_html_css()
    print("✓ test_skill_normalization_html_css passed")
    test_confidence_formula_transparency()
    print("✓ test_confidence_formula_transparency passed")
    print("\n========================================================")
    print("ALL CANDIDATE INTELLIGENCE & DATA QUALITY TESTS PASSED!")
    print("========================================================")
