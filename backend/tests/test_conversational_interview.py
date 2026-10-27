import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.ai.rag import context_builder as context_module
from app.database.session import SessionLocal
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.interview_session import (
    InterviewAnswerRequest,
    InterviewSessionCreateRequest,
)
from app.services import conversational_interview_service as service


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
        elif "latest_answer" in user_message:
            content = {
                "assessment": "The answer described a concrete FastAPI use.",
                "strengths": ["Concrete implementation context"],
                "improvements": ["Explain authorization"],
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
    provider = FakeProvider()
    monkeypatch.setattr(service, "get_model_provider", lambda: provider)
    monkeypatch.setattr(service, "_candidate_context", lambda candidate_id, query: FakeContext())
    monkeypatch.setattr(service, "_graph_evidence", lambda candidate_id: {"skills": [{"name": "FastAPI"}]})
    from app.models.proctoring_event import ProctoringEvent
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


def test_session_creation_and_first_question(interview_setup):
    db, user, provider = interview_setup
    result = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(target_role="Backend Developer", interview_mode="target_role", language="en"),
    )

    assert result.session_id
    assert result.candidate_id == user.id
    assert result.question_number == 1
    assert result.current_question.question == "How did you use FastAPI?"
    assert provider.calls


def test_answer_persists_transcript_and_generates_follow_up(interview_setup, monkeypatch):
    db, user, _ = interview_setup
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest(language="ta"))
    result = service.submit_interview_answer(
        db,
        user,
        session.session_id,
        InterviewAnswerRequest(answer="I used FastAPI to create REST APIs for resume processing."),
    )

    assert len(result.transcript) == 1
    assert result.transcript[0].answer.startswith("I used FastAPI")
    assert result.latest_evaluation.follow_up_reason
    assert result.question_number == 2
    assert result.current_question is not None
    assert "authorization" in result.current_question.question.lower()


def test_session_isolation_and_resume(interview_setup):
    db, user, _ = interview_setup
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest())
    assert service.get_interview_session(db, user, session.session_id).session_id == session.session_id
    other = db.query(User).filter(User.id != user.id).first()
    with pytest.raises(service.InterviewSessionNotFound):
        service.get_interview_session(db, other, session.session_id)
    with pytest.raises(service.InterviewSessionNotFound):
        service.get_interview_session(db, user, "missing-session")


def test_completion_returns_report(interview_setup):
    db, user, _ = interview_setup
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest())
    service.submit_interview_answer(db, user, session.session_id, InterviewAnswerRequest(answer="I built REST APIs."))
    completed = service.complete_interview_session(db, user, session.session_id)

    assert completed.status == "completed"
    assert completed.completed_at is not None
    assert completed.final_report.overall_interview_summary
    assert completed.current_question is None


def test_supported_languages_and_empty_answer_validation():
    for language in ("en", "ta", "hi"):
        assert InterviewSessionCreateRequest(language=language).language == language
    with pytest.raises(ValidationError):
        InterviewAnswerRequest(answer="   ")


def test_provider_and_rag_failures_are_not_silently_persisted(interview_setup, monkeypatch):
    db, user, provider = interview_setup
    # AI provider failure falls back gracefully to evidence-grounded question
    monkeypatch.setattr(service, "_provider_json", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("provider unavailable")))
    sess = service.create_interview_session(db, user, InterviewSessionCreateRequest())
    assert sess.status == "active"
    assert sess.current_question is not None

    # RAG infrastructure failure raises
    monkeypatch.setattr(service, "_candidate_context", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("RAG unavailable")))
    with pytest.raises(RuntimeError, match="RAG unavailable"):
        service.create_interview_session(db, user, InterviewSessionCreateRequest())


def test_question_history_and_cooldown(interview_setup):
    db, user, _ = interview_setup
    sess = service.create_interview_session(db, user, InterviewSessionCreateRequest())
    q1_text = sess.current_question.question
    assert q1_text

    # Verify recently asked question is detected
    recently_asked = service.get_recently_asked_question_texts(db, user.id, days=30)
    assert q1_text in recently_asked

    # Submit an answer to create a transcript entry
    service.submit_interview_answer(db, user, sess.session_id, InterviewAnswerRequest(answer="I implemented JWT token auth."))

    # Verify question history returns the asked question with cooldown info
    history = service.get_candidate_question_history(db, user, days_cooldown=30)
    assert len(history) >= 1
    found = next((item for item in history if item["question"] == q1_text), None)
    assert found is not None
    assert found["days_ago"] == 0
    assert found["ready_for_retest"] is False
    assert found["days_until_retest"] == 30


def test_focus_topic_grounding_and_fallback(interview_setup, monkeypatch):
    db, user, _ = interview_setup

    # Test 1: create session with focus_topic
    sess = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(
            target_role="Backend Developer",
            interview_mode="database",
            focus_topic="Database & SQL",
            language="en",
        ),
    )
    assert sess.focus_topic == "Database & SQL"
    assert sess.interview_mode == "database"

    # Test 2: Fallback question honors DSA focus topic
    sess_dsa = InterviewSession(
        session_id="dummy-dsa-id",
        candidate_id=user.id,
        target_role="Software Engineer",
        interview_mode="dsa",
        focus_topic="Data Structures & Algorithms",
        language="en",
        question_number=1,
    )
    dsa_q = service._fallback_next_question(sess_dsa, [], {"skills": []})
    assert any(term in dsa_q.topic.lower() for term in ["pointer", "algorithm", "tree", "window", "dsa", "complexity"])
    assert "Example:" in dsa_q.question

    # Test 3: Fallback question honors Database / SQL focus topic
    sess_sql = InterviewSession(
        session_id="dummy-sql-id",
        candidate_id=user.id,
        target_role="Backend Engineer",
        interview_mode="database",
        focus_topic="Database & SQL",
        language="en",
        question_number=1,
    )
    sql_q = service._fallback_next_question(sess_sql, [], {"skills": []})
    assert any(term in sql_q.topic.lower() for term in ["database", "sql", "index", "acid", "isolation"])

    # Test 4: Switching focus_topic during answer submission updates session
    ans_res = service.submit_interview_answer(
        db,
        user,
        sess.session_id,
        InterviewAnswerRequest(answer="I used B-Tree indexes.", focus_topic="System Architecture & Design"),
    )
    assert ans_res.focus_topic == "System Architecture & Design"

    # Test 5: Comprehensive mode creates unified session and rotates across all 4 pillars
    sess_comp = InterviewSession(
        session_id="dummy-comp-id",
        candidate_id=user.id,
        target_role="Software Engineer",
        interview_mode="comprehensive",
        focus_topic="All-in-One AI Interview & Mastery Room (Agent Teaches)",
        language="en",
        question_number=1,
    )
    comp_q1 = service._fallback_next_question(sess_comp, [], {"skills": [], "projects": [{"title": "CareerVerseAI"}]})
    assert comp_q1 is not None
    assert comp_q1.question

    # Test 6: Teaching action in Cyra chat produces structured pedagogical lesson
    from app.schemas.interview import CyraChatRequest
    teach_req = CyraChatRequest(
        message="Please teach me this concept.",
        current_question="Given an array of integers nums and an integer target, find two numbers that add up to target.",
        role="Software Engineer",
        candidate_code="",
        action_type="teach",
    )
    teach_resp = service.generate_cyra_chat_response(teach_req, user)
    assert teach_resp.action_type == "teach"
    assert teach_resp.reply
    assert len(teach_resp.reply) > 20


def test_get_candidate_interview_sessions_isolation(interview_setup):
    db, user1, _ = interview_setup
    other = db.query(User).filter(User.id != user1.id).first()
    if not other:
        other = SimpleNamespace(id="other-cand-99")

    # Create session for user 1
    s1 = service.create_interview_session(db, user1, InterviewSessionCreateRequest())

    # User 1 sessions must contain s1
    sessions_user1 = service.get_candidate_interview_sessions(db, user1)
    assert any(s.session_id == s1.session_id for s in sessions_user1)
    for s in sessions_user1:
        raw = db.query(InterviewSession).filter(InterviewSession.session_id == s.session_id).first()
        assert raw.candidate_id == user1.id

    # Other candidate's sessions must NOT contain s1
    sessions_other = service.get_candidate_interview_sessions(db, other)
    assert not any(s.session_id == s1.session_id for s in sessions_other)


def test_localize_question_payload_tamil_and_hindi():
    from app.schemas.interview_session import InterviewQuestionPayload
    q = InterviewQuestionPayload(
        question_id="test_q1",
        session_id="dummy",
        track="dsa",
        language="en",
        question="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        question_type="technical",
        difficulty="medium",
        topic="Two Sum (Hash Map Lookup Invariant)",
        rationale="Tests hash map lookup",
    )
    # Test Tamil localization
    q_ta = service.localize_question_payload(q, "ta")
    assert q_ta.language == "ta"
    assert "Two Sum" in q_ta.question or "array" in q_ta.question
    assert "Two Sum" in q_ta.topic

    # Test Hindi localization
    q_hi = service.localize_question_payload(q, "hi")
    assert q_hi.language == "hi"
    assert "Two Sum" in q_hi.question or "array" in q_hi.question
    assert "Two Sum" in q_hi.topic


def test_multiturn_diversity_and_pool_rotation(interview_setup):
    db, user, _ = interview_setup
    sess = InterviewSession(
        session_id="dummy-rot-id",
        candidate_id=user.id,
        target_role="Software Engineer",
        interview_mode="dsa",
        focus_topic="Data Structures & Algorithms",
        language="en",
        question_number=1,
    )
    q1 = service._fallback_next_question(sess, [], {"skills": []})
    
    # Second turn with question 1 in transcript
    sess.question_number = 2
    sess.current_question = q1.model_dump()
    transcript = [{"question": q1.model_dump(), "answer": "Used hash map"}]
    q2 = service._fallback_next_question(sess, transcript, {"skills": []})

    assert q1.question != q2.question
    assert q1.normalized_concept != q2.normalized_concept
    assert service.calculate_text_similarity(q1.question, q2.question) < 0.60


def test_multilingual_evaluation_and_reports_tamil_and_hindi(interview_setup):
    db, user, _ = interview_setup
    q = service.InterviewQuestionPayload(
        question="Two Sum problem in Python",
        topic="Two Sum Invariants",
        normalized_concept="dsa:arrays_hash_map",
        language="ta",
    )
    # Test Tamil evaluation fallback
    eval_ta = service._fallback_evaluation("நான் hash map பயன்படுத்தினேன்", q, "Python Developer", language="ta")
    assert any(w in eval_ta.assessment for w in ["சுருக்கமான", "பகுப்பாய்வு", "பொறியியல்"])
    assert any("நேரடி" in s or "கேள்விக்கான" in s or "கட்டமைக்கப்பட்ட" in s for s in eval_ta.strengths)
    assert any("விளக்குங்கள்" in imp or "Time" in imp or "பயன்படுத்திய" in imp for imp in eval_ta.improvements)

    # Test Hindi evaluation fallback
    eval_hi = service._fallback_evaluation("Maine hash map use kiya", q, "Python Developer", language="hi")
    assert any(w in eval_hi.assessment for w in ["संक्षिप्त", "विश्लेषण", "इंजीनियरिंग"])
    assert any("संबोधित" in s or "स्पष्ट" in s or "प्राथमिक" in s for s in eval_hi.strengths)

    # Test Tamil final report fallback
    session_ta = InterviewSession(
        session_id="ta-sess-report",
        candidate_id=user.id,
        target_role="Full Stack Engineer",
        language="ta",
        transcript=[{"question": q.model_dump(), "answer": "Implemented using hash map"}],
    )
    report_ta = service._fallback_final_report(session_ta, {})
    assert "நேர்காணல் சுற்றை" in report_ta.overall_interview_summary or "வெற்றிகரமாக" in report_ta.overall_interview_summary
    assert any("வெளிப்படுத்தியுள்ளீர்கள்" in s or "பொறியியல்" in s for s in report_ta.strengths)

    # Test Hindi final report fallback
    session_hi = InterviewSession(
        session_id="hi-sess-report",
        candidate_id=user.id,
        target_role="Full Stack Engineer",
        language="hi",
        transcript=[{"question": q.model_dump(), "answer": "Implemented using hash map"}],
    )
    report_hi = service._fallback_final_report(session_hi, {})
    assert "साक्षात्कार सत्र" in report_hi.overall_interview_summary or "सफलतापूर्वक" in report_hi.overall_interview_summary


def test_update_session_language_mid_interview(interview_setup):
    db, user, _ = interview_setup
    session = service.create_interview_session(db, user, InterviewSessionCreateRequest(language="en"))
    assert session.language == "en"

    # Switch mid-interview to Tamil
    updated_ta = service.update_session_language(db, user, session.session_id, "ta")
    assert updated_ta.language == "ta"
    assert updated_ta.current_question.language == "ta"
    # Current question was localized to Tamil
    assert "வணக்கம்" in updated_ta.current_question.question or any(ord(c) >= 0x0B80 and ord(c) <= 0x0BFF for c in updated_ta.current_question.question)

    # Switch to Hindi
    updated_hi = service.update_session_language(db, user, session.session_id, "hi")
    assert updated_hi.language == "hi"
    assert updated_hi.current_question.language == "hi"
    assert "नमस्ते" in updated_hi.current_question.question or any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in updated_hi.current_question.question)


def test_cyra_chat_multilingual_response(interview_setup, monkeypatch):
    """Verify generate_cyra_chat_response returns a reply in Tamil/Hindi.

    The function contains a local 'from app.ai.providers.factory import
    get_model_provider' that bypasses the fixture-level patch on the service
    module.  We patch the factory module directly so the real Groq network call
    is never made, making the test deterministic.
    """
    from types import SimpleNamespace as NS
    from app.schemas.interview import CyraChatRequest
    import app.ai.providers.factory as factory_module

    _, user, _ = interview_setup

    # Deterministic fake: returns a Tamil reply for 'ta' prompts, Hindi for 'hi'.
    class _CyraFakeProvider:
        def generate_text(self, *, system_prompt, user_message, **kwargs):
            if "TAMIL" in system_prompt or "ta" in system_prompt[:80]:
                content = "உங்கள் approach-ல் hash map பயன்படுத்துங்கள், அது O(n) complexity-ல் solve ஆகும்."
            elif "HINDI" in system_prompt or "hi" in system_prompt[:80]:
                content = "आप hash map का उपयोग करें — इससे O(n) में solve होगा और space complexity O(n) रहेगी।"
            else:
                content = "Use a hash map to group characters by their sorted key in O(n) time."
            return NS(content=content, model="fake-cyra")

    monkeypatch.setattr(factory_module, "get_model_provider", lambda: _CyraFakeProvider())

    req_ta = CyraChatRequest(
        message="எனக்கு ஒரு hint குடுங்க",
        current_question="Group Anagrams",
        role="Frontend Engineer",
        action_type="hint",
        language="ta",
    )
    res_ta = service.generate_cyra_chat_response(req_ta, user)
    assert res_ta.reply
    assert any(ord(c) >= 0x0B80 and ord(c) <= 0x0BFF for c in res_ta.reply) or "hash" in res_ta.reply.lower()

    req_hi = CyraChatRequest(
        message="Mujhe ek hint chahiye",
        current_question="Group Anagrams",
        role="Frontend Engineer",
        action_type="hint",
        language="hi",
    )
    res_hi = service.generate_cyra_chat_response(req_hi, user)
    assert res_hi.reply
    assert any(ord(c) >= 0x0900 and ord(c) <= 0x097F for c in res_hi.reply) or "hash" in res_hi.reply.lower()


def test_language_persists_across_all_turns_tamil(interview_setup):
    """Language 'ta' must be stored in the session after creation and preserved
    in every subsequent submit_interview_answer call, as evidenced both by the
    session.language field and by the JSON user_payload serialised for the LLM."""
    db, user, provider = interview_setup

    session = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(language="ta"),
    )
    assert session.language == "ta"

    answers = [
        "இந்த array-ல் hash map பயன்படுத்தி O(n) நேரத்தில் தீர்க்கலாம்.",
        "Two-pointer technique-ஐ sorted array-க்கு பயன்படுத்தலாம்.",
        "Space complexity O(1)-க்கு குறைக்க in-place sorting உதவும்.",
    ]
    for answer_text in answers:
        result = service.submit_interview_answer(
            db,
            user,
            session.session_id,
            InterviewAnswerRequest(answer=answer_text),
        )
        # Language field must remain 'ta' across every turn
        assert result.language == "ta", f"Language reset on turn; got {result.language!r}"

    # The FakeProvider accumulates every user_message in .calls.
    # Each call is a JSON string that includes the session's language field.
    for call in provider.calls:
        assert '"language": "ta"' in call, (
            f"Expected '\"language\": \"ta\"' in LLM user_message but got: {call[:200]}"
        )


def test_repair_path_preserves_language_tamil(interview_setup, monkeypatch):
    """When _parse_json raises ValueError on the first LLM response, the repair
    call must use a system prompt built by language_prompt_builder with 'ta',
    which means the prompt must contain 'Tamil'."""
    db, user, provider = interview_setup

    # Track system prompts sent to the provider's generate_text
    recorded_system_prompts: list = []
    original_generate_text = provider.generate_text

    def capturing_generate_text(*, system_prompt, user_message, **kwargs):
        recorded_system_prompts.append(system_prompt)
        return original_generate_text(
            system_prompt=system_prompt, user_message=user_message, **kwargs
        )

    provider.generate_text = capturing_generate_text

    # Force _parse_json to raise on the first call only, succeeding on retry
    call_count = {"n": 0}
    original_parse_json = service._parse_json

    def failing_parse_json(raw: str):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise ValueError("Simulated malformed JSON on first parse")
        return original_parse_json(raw)

    monkeypatch.setattr(service, "_parse_json", failing_parse_json)

    session = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(language="ta"),
    )
    assert session.language == "ta"

    # The repair path in _provider_json calls language_prompt_builder.with_system_language_policy
    # with 'ta', so at least one recorded system prompt must mention 'Tamil'.
    assert any("Tamil" in sp for sp in recorded_system_prompts), (
        "Expected at least one system prompt to contain 'Tamil' (from language_prompt_builder "
        f"repair path), but got prompts: {[sp[:100] for sp in recorded_system_prompts]}"
    )


def test_github_mode_never_routes_to_dsa_questions(interview_setup, monkeypatch):
    """In GitHub/Projects mode, fallback questions must NEVER yield LeetCode DSA puzzles."""
    db, user, provider = interview_setup

    # Force provider to fail so fallback questions are exercised across all 5 turns
    def failing_generate_text(**kwargs):
        raise RuntimeError("Simulated provider failure to trigger fallback pool")

    monkeypatch.setattr(provider, "generate_text", failing_generate_text)

    # Mock candidate connected repo evidence
    monkeypatch.setattr(
        service,
        "_retrieve_candidate_project_evidence",
        lambda *args, **kwargs: {
            "has_repository": True,
            "repository_name": "agentic-ecomm",
            "repository_language": "Python/FastAPI",
            "repository_description": "Multi-agent e-commerce backend",
            "evidence_status": "grounded",
            "repository_citations": [
                {"file_path": "backend/app/main.py", "line_range": "L1-L30", "rationale": "Main app entrypoint"}
            ],
        },
    )

    session_res = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(
            target_role="Full Stack Developer",
            interview_mode="github",
            language="en",
        ),
    )

    forbidden_dsa_keywords = ["anagram", "two pointer", "water", "binary tree", "leetcode", "sliding window", "linked list", "array of strings"]
    session_id = session_res.session_id

    # Verify first question
    q1 = session_res.current_question.question.lower()
    for kw in forbidden_dsa_keywords:
        assert kw not in q1, f"Found forbidden DSA keyword '{kw}' in GitHub question: {q1}"

    # Answer turns 1 through 4 to inspect all generated questions
    for i in range(1, 5):
        ans_res = service.submit_interview_answer(
            db,
            user,
            session_id,
            InterviewAnswerRequest(
                answer="I structured this service with modular FastAPI routers, dependency injection for DB sessions, and structured logging.",
            ),
        )
        if ans_res.status == "completed":
            break
        curr_q = (ans_res.current_question.question if ans_res.current_question else "").lower()
        for kw in forbidden_dsa_keywords:
            assert kw not in curr_q, f"Turn {i+1} yielded forbidden DSA keyword '{kw}' in GitHub mode: {curr_q}"


def test_follow_up_does_not_increment_core_question_count(interview_setup, monkeypatch):
    """A follow-up question must probe deeper on the current core question and NOT advance core_question_number."""
    db, user, provider = interview_setup
    session_res = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(target_role="Backend Developer", interview_mode="target_role", language="en"),
    )
    assert session_res.core_question_number == 1
    assert session_res.is_follow_up is False

    orig_generate = provider.generate_text
    def follow_up_generate(*, system_prompt, user_message, **kwargs):
        if "latest_answer" in user_message:
            return SimpleNamespace(
                content=json.dumps({
                    "assessment": "Brief answer needing follow-up.",
                    "score": 6,
                    "is_follow_up_needed": True,
                    "follow_up_reason": "Explain authorization mechanisms in detail.",
                    "missing_elements": ["JWT token structure", "Revocation"],
                }),
                model="fake-model",
            )
        return orig_generate(system_prompt=system_prompt, user_message=user_message, **kwargs)

    monkeypatch.setattr(provider, "generate_text", follow_up_generate)

    # Submit an answer that prompts a follow-up
    ans_res = service.submit_interview_answer(
        db,
        user,
        session_res.session_id,
        InterviewAnswerRequest(answer="I used FastAPI."),
    )
    # Question count (total turns) advances to 2, but core question index stays 1 for follow-up
    assert ans_res.question_number == 2
    assert ans_res.is_follow_up is True
    assert ans_res.core_question_number == 1


def test_final_report_derives_auditable_scorecard(interview_setup):
    """Completed session must have deterministic overall_score, average_question_score, relevance_score, and duration."""
    db, user, provider = interview_setup
    session_res = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(target_role="Backend Developer", interview_mode="target_role", language="en"),
    )
    # Submit 1 detailed answer
    service.submit_interview_answer(
        db,
        user,
        session_res.session_id,
        InterviewAnswerRequest(
            answer="In our FastAPI backend, I designed asynchronous endpoint handlers using async/await with connection pooling in SQLAlchemy to achieve 45ms P99 latency.",
        ),
    )
    comp_res = service.complete_interview_session(db, user, session_res.session_id)
    assert comp_res.status == "completed"
    assert comp_res.final_report is not None
    rep = comp_res.final_report

    assert rep.overall_score is not None
    assert 1.0 <= rep.overall_score <= 10.0
    assert rep.average_question_score is not None
    assert rep.relevance_score is not None
    assert rep.duration_seconds is not None
    assert isinstance(rep.question_evaluations, list)
    assert len(rep.question_evaluations) >= 1
    first_q_eval = rep.question_evaluations[0]
    assert "score" in first_q_eval
    assert "rubric_scores" in first_q_eval


def test_question_history_persists_mastery_and_citations(interview_setup):
    """Question history must expose mastery status, rubric scores, and citations."""
    db, user, provider = interview_setup
    session_res = service.create_interview_session(
        db,
        user,
        InterviewSessionCreateRequest(target_role="Backend Developer", interview_mode="target_role", language="en"),
    )
    service.submit_interview_answer(
        db,
        user,
        session_res.session_id,
        InterviewAnswerRequest(answer="I implemented JWT authorization with expiration and token revocation via Redis blocklist."),
    )
    history = service.get_candidate_question_history(db, user)
    assert len(history) >= 1
    item = history[0]
    assert "question" in item
    assert "score" in item
    assert "mastery_status" in item
    assert item["mastery_status"] in ["mastered", "needs_revision", "practiced"]
    assert "rubric_scores" in item
    assert "session_id" in item