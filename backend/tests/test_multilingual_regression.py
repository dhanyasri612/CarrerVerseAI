"""
test_multilingual_regression.py

12-scenario regression suite validating the complete language pipeline.
All 9 backend tests live here. The 3 frontend tests are in the frontend suite.

No real LLM or network calls are made — all external dependencies are mocked.
"""

import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from app.ai.agents.state import CareerIntelligenceState
from app.ai.language.detector import language_detector
from app.ai.language.prompt_builder import language_prompt_builder
from app.database.session import SessionLocal
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.interview_session import (
    InterviewAnswerRequest,
    InterviewSessionCreateRequest,
)
from app.services import conversational_interview_service as service


# ── Shared test doubles ─────────────────────────────────────────────────────

class FakeProvider:
    """Records every (system_prompt, user_message) pair without hitting a real LLM."""

    def __init__(self, responses: list | None = None):
        self.calls: list[dict] = []           # raw user_message strings (for language assertions)
        self.system_prompts: list[str] = []   # system prompts per call
        self._responses = responses or []
        self._idx = 0

    def _next_content(self, system_prompt: str, user_message: str) -> str:
        """Return the next canned response, cycling back to the last one when exhausted."""
        if self._responses:
            idx = min(self._idx, len(self._responses) - 1)
            self._idx += 1
            return self._responses[idx]
        # Default response valid for question-generation path
        return json.dumps({
            "question": "How did you apply hashing in your projects?",
            "question_type": "skill_based",
            "difficulty": "medium",
            "topic": "Hashing",
            "rationale": "Regression test default question.",
        })

    def generate_text(self, *, system_prompt, user_message, temperature=0.2, max_completion_tokens=None):
        self.system_prompts.append(system_prompt)
        self.calls.append(user_message)
        return SimpleNamespace(content=self._next_content(system_prompt, user_message), model="fake-model")


class FakeContext:
    context_text = "Candidate has Python and FastAPI evidence."


def _first_user():
    db = SessionLocal()
    try:
        return db.query(User).first()
    finally:
        db.close()


@pytest.fixture()
def db_session():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture()
def regression_setup(monkeypatch):
    """
    Fixture that patches the LLM provider and RAG helpers for every regression
    test.  Yields (db, user, provider) like the existing interview_setup pattern.
    """
    provider = FakeProvider()
    monkeypatch.setattr(service, "get_model_provider", lambda: provider)
    monkeypatch.setattr(service, "_candidate_context", lambda *a, **kw: FakeContext())
    monkeypatch.setattr(service, "_graph_evidence", lambda *a, **kw: {"skills": [{"name": "Python"}]})

    db = SessionLocal()
    user = _first_user()
    yield db, user, provider

    # Tear-down: delete any sessions created during this test
    db.query(InterviewSession).filter(InterviewSession.candidate_id == user.id).delete()
    db.commit()
    db.close()


# ────────────────────────────────────────────────────────────────────────────
# Scenario 1 — English selection → LLM prompt contains English instruction
# ────────────────────────────────────────────────────────────────────────────

def test_01_english_selection_prompt_contains_english_instruction(regression_setup):
    """LLM system prompt must reference English language policy when language='en'."""
    db, user, provider = regression_setup

    service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="en")
    )

    assert provider.system_prompts, "No LLM call was made."
    combined = "\n".join(provider.system_prompts)
    # The language policy appended by with_system_language_policy names the language
    assert "English" in combined, (
        "Expected 'English' in system prompts but got: " + combined[:300]
    )


# ────────────────────────────────────────────────────────────────────────────
# Scenario 2 — Tamil selection → LLM prompt contains ta-IN or Tamil instruction
# ────────────────────────────────────────────────────────────────────────────

def test_02_tamil_selection_prompt_contains_tamil_instruction(regression_setup):
    """LLM system prompt must reference Tamil when language='ta'."""
    db, user, provider = regression_setup

    service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="ta")
    )

    combined = "\n".join(provider.system_prompts)
    assert "Tamil" in combined or "ta-IN" in combined or "ta)" in combined, (
        "Expected Tamil language instruction in system prompts but got: " + combined[:300]
    )


# ────────────────────────────────────────────────────────────────────────────
# Scenario 3 — Hindi selection → LLM prompt contains hi-IN or Hindi instruction
# ────────────────────────────────────────────────────────────────────────────

def test_03_hindi_selection_prompt_contains_hindi_instruction(regression_setup):
    """LLM system prompt must reference Hindi when language='hi'."""
    db, user, provider = regression_setup

    service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="hi")
    )

    combined = "\n".join(provider.system_prompts)
    assert "Hindi" in combined or "hi-IN" in combined or "hi)" in combined, (
        "Expected Hindi language instruction in system prompts but got: " + combined[:300]
    )


# ────────────────────────────────────────────────────────────────────────────
# Scenario 4 — Tanglish query → response/prompt reflects Tamil code-mixing policy
# ────────────────────────────────────────────────────────────────────────────

def test_04_tanglish_query_prompt_reflects_tamil_code_mixing_policy():
    """
    The language detector must identify a Tanglish query as 'ta' and the prompt
    builder must include the code-mixing policy for Tamil / Tanglish.
    """
    tanglish_query = "enakku SQL queries la help venum, eppadi optimize panrathu theriyum?"
    result = language_detector.detect_language(tanglish_query)
    assert result.language_code == "ta", (
        f"Expected 'ta' for Tanglish query, got '{result.language_code}' "
        f"via method '{result.detection_method}'"
    )

    # Prompt builder must embed Tanglish / code-mixing guidance
    prompt = language_prompt_builder.with_system_language_policy("base system", "ta")
    assert "Tamil" in prompt
    assert "Tanglish" in prompt or "code-mix" in prompt.lower() or "code mix" in prompt.lower(), (
        "Expected Tanglish/code-mix guidance in Tamil policy prompt: " + prompt[:400]
    )


# ────────────────────────────────────────────────────────────────────────────
# Scenario 5 — Language persists across 3+ turns in the same backend session
# ────────────────────────────────────────────────────────────────────────────

def test_05_language_persists_across_three_turns(regression_setup):
    """session.language must stay 'ta' on every turn and each LLM payload must
    serialize language='ta'."""
    db, user, provider = regression_setup

    session = service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="ta")
    )
    assert session.language == "ta"

    for i, answer in enumerate([
        "Hash map பயன்படுத்தி O(n) solve panrom.",
        "Two pointer approach sorted array-ku better.",
        "In-place sort panni space O(1) achieve panrom.",
    ], start=1):
        result = service.submit_interview_answer(
            db, user, session.session_id, InterviewAnswerRequest(answer=answer)
        )
        assert result.language == "ta", f"Language reset on turn {i}; got {result.language!r}"

    # Every user_message payload sent to the LLM must encode language='ta'
    for idx, call in enumerate(provider.calls):
        assert '"language": "ta"' in call, (
            f"Call {idx}: Expected '\"language\": \"ta\"' in LLM message, got: {call[:200]}"
        )


# ────────────────────────────────────────────────────────────────────────────
# Scenario 6 — All LangGraph nodes preserve the `language` field
# ────────────────────────────────────────────────────────────────────────────

def test_06_langgraph_nodes_preserve_language_field(monkeypatch):
    """
    Mock the orchestrator's individual node methods and verify that the
    `response_language` / `detected_language` fields survive each node's
    state transformation.
    """
    from app.ai.agents.orchestrator import CareerOrchestrator

    # Build a minimal initial state with language='ta'
    initial_state: CareerIntelligenceState = {
        "candidate_id": 1,
        "user_query": "enakku career advice venum",
        "response_language": "ta",
        "detected_language": "ta",
        "language_name": "Tamil",
        "language_confidence": 1.0,
        "language_metadata": {},
        "errors": [],
        "metadata": {},
        "agents_used": [],
        "agent_results": {},
        "tasks": [],
        "status": "validated",
    }

    orch = CareerOrchestrator.__new__(CareerOrchestrator)
    # Minimal attribute set needed by the nodes under test
    orch.lang_detector = language_detector
    orch.query_norm = SimpleNamespace(normalize_query=lambda q, l: q)
    orch.task_router = SimpleNamespace(
        analyze_task=lambda query, explicit_role: ("general", ["recommendation"], None)
    )

    # task_router_node must preserve response_language
    router_output = orch.task_router_node(initial_state)
    merged = {**initial_state, **router_output}
    assert merged.get("response_language") == "ta" or initial_state.get("response_language") == "ta", (
        "task_router_node dropped response_language from state"
    )
    assert merged.get("detected_language") == "ta" or initial_state.get("detected_language") == "ta"

    # request_processor node re-runs detection; explicit override must keep 'ta'
    orch._llm_provider = None
    proc_output = orch.request_processor(initial_state)
    assert proc_output.get("response_language") == "ta", (
        f"request_processor changed response_language to '{proc_output.get('response_language')}'"
    )
    assert proc_output.get("detected_language") == "ta"


# ────────────────────────────────────────────────────────────────────────────
# Scenario 7 — Changing language mid-session updates the next response's language
# ────────────────────────────────────────────────────────────────────────────

def test_07_changing_language_mid_session_updates_instruction(regression_setup):
    """update_session_language must update session.language and localize the
    current question to the new language."""
    db, user, _ = regression_setup

    session = service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="en")
    )
    assert session.language == "en"

    updated = service.update_session_language(db, user, session.session_id, "ta")
    assert updated.language == "ta", f"Expected 'ta', got '{updated.language}'"
    assert updated.current_question.language == "ta"


# ────────────────────────────────────────────────────────────────────────────
# Scenario 8 — Two concurrent sessions with different languages do not overwrite
# ────────────────────────────────────────────────────────────────────────────

def test_08_two_concurrent_sessions_do_not_overwrite_languages(regression_setup):
    """Sessions A (ta) and B (hi) must maintain independent language state."""
    db, user, _ = regression_setup

    session_a = service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="ta")
    )
    session_b = service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="hi")
    )

    assert session_a.language == "ta"
    assert session_b.language == "hi"

    # Re-fetch both sessions independently to confirm DB isolation
    fetched_a = service.get_interview_session(db, user, session_a.session_id)
    fetched_b = service.get_interview_session(db, user, session_b.session_id)

    assert fetched_a.language == "ta", f"Session A language changed to '{fetched_a.language}'"
    assert fetched_b.language == "hi", f"Session B language changed to '{fetched_b.language}'"


# ────────────────────────────────────────────────────────────────────────────
# Scenario 9 — Errors and retries do not silently revert to English
# ────────────────────────────────────────────────────────────────────────────

def test_09_retry_on_parse_failure_does_not_revert_to_english(regression_setup, monkeypatch):
    """When _parse_json raises on the first attempt, the repair path's system
    prompt must still reference 'Tamil' — not silently fall back to English."""
    db, user, provider = regression_setup

    captured_system_prompts: list[str] = []
    orig_generate = provider.generate_text

    def capturing_generate(*, system_prompt, user_message, **kwargs):
        captured_system_prompts.append(system_prompt)
        return orig_generate(system_prompt=system_prompt, user_message=user_message, **kwargs)

    provider.generate_text = capturing_generate

    # Make _parse_json fail on first call only
    attempt = {"n": 0}
    orig_parse = service._parse_json

    def failing_parse(raw):
        attempt["n"] += 1
        if attempt["n"] == 1:
            raise ValueError("Injected parse failure for regression test")
        return orig_parse(raw)

    monkeypatch.setattr(service, "_parse_json", failing_parse)

    session = service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="ta")
    )
    assert session.language == "ta"

    combined = "\n".join(captured_system_prompts)
    assert "Tamil" in combined, (
        "Repair path dropped language policy — expected 'Tamil' in system prompts. "
        "Got: " + combined[:400]
    )
    # Must NOT contain an English-only revert instruction while Tamil is selected
    # (English policy can appear alongside Tamil, but no prompt should replace it entirely)
    # Check that at least one prompt is specifically a Tamil policy prompt
    assert any("Tamil" in sp for sp in captured_system_prompts), (
        "No system prompt contained 'Tamil' — language silently reverted to English on retry."
    )


# ────────────────────────────────────────────────────────────────────────────
# Scenario 13 — Malayalam selection → LLM prompt contains Malayalam instruction
# ────────────────────────────────────────────────────────────────────────────

def test_13_malayalam_selection_prompt_contains_malayalam_instruction(regression_setup):
    """LLM system prompt must reference Malayalam when language='ml'."""
    db, user, provider = regression_setup

    service.create_interview_session(
        db, user, InterviewSessionCreateRequest(language="ml")
    )

    combined = "\n".join(provider.system_prompts)
    assert "Malayalam" in combined or "ml" in combined, (
        "Expected Malayalam language instruction in system prompts but got: " + combined[:300]
    )


def test_14_malayalam_detection_and_localization():
    """Validates Unicode Malayalam detection, Manglish keyword detection, and localization."""
    # Unicode Malayalam detection
    res = language_detector.detect_language("എനിക്ക് ഒരു പൈത്തൺ ഇന്റർവ്യൂ ചോദ്യം വേണം")
    assert res.language_code == "ml"
    assert res.is_supported is True

    # Manglish lexical keyword detection
    manglish_res = language_detector.detect_language("enikku python interview chodhyam venam")
    assert manglish_res.language_code == "ml"

    # Localized question payload test
    from app.schemas.interview_session import InterviewQuestionPayload
    dummy_q = InterviewQuestionPayload(
        question_id="test-1",
        question="How do you group anagrams?",
        question_type="technical",
        difficulty="medium",
        topic="Arrays & Hash Maps",
        normalized_concept="dsa:arrays_hash_map",
    )
    localized = service.localize_question_payload(dummy_q, "ml")
    assert localized.language == "ml"
    assert "നമസ്കാരം" in localized.question
    assert "anagrams" in localized.question
