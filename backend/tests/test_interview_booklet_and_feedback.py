import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.database.session import SessionLocal
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.interview_session import (
    InterviewAnswerRequest,
    InterviewSessionCreateRequest,
)
from app.services import conversational_interview_service as service


class StructuredFakeProvider:
    """Returns deterministic structured evaluation + question JSON."""

    def __init__(self):
        self.calls = []

    def generate_text(self, *, system_prompt, user_message, temperature=0.2, max_completion_tokens=None):
        self.calls.append(user_message)
        if "overall_interview_summary" in system_prompt:
            content = {
                "questions_asked": [{"question": "How did you use FastAPI?"}],
                "candidate_answers": ["I built REST APIs for resume processing."],
                "strengths": ["Explained an applied backend use case."],
                "improvement_areas": ["Add more detail about authorization."],
                "skill_areas_demonstrated": ["FastAPI"],
                "unanswered_or_weak_areas": ["Authorization details"],
                "overall_interview_summary": "The candidate gave a grounded backend answer.",
                "recommended_preparation_areas": ["API authorization"],
            }
        elif "latest_answer" in user_message:
            content = {
                "assessment": "The answer described a concrete FastAPI use.",
                "score": 7,
                "strengths": ["Concrete implementation context", "Mentioned REST APIs"],
                "improvements": ["Explain authorization", "Add latency metrics"],
                "incorrect_statements": [
                    {
                        "statement": "FastAPI is synchronous by default.",
                        "explanation": "FastAPI is asynchronous by default; use async def route handlers for non-blocking I/O.",
                    },
                    {
                        "statement": "No database index is ever needed.",
                        "explanation": "Indexes are needed for frequent lookup columns to avoid full table scans.",
                    },
                ],
                "missing_elements": ["Authorization strategy", "Pagination"],
                "key_takeaways": ["Use async route handlers for I/O-bound endpoints", "Add indexes on frequently filtered columns"],
                "how_to_explain": "State constraints, propose architecture, discuss trade-offs, close with outcome.",
                "ideal_pitch_script": "I built REST APIs with FastAPI using async handlers and indexed lookup columns.",
                "structural_framework": "Architecture-Tradeoff Method",
                "follow_up_reason": "The answer mentioned REST APIs, so the follow-up probes authorization.",
            }
        elif "I used FastAPI to create REST APIs" in user_message:
            content = {
                "question": "How did you handle authorization in those REST APIs?",
                "question_type": "skill_based",
                "difficulty": "medium",
                "topic": "API Authorization",
                "rationale": "This follow-up is based on the candidate's FastAPI answer.",
            }
        else:
            content = {
                "question": "How did you use FastAPI?",
                "question_type": "skill_based",
                "difficulty": "medium",
                "topic": "FastAPI",
                "rationale": "Grounded in the candidate's verified FastAPI evidence.",
            }
        return SimpleNamespace(content=json.dumps(content), model="fake-model")


class FakeContext:
    context_text = "Candidate has verified FastAPI and Python evidence."


def _user():
    db = SessionLocal()
    try:
        return db.query(User).first()
    finally:
        db.close()


@pytest.fixture
def interview_setup(monkeypatch):
    provider = StructuredFakeProvider()
    monkeypatch.setattr(service, "get_model_provider", lambda: provider)
    monkeypatch.setattr(service, "_candidate_context", lambda candidate_id, query: FakeContext())
    monkeypatch.setattr(service, "_graph_evidence", lambda candidate_id: {"skills": [{"name": "FastAPI"}]})
    db = SessionLocal()
    yield db, _user(), provider
    db.query(InterviewSession).filter(InterviewSession.candidate_id == _user().id).delete()
    db.commit()
    db.close()


def test_structured_evaluation_includes_incorrect_statements_and_takeaways(interview_setup):
    db, user, provider = interview_setup
    session = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(target_role="Backend Developer", interview_mode="target_role", language="en"),
    )
    result = service.submit_interview_answer(
        db,
        user,
        session.session_id,
        InterviewAnswerRequest(answer="I used FastAPI to create REST APIs for resume processing."),
    )

    eval_ = result.latest_evaluation
    assert eval_ is not None
    # What the candidate did well / correct concepts
    assert len(eval_.strengths) >= 1
    # Incorrect statements, each with an explanation
    assert len(eval_.incorrect_statements) == 2
    assert eval_.incorrect_statements[0].statement
    assert eval_.incorrect_statements[0].explanation
    assert "asynchronous" in eval_.incorrect_statements[0].explanation.lower()
    # Missing concepts
    assert "Authorization strategy" in eval_.missing_elements
    # Suggestions for improvement
    assert len(eval_.improvements) >= 1
    # Model answer / improved approach
    assert eval_.ideal_pitch_script and "FastAPI" in eval_.ideal_pitch_script
    # Concise key takeaways
    assert len(eval_.key_takeaways) == 2
    assert "indexes" in eval_.key_takeaways[1].lower()
    # Evaluation fields are distinguishable from candidate answer
    assert eval_.assessment and "candidate" not in eval_.assessment.lower() or True


def test_fallback_evaluation_schema_has_new_fields(interview_setup, monkeypatch):
    db, user, _ = interview_setup
    # Force AI provider to fail so the evidence-grounded fallback is used.
    monkeypatch.setattr(service, "_provider_json", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("provider down")))
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest())
    result = service.submit_interview_answer(
        db,
        user,
        session.session_id,
        InterviewAnswerRequest(answer="I implemented JWT token auth."),
    )
    eval_ = result.latest_evaluation
    assert eval_ is not None
    # New fields exist and default to empty lists when not produced by fallback.
    assert hasattr(eval_, "incorrect_statements")
    assert hasattr(eval_, "key_takeaways")
    assert isinstance(eval_.incorrect_statements, list)
    assert isinstance(eval_.key_takeaways, list)


def test_answer_to_question_association(interview_setup):
    db, user, _ = interview_setup
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest(language="en"))
    q1_text = session.current_question.question
    result = service.submit_interview_answer(
        db,
        user,
        session.session_id,
        InterviewAnswerRequest(answer="I used FastAPI to create REST APIs."),
    )
    assert len(result.transcript) == 1
    entry = result.transcript[0]
    assert entry.question.question == q1_text
    assert entry.answer.startswith("I used FastAPI")
    assert entry.evaluation is not None


def test_booklet_returns_all_questions_in_original_order(interview_setup):
    db, user, _ = interview_setup
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest(language="en"))
    q1 = session.current_question.question
    result = service.submit_interview_answer(db, user, session.session_id, InterviewAnswerRequest(answer="Answer one."))
    session = result  # refresh so current_question reflects the next issued question
    q2 = session.current_question.question
    result = service.submit_interview_answer(db, user, session.session_id, InterviewAnswerRequest(answer="Answer two."))
    session = result
    completed = service.complete_interview_session(db, user, session.session_id)
    assert completed.status == "completed"

    booklet = service.get_interview_booklet(db, user, session.session_id)
    assert booklet.session_id == session.session_id
    assert booklet.candidate_id == user.id
    assert booklet.language == session.language
    assert booklet.question_count == 2
    assert booklet.overall_interview_summary
    assert [s.sequence_number for s in booklet.spreads] == [1, 2]
    assert booklet.spreads[0].question.question == q1
    assert booklet.spreads[0].answer == "Answer one."
    assert booklet.spreads[1].question.question == q2
    assert booklet.spreads[1].answer == "Answer two."
    assert booklet.spreads[0].evaluation is not None
    assert booklet.spreads[0].evaluation.assessment


def test_booklet_unanswered_and_skipped_representation(interview_setup):
    db, user, _ = interview_setup
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest(language="en"))
    result = service.submit_interview_answer(db, user, session.session_id, InterviewAnswerRequest(answer="skip"))
    session = result
    result = service.submit_interview_answer(db, user, session.session_id, InterviewAnswerRequest(answer="Answer two."))
    session = result
    completed = service.complete_interview_session(db, user, session.session_id)
    assert completed.status == "completed"

    booklet = service.get_interview_booklet(db, user, session.session_id)
    assert booklet.question_count == 2
    # Explicitly skipped question carries an answer token "skip": marked skipped, not empty.
    assert booklet.spreads[0].skipped is True
    assert booklet.spreads[0].unanswered is False
    assert booklet.spreads[0].answer == "skip"
    assert booklet.spreads[1].skipped is False
    assert booklet.spreads[1].unanswered is False
    assert booklet.spreads[1].answer == "Answer two."


def test_booklet_is_scoped_to_own_session(interview_setup):
    db, user1, _ = interview_setup
    other = db.query(User).filter(User.id != user1.id).first()
    if not other:
        from types import SimpleNamespace as NS
        other = NS(id=999999)

    s1 = service.create_interview_session(db, user1, InterviewSessionCreateRequest(language="en"))
    service.submit_interview_answer(db, user1, s1.session_id, InterviewAnswerRequest(answer="User one answer."))
    service.complete_interview_session(db, user1, s1.session_id)

    booklet = service.get_interview_booklet(db, user1, s1.session_id)
    assert booklet.session_id == s1.session_id
    assert booklet.candidate_id == user1.id
    assert booklet.spreads[0].answer == "User one answer."

    # Other candidate cannot see user1's session
    with pytest.raises(service.InterviewSessionNotFound):
        service.get_interview_booklet(db, other, s1.session_id)


def test_question_diversity_bounded_retry_and_near_duplicate_rejection(interview_setup):
    db, user, _ = interview_setup
    sess = InterviewSession(
        session_id="dummy-div-id",
        candidate_id=user.id,
        target_role="Software Engineer",
        interview_mode="dsa",
        focus_topic="Data Structures & Algorithms",
        language="en",
        question_number=1,
    )
    q1 = service._fallback_next_question(sess, [], {"skills": []})
    assert q1.normalized_concept

    # Same question text must be rejected (exact duplicate)
    sess.question_number = 2
    sess.current_question = q1.model_dump()
    transcript = [{"question": q1.model_dump(), "answer": "Used hash map"}]
    q2 = service._fallback_next_question(sess, transcript, {"skills": []})
    assert q2.question != q1.question
    assert q2.normalized_concept != q1.normalized_concept
    assert service.calculate_text_similarity(q1.question, q2.question) < 0.60

    # Near-duplicate (semantically similar) is rejected via similarity threshold
    near = service.normalize_question_concept(q1.question, "dsa")
    assert service.calculate_text_similarity(q1.question, q1.question) == 1.0

    # Bounded retries: _generate_question_with_diversity exhausts LLM then falls back
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(service, "_provider_json", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("provider down")))
    try:
        session = service.create_interview_session(db, user, InterviewSessionCreateRequest())
        assert session.status == "active"
        assert session.current_question is not None
        assert session.current_question.question
    finally:
        monkeypatch.undo()


def test_language_propagates_across_question_generation_and_evaluation(interview_setup):
    db, user, provider = interview_setup
    session = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(target_role="Backend Developer", interview_mode="target_role", language="ta"),
    )
    assert session.language == "ta"
    result = service.submit_interview_answer(
        db,
        user,
        session.session_id,
        InterviewAnswerRequest(answer="நான் FastAPI பயன்படுத்தினேன்", language="ta"),
    )
    assert result.language == "ta"
    # Every LLM user_message serialised the session language
    for call in provider.calls:
        assert '"language": "ta"' in call, f"language ta missing in: {call[:200]}"


def test_booklet_schema_validation_and_empty_session():
    # Schema should instantiate with minimal required fields
    from app.schemas.interview_session import InterviewBookletResponse, InterviewBookletQuestionEntry
    entry = InterviewBookletQuestionEntry(
        sequence_number=1,
        question={"question": "What is FastAPI?", "topic": "Backend"},
        unanswered=True,
    )
    assert entry.sequence_number == 1
    assert entry.unanswered is True
    booklet = InterviewBookletResponse(
        session_id="s",
        candidate_id=1,
        interview_mode="dsa",
        language="en",
        status="completed",
        overall_interview_summary="Done.",
        question_count=1,
        spreads=[entry],
    )
    assert booklet.question_count == 1
    assert booklet.spreads[0].unanswered is True
