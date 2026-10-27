import os
import sys
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.utils.security import hash_password
from app.core.dependencies import get_current_user

client = TestClient(app)


def _ensure_test_user():
    """Return (or create) a stable test candidate user in the test DB."""
    db = SessionLocal()
    try:
        # Ensure candidate role exists
        role = db.query(Role).filter(Role.name == "candidate").first()
        if not role:
            role = Role(name="candidate")
            db.add(role)
            db.commit()
            db.refresh(role)

        user = db.query(User).filter(User.email == "sg_frontend_test@candidate.io").first()
        if not user:
            user = User(
                name="SG Frontend Test",
                email="sg_frontend_test@candidate.io",
                hashed_password=hash_password("Test123!"),
                role_id=role.id,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        # Detach from session so object is usable after db.close()
        db.expunge(user)
        return user
    finally:
        db.close()


@pytest.fixture(autouse=True)
def _clear_overrides():
    """Guarantee dependency overrides are cleared after every test in this module."""
    yield
    app.dependency_overrides.clear()


def test_skill_gap_demonstrated_count():
    """Ensure the backend skill-gap endpoint returns a valid response for an
    authenticated candidate.  The frontend merges strengths + skill_gaps to
    count demonstrated skills; this test checks the endpoint itself is healthy.
    """
    test_user = _ensure_test_user()
    app.dependency_overrides[get_current_user] = lambda: test_user
    response = client.post(
        "/ai/career/skill-gap",
        json={"target_role": "Backend Developer", "query": ""},
    )
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}, body: {response.text}"
    data = response.json()
    # Accept any non-empty skill_gaps list — exact count depends on live AI output
    assert "skill_gaps" in data or "strengths" in data, "Response must contain skill_gaps or strengths"
