import os
import io
import fitz
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.models.resume import Resume
from app.models.parsed_resume import ParsedResume
from app.models.job import Job
from app.models.github_profile import GitHubProfile
from app.models.github_repository import GitHubRepository
from app.models.certification import Certification
from app.utils.security import hash_password
from app.utils.jwt import create_access_token
from app.parsers.skill_normalizer import normalize_skill as parser_norm, get_canonical_skill_name
from app.utils.skill_normalizer import normalize_skill as utils_norm

client = TestClient(app)


def setup_test_users():
    db: Session = SessionLocal()

    # Roles
    candidate_role = db.query(Role).filter(Role.name == "candidate").first()
    if not candidate_role:
        candidate_role = Role(name="candidate")
        db.add(candidate_role)
        db.commit()
        db.refresh(candidate_role)

    recruiter_role = db.query(Role).filter(Role.name == "recruiter").first()
    if not recruiter_role:
        recruiter_role = Role(name="recruiter")
        db.add(recruiter_role)
        db.commit()
        db.refresh(recruiter_role)

    # Candidate User
    candidate = db.query(User).filter(User.email == "alex_stab@candidate.io").first()
    if not candidate:
        candidate = User(
            name="Alex Candidate",
            email="alex_stab@candidate.io",
            hashed_password=hash_password("Secret123!"),
            role_id=candidate_role.id,
            is_active=True
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)

    # Recruiter User
    recruiter = db.query(User).filter(User.email == "rachel_stab@techcorp.io").first()
    if not recruiter:
        recruiter = User(
            name="Rachel Recruiter",
            email="rachel_stab@techcorp.io",
            hashed_password=hash_password("Secret123!"),
            role_id=recruiter_role.id,
            is_active=True
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)

    candidate_token = create_access_token({"sub": candidate.email})
    recruiter_token = create_access_token({"sub": recruiter.email})

    candidate_id = candidate.id
    recruiter_id = recruiter.id

    db.close()
    return candidate_token, recruiter_token, candidate_id, recruiter_id


def test_resume_parsing_status_lifecycle(tmp_path):
    candidate_token, _, candidate_id, _ = setup_test_users()
    headers = {"Authorization": f"Bearer {candidate_token}"}
    db: Session = SessionLocal()

    # 1. Create a genuine test PDF on disk using PyMuPDF
    resume_file = tmp_path / "alex_stab_resume.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "Alex Candidate\nEmail: alex_stab@candidate.io\nPhone: +1 555-0199\n\nSkills:\nPython, FastAPI, Docker, PostgreSQL\n\nExperience:\nSoftware Engineer at TechCorp\n\nEducation:\nBachelor of Science in Computer Science")
    doc.save(str(resume_file))
    doc.close()

    # 2. Insert Resume into DB with parsed_status = False
    resume = Resume(
        user_id=candidate_id,
        file_name="alex_stab_resume.pdf",
        file_path=str(resume_file),
        file_type="application/pdf",
        file_size=os.path.getsize(str(resume_file)),
        parsed_status=False
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    resume_id = resume.id

    # Verify initial status is False
    assert resume.parsed_status is False

    # 3. Trigger parse resume
    parse_res = client.post(f"/parser/parse/{resume_id}", headers=headers)
    assert parse_res.status_code == 200, f"Parse failed: {parse_res.text}"

    # Verify parsed_status updated to True in database
    db.refresh(resume)
    assert resume.parsed_status is True

    # 4. Trigger reparse resume
    reparse_res = client.post(f"/parser/reparse/{resume_id}", headers=headers)
    assert reparse_res.status_code == 200
    db.refresh(resume)
    assert resume.parsed_status is True

    # 5. Delete parsed resume -> status should revert to False
    del_res = client.delete(f"/parser/resume/{resume_id}", headers=headers)
    assert del_res.status_code == 200
    db.refresh(resume)
    assert resume.parsed_status is False

    # Cleanup
    db.delete(resume)
    db.commit()
    db.close()


def test_job_security_and_role_authorization_matrix():
    candidate_token, recruiter_token, _, _ = setup_test_users()
    candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
    recruiter_headers = {"Authorization": f"Bearer {recruiter_token}"}

    job_payload = {
        "title": "Senior Backend Architect Stabilization",
        "company": "DeepTech Systems",
        "description": "Lead high-scale Python and distributed microservice infrastructure.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        "location": "San Francisco, CA (Hybrid)",
        "salary": "$170,000 - $210,000",
        "experience": "5+ years"
    }

    # 1. Anonymous user attempts job creation -> 401 Unauthorized
    anon_post = client.post("/jobs/", json=job_payload)
    assert anon_post.status_code == 401

    # 2. Candidate attempts job creation -> 403 Forbidden
    candidate_post = client.post("/jobs/", json=job_payload, headers=candidate_headers)
    assert candidate_post.status_code == 403
    assert "Forbidden" in candidate_post.json()["detail"]

    # 3. Recruiter creates job -> 201 Created
    recruiter_post = client.post("/jobs/", json=job_payload, headers=recruiter_headers)
    assert recruiter_post.status_code == 201
    job_id = recruiter_post.json()["id"]
    assert recruiter_post.json()["title"] == "Senior Backend Architect Stabilization"

    # 4. Candidate can browse and view jobs -> 200 OK
    list_jobs = client.get("/jobs/", headers=candidate_headers)
    assert list_jobs.status_code == 200
    assert len(list_jobs.json()) >= 1

    get_job = client.get(f"/jobs/{job_id}", headers=candidate_headers)
    assert get_job.status_code == 200
    assert get_job.json()["company"] == "DeepTech Systems"

    # 5. Candidate attempts to delete job -> 403 Forbidden
    candidate_delete = client.delete(f"/jobs/{job_id}", headers=candidate_headers)
    assert candidate_delete.status_code == 403

    # 6. Recruiter deletes job -> 200 OK
    recruiter_delete = client.delete(f"/jobs/{job_id}", headers=recruiter_headers)
    assert recruiter_delete.status_code == 200


def test_unified_skill_gap_analysis_engine():
    candidate_token, recruiter_token, candidate_id, _ = setup_test_users()
    candidate_headers = {"Authorization": f"Bearer {candidate_token}"}
    recruiter_headers = {"Authorization": f"Bearer {recruiter_token}"}
    db: Session = SessionLocal()

    # 1. Create target job requiring Python, FastAPI, PostgreSQL, Kubernetes, Rust
    job_payload = {
        "title": "Cloud Infrastructure Lead Stabilization",
        "company": "ScaleAI Labs",
        "description": "Build high-throughput AI pipelines.",
        "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "Rust"],
        "location": "Remote",
        "salary": "$180,000",
        "experience": "4+ years"
    }
    create_res = client.post("/jobs/", json=job_payload, headers=recruiter_headers)
    assert create_res.status_code == 201
    job_id = create_res.json()["id"]

    # 2. Populate candidate user with multiple data sources:
    db.query(GitHubRepository).filter(GitHubRepository.name == "fastapi-orchestrator-stab").delete()
    db.query(GitHubProfile).filter(GitHubProfile.user_id == candidate_id).delete()
    db.query(Certification).filter(Certification.user_id == candidate_id).delete()
    db.commit()

    gh_profile = GitHubProfile(
        user_id=candidate_id,
        username="alexdev_stab",
        languages=["Python", "FastAPI"],
        profile_url="https://github.com/alexdev_stab",
        total_repositories=5,
        total_stars=24
    )
    db.add(gh_profile)
    db.commit()
    db.refresh(gh_profile)

    gh_repo = GitHubRepository(
        github_profile_id=gh_profile.id,
        github_repo_id=987654,
        name="fastapi-orchestrator-stab",
        language="Python",
        stars=18,
        topics=["fastapi", "docker", "postgresql"]
    )
    db.add(gh_repo)

    # - Verified Certification in Kubernetes
    cert = Certification(
        user_id=candidate_id,
        name="Certified Kubernetes Administrator (CKA)",
        issuing_organization="Cloud Native Computing Foundation",
        source="PLATFORM_SYNC",
        verification_status="VERIFIED",
        extracted_skills=["Kubernetes", "Docker"],
        confidence_score=0.95
    )
    db.add(cert)
    db.commit()

    # 3. Execute Unified Skill Gap Analysis
    unified_gap_res = client.post(f"/skill-gap/analyze-unified/{job_id}", headers=candidate_headers)
    assert unified_gap_res.status_code == 200
    data = unified_gap_res.json()

    # Assertions
    assert data["job_id"] == job_id
    assert data["job_title"] == "Cloud Infrastructure Lead Stabilization"
    assert data["company"] == "ScaleAI Labs"
    assert data["total_required_skills"] == 6

    # Matched skills should include Python, FastAPI, PostgreSQL, Docker, Kubernetes
    assert "Python" in data["matched_skills"]
    assert "Kubernetes" in data["matched_skills"]
    assert "FastAPI" in data["matched_skills"]
    
    # Missing skills should be Rust
    assert "Rust" in data["missing_skills"]
    assert data["match_percentage"] > 70.0
    assert len(data["matched_skills_details"]) >= 4
    assert len(data["recommendations"]) >= 1

    # 4. Verify GET endpoint works identically
    get_gap_res = client.get(f"/skill-gap/analyze-unified/{job_id}", headers=candidate_headers)
    assert get_gap_res.status_code == 200
    assert get_gap_res.json()["match_percentage"] == data["match_percentage"]

    # 5. Non-existent job returns 404
    missing_job_res = client.post("/skill-gap/analyze-unified/999999", headers=candidate_headers)
    assert missing_job_res.status_code == 404

    # Cleanup job
    client.delete(f"/jobs/{job_id}", headers=recruiter_headers)
    db.close()


def test_skill_normalizer_single_source_of_truth():
    test_cases = [
        ("py", "Python"),
        ("python3", "Python"),
        ("js", "JavaScript"),
        ("reactjs", "React"),
        ("react.js", "React"),
        ("postgres", "PostgreSQL"),
        ("postgresql", "PostgreSQL"),
        ("k8s", "Kubernetes"),
        ("ts", "TypeScript"),
        ("docker", "Docker"),
        ("fastapi", "FastAPI"),
        ("mongodb", "MongoDB"),
        ("genai", "Generative AI"),
        ("html5/css3", "HTML / CSS")
    ]

    for raw_alias, expected_canonical in test_cases:
        from_parser = get_canonical_skill_name(raw_alias)
        from_utils = utils_norm(raw_alias)
        
        assert from_parser == expected_canonical, f"Parser failed for {raw_alias}: got {from_parser}, expected {expected_canonical}"
        assert from_utils == expected_canonical, f"Utils failed for {raw_alias}: got {from_utils}, expected {expected_canonical}"
        assert from_parser == from_utils, f"Mismatch between normalizers for {raw_alias}"


def test_cors_and_health_check():
    # 1. Health check
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "CarrerVerseAI API"
    assert data["status"] == "healthy"

    # 2. CORS Preflight OPTIONS check
    options_res = client.options(
        "/jobs/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type"
        }
    )
    assert options_res.status_code in [200, 204]
    assert options_res.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_auth_validation_and_security():
    setup_test_users()
    
    # 1. Duplicate registration returns 400
    dup_res = client.post("/auth/register", json={
        "name": "Alex Duplicate",
        "email": "alex_stab@candidate.io",
        "password": "Password123!",
        "role_id": 1
    })
    assert dup_res.status_code == 400
    assert "already registered" in dup_res.json()["detail"].lower()

    # 2. Invalid password login returns 401
    bad_login = client.post("/auth/login", json={
        "email": "alex_stab@candidate.io",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401
    assert "invalid email or password" in bad_login.json()["detail"].lower()

    # 3. Non-existent user login returns 401
    no_user = client.post("/auth/login", json={
        "email": "ghost_nonexistent_user@candidate.io",
        "password": "Password123!"
    })
    assert no_user.status_code == 401
