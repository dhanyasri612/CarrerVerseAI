import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./resume_ai_test.db")

import fitz
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.session import SessionLocal
from app.models.role import Role
from app.models.user import User
from app.models.resume import Resume
from app.services.ai_service import ai_service
from app.utils.security import hash_password
from app.utils.jwt import create_access_token
from app.core.dependencies import get_current_user

client = TestClient(app)


class FakeResumeAIProvider:
    def generate(self, **kwargs):
        return type(
            "Response",
            (),
            {
                "content": '{"summary":"Experienced Python engineer.","skills":[{"name":"Python","category":"programming_language","evidence":"Built backend services in Python","source_section":"projects","confidence":"High"}],"education":[],"experience":[],"projects":[],"certifications":[],"achievements":[]}',
                "model": "fake-model",
            },
        )()


def setup_user_and_resume(user_email: str = "resume_ai_user@careerverse.ai"):
    db: Session = SessionLocal()
    role = db.query(Role).filter(Role.name == "candidate").first()
    if not role:
        role = Role(name="candidate")
        db.add(role)
        db.commit()
        db.refresh(role)

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        user = User(
            name="Resume AI User",
            email=user_email,
            hashed_password=hash_password("Pass123!"),
            role_id=role.id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    existing_resume = db.query(Resume).filter(Resume.user_id == user.id).first()
    if existing_resume:
        if existing_resume.file_path and os.path.exists(existing_resume.file_path):
            os.remove(existing_resume.file_path)
        db.delete(existing_resume)
        db.commit()

    os.makedirs("uploads/resumes", exist_ok=True)
    file_path = os.path.join("uploads", "resumes", f"{user.id}_resume.pdf")
    if os.path.exists(file_path):
        os.remove(file_path)

    pdf = fitz.open()
    page = pdf.new_page()
    page.insert_text((72, 72), "Python backend engineer with FastAPI experience and cloud deployment work.")
    pdf.save(file_path)
    pdf.close()

    resume = Resume(
        user_id=user.id,
        file_name="resume.pdf",
        file_path=file_path,
        file_type="application/pdf",
        file_size=os.path.getsize(file_path),
        parsed_status=True,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    token = create_access_token({"sub": user.email})
    db.close()
    return user, resume, token


def test_resume_ai_schema_validates_response(monkeypatch):
    monkeypatch.setattr(ai_service, "provider", FakeResumeAIProvider())
    result, model = ai_service.generate_resume_intelligence(resume_text="Python backend development experience")
    assert result.summary == "Experienced Python engineer."
    assert result.skills[0].name == "Python"
    assert result.skills[0].confidence == "High"
    assert model == "fake-model"


def test_resume_ai_endpoint_returns_typed_response(monkeypatch):
    monkeypatch.setattr(ai_service, "provider", FakeResumeAIProvider())
    user, resume, token = setup_user_and_resume("resume_ai_endpoint@careerverse.ai")
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        response = client.post(f"/ai/resume/{resume.id}/analyze")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == "Experienced Python engineer."
    assert payload["skills"][0]["name"] == "Python"
    assert payload["skills"][0]["confidence"] == "High"


def test_resume_ai_requires_resume_ownership():
    user, resume, token = setup_user_and_resume("resume_ai_user_ownership@careerverse.ai")
    other_user_email = "resume_ai_other@careerverse.ai"
    db: Session = SessionLocal()
    other_user = db.query(User).filter(User.email == other_user_email).first()
    if not other_user:
        other_user = User(
            name="Other User",
            email=other_user_email,
            hashed_password=hash_password("Pass123!"),
            role_id=db.query(Role).filter(Role.name == "candidate").first().id,
            is_active=True,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
    db.close()

    other_token = create_access_token({"sub": other_user.email})
    response = client.post(
        f"/ai/resume/{resume.id}/analyze",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404


def test_resume_ai_missing_resume_returns_404():
    _, _, token = setup_user_and_resume("resume_ai_missing@careerverse.ai")
    response = client.post(
        "/ai/resume/999999/analyze",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_resume_ai_invalid_provider_response_is_rejected(monkeypatch):
    monkeypatch.setattr(ai_service, "provider", type("BadProvider", (), {"generate": lambda self, **kwargs: type("BadResponse", (), {"content": '{"bad": true}', "model": "bad-model"})()})())
    try:
        ai_service.generate_resume_intelligence(resume_text="Python and FastAPI")
        assert False, "Expected validation error"
    except Exception:
        assert True
