import pytest
from types import SimpleNamespace
from pydantic import ValidationError

from app.database.session import SessionLocal
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.models.proctoring_event import ProctoringEvent
from app.schemas.interview import CyraChatRequest
from app.schemas.interview_session import (
    InterviewAnswerRequest,
    InterviewQuestionPayload,
    InterviewSessionCreateRequest,
)
from app.services import conversational_interview_service as service
import json

class FakeProvider:
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
        elif "Candidate greeted:" in user_message:
            return SimpleNamespace(content="Hello! I am Dr. Cyra Vance, your AI interviewer. How can I help you today?", model="fake-model")
        elif "Candidate said:" in user_message:
            return SimpleNamespace(content="That's outside our technical scope. Let's stay focused on the interview question.", model="fake-model")
        elif "latest_answer" in user_message:
            content = {
                "assessment": "The answer described a concrete FastAPI use.",
                "strengths": ["Concrete implementation context"],
                "improvements": ["Explain authorization"],
                "follow_up_reason": "The answer mentioned REST APIs, so the follow-up probes authorization.",
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
def clean_interview_setup(monkeypatch):
    provider = FakeProvider()
    monkeypatch.setattr(service, "get_model_provider", lambda: provider)
    monkeypatch.setattr(service, "_candidate_context", lambda candidate_id, query: FakeContext())
    monkeypatch.setattr(service, "_graph_evidence", lambda candidate_id, **kwargs: {"skills": [{"name": "FastAPI"}]})
    db = SessionLocal()
    u = _user()
    if u:
        sess_ids = [s.session_id for s in db.query(InterviewSession).filter(InterviewSession.candidate_id == u.id).all()]
        if sess_ids:
            db.query(ProctoringEvent).filter(ProctoringEvent.session_id.in_(sess_ids)).delete(synchronize_session=False)
        db.query(InterviewSession).filter(InterviewSession.candidate_id == u.id).delete(synchronize_session=False)
        db.commit()
    yield db, u, provider
    if u:
        sess_ids = [s.session_id for s in db.query(InterviewSession).filter(InterviewSession.candidate_id == u.id).all()]
        if sess_ids:
            db.query(ProctoringEvent).filter(ProctoringEvent.session_id.in_(sess_ids)).delete(synchronize_session=False)
        db.query(InterviewSession).filter(InterviewSession.candidate_id == u.id).delete(synchronize_session=False)
        db.commit()
    db.close()


# ── PRIORITY 1: INTENT-AWARE CYRA CONVERSATION TESTS ──────────────────────────

def test_cyra_intent_routing_empty_message(clean_interview_setup):
    _, user, _ = clean_interview_setup
    req = CyraChatRequest(message="   ", current_question="Explain indexing in PostgreSQL")
    resp = service.generate_cyra_chat_response(req, user)
    assert resp.action_type == "empty_prompt"
    assert "listening" in resp.reply.lower() or "input" in resp.reply.lower()


def test_cyra_intent_routing_greeting(clean_interview_setup):
    _, user, _ = clean_interview_setup
    req = CyraChatRequest(message="Hello Cyra! Good morning", current_question="Explain indexing in PostgreSQL")
    resp = service.generate_cyra_chat_response(req, user)
    assert resp.action_type == "greeting"
    assert "Dr. Cyra Vance" in resp.reply or "hello" in resp.reply.lower() or "good to meet you" in resp.reply.lower()
    # Ensure it didn't evaluate an idea
    assert "your code" not in resp.reply.lower()


def test_cyra_intent_routing_hint(clean_interview_setup):
    _, user, _ = clean_interview_setup
    req = CyraChatRequest(message="Can you give me a subtle hint please?", current_question="Two Sum problem", action_type="hint")
    resp = service.generate_cyra_chat_response(req, user)
    assert resp.action_type == "hint"
    assert len(resp.reply) > 20


def test_cyra_intent_routing_try_again(clean_interview_setup):
    _, user, _ = clean_interview_setup
    req = CyraChatRequest(message="Let me try again with a different approach", current_question="LRU Cache implementation")
    resp = service.generate_cyra_chat_response(req, user)
    assert any(w in resp.reply.lower() for w in ["fresh", "again", "updated", "revised", "another", "try", "approach"])


def test_cyra_intent_routing_unrelated_message(clean_interview_setup):
    _, user, _ = clean_interview_setup
    req = CyraChatRequest(message="What is the weather like today?", current_question="Design a URL shortener")
    resp = service.generate_cyra_chat_response(req, user)
    assert any(w in resp.reply.lower() for w in ["scope", "technical", "focus", "get back", "back to", "stay focused"])


# ── PRIORITY 2: STRICT, EVIDENCE-BASED ANSWER EVALUATION TESTS ───────────────

def test_evaluation_rejects_empty_answer(clean_interview_setup):
    db, user, _ = clean_interview_setup
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest())
    with pytest.raises((service.InterviewSessionStateError, ValidationError)):
        service.submit_interview_answer(db, user, session.session_id, InterviewAnswerRequest(answer="   "))


def test_evaluation_greeting_gets_minimal_score(clean_interview_setup):
    db, user, _ = clean_interview_setup
    q = InterviewQuestionPayload(
        question="How do you handle deadlocks in PostgreSQL?",
        topic="PostgreSQL Concurrency",
        track="backend",
    )
    eval_res = service._fallback_evaluation("Hi Cyra, good morning!", q, "Backend Developer", language="en")
    assert eval_res.score == 1
    assert eval_res.rubric_scores.get("relevance") == 1
    assert eval_res.rubric_scores.get("technical_correctness") == 1
    assert "greeting" in eval_res.assessment.lower()
    assert len(eval_res.missing_elements) >= 1


def test_evaluation_dont_know_gets_honest_constructive_evaluation(clean_interview_setup):
    db, user, _ = clean_interview_setup
    q = InterviewQuestionPayload(
        question="Explain raft consensus algorithm invariants.",
        topic="Distributed Consensus",
        track="backend",
    )
    eval_res = service._fallback_evaluation("I don't know raft algorithm, haven't implemented it.", q, "Backend Developer", language="en")
    assert eval_res.score == 1
    assert eval_res.rubric_scores.get("relevance") == 2
    assert eval_res.rubric_scores.get("technical_correctness") == 1
    assert "unfamiliar" in eval_res.assessment.lower() or "first principles" in eval_res.assessment.lower()
    assert any("honest" in s.lower() for s in eval_res.strengths)


def test_evaluation_irrelevant_answer_gets_low_relevance(clean_interview_setup):
    db, user, _ = clean_interview_setup
    q = InterviewQuestionPayload(
        question="How do you diagnose memory leaks in a Python asynchronous web service?",
        topic="Python Memory Profiling",
        track="backend",
    )
    # Discussing something completely unrelated without tech anchors
    eval_res = service._fallback_evaluation(
        "Yesterday I baked an apple pie with cinnamon and crust and enjoyed it immensely with coffee.",
        q,
        "Backend Developer",
        language="en",
    )
    assert eval_res.score <= 2
    assert eval_res.rubric_scores.get("relevance") == 1
    assert "off-topic" in eval_res.assessment.lower()


def test_evaluation_partial_answer_receives_proportional_credit(clean_interview_setup):
    db, user, _ = clean_interview_setup
    q = InterviewQuestionPayload(
        question="How do database indexes speed up SELECT queries?",
        topic="Database Indexing",
        track="backend",
    )
    eval_res = service._fallback_evaluation("Indexes use B-trees to avoid full table scans.", q, "Backend Developer", language="en")
    assert 3 <= eval_res.score <= 5
    assert eval_res.rubric_scores.get("relevance") >= 5
    assert len(eval_res.missing_elements) >= 1
    assert eval_res.is_follow_up_needed is True


def test_evaluation_high_quality_answer_receives_high_marks(clean_interview_setup):
    db, user, _ = clean_interview_setup
    q = InterviewQuestionPayload(
        question="How do you handle database connection pooling and failover in high-concurrency backend services?",
        topic="Connection Pooling",
        track="backend",
    )
    detailed_answer = (
        "We implement connection pooling using PgBouncer in transaction pooling mode to multiplex thousands of client connections "
        "into a bounded pool of database server connections, avoiding process per connection overhead. We set pool size based on CPU cores "
        "and disk I/O capacity using Little's law. For failover, we configure read replicas with streaming replication and keepalives with automated "
        "health probes to promote a standby with minimal lag while preventing split-brain conditions."
    )
    eval_res = service._fallback_evaluation(detailed_answer, q, "Backend Developer", language="en")
    assert eval_res.score >= 7
    assert eval_res.rubric_scores.get("relevance") >= 8
    assert eval_res.rubric_scores.get("technical_correctness") >= 7
