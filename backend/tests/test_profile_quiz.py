import json
from types import SimpleNamespace

import pytest

from app.database.session import SessionLocal
from app.models.profile_quiz_session import ProfileQuizSession
from app.models.user import User
from app.schemas.profile_quiz import QuizAnswerRequest, QuizSessionCreateRequest
from app.services import profile_quiz_service as service


class FakeProvider:
    def generate_text(self, *, system_prompt, user_message, temperature=0.2, max_completion_tokens=None):
        if "Career Intelligence Synthesizer" in system_prompt:
            payload = {
                "career_direction": "Backend engineering",
                "summary": "Your answers support exploring backend engineering with the evidence currently available.",
                "career_paths": ["Backend Developer"],
                "strengths": ["API development"],
                "skills_to_develop": ["Cloud deployment"],
                "recommended_next_steps": ["Build a deployable API project"],
            }
        else:
            payload = {
                "questions": [
                    {"id": "q1", "question": "Which kind of work energizes you?", "question_type": "single", "options": ["Building APIs", "Designing interfaces"], "why_it_matters": "Helps identify your preferred work."},
                    {"id": "q2", "question": "Describe a project you are proud of.", "question_type": "text", "options": [], "why_it_matters": "Adds project context."},
                ]
            }
        return SimpleNamespace(content=json.dumps(payload), model="test-model")


@pytest.fixture
def quiz_setup(monkeypatch):
    db = SessionLocal()
    user = db.query(User).first()
    provider = FakeProvider()
    monkeypatch.setattr(service, "get_model_provider", lambda: provider)
    monkeypatch.setattr(service, "_evidence", lambda *args, **kwargs: {"context": "Verified candidate context"})
    yield db, user
    db.query(ProfileQuizSession).filter(ProfileQuizSession.candidate_id == user.id).delete()
    db.commit()
    db.close()


def test_quiz_lifecycle_and_personalized_result(quiz_setup):
    db, user = quiz_setup
    session = service.create_quiz_session(db, user, QuizSessionCreateRequest())
    assert session.status == "active"
    assert len(session.questions) in (2, 5)
    answered = service.answer_quiz_question(db, user, session.session_id, QuizAnswerRequest(answer="Building APIs"))
    assert answered.question_number == 2
    assert answered.answers[0]["answer"] == "Building APIs"
    completed = service.complete_quiz(db, user, session.session_id)
    assert completed.status == "completed"
    assert completed.result.career_direction == "Backend engineering"


def test_quiz_session_isolation(quiz_setup):
    db, user = quiz_setup
    session = service.create_quiz_session(db, user, QuizSessionCreateRequest())
    other = db.query(User).filter(User.id != user.id).first()
    with pytest.raises(service.QuizSessionNotFound):
        service.get_quiz_session(db, other, session.session_id)
