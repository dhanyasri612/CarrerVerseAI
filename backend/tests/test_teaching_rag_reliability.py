"""
Comprehensive RAG Reliability & Evidence Sufficiency Test Suite for CareerVerse AI Teaching Room.
Validates:
1. ChromaDB PyO3/Rust panic handling and safe ephemeral fallback.
2. Relevant vs. irrelevant evidence retrieval.
3. Ambiguous question detection and targeted clarification.
4. Questions absent from knowledge base (anti-hallucination & zero fake citations).
5. Section-aware bounded chunking and metadata preservation.
6. LLM provider failure graceful degradation.
7. Existing Teaching Room schema backwards-compatibility.
"""

from unittest.mock import MagicMock, patch
import pytest

from app.database.session import SessionLocal
from app.models.user import User
from app.ai.rag.evidence_gate import (
    is_ambiguous_query,
    extract_meaningful_keywords,
    evaluate_teaching_evidence_sufficiency,
)
from app.ai.rag.technical_sources import (
    _SectionAwareTextParser,
    chunk_sections,
    _default_collection,
    search_fresh_technical_sources,
    render_technical_sources_context,
)
from app.services.teaching_service import (
    chat_with_teaching_mentor,
    interact_with_teaching_lesson,
    evaluate_and_teach,
)
from app.schemas.teaching import (
    TeachingChatRequest,
    TeachingChatResponse,
    TeachingInteractionRequest,
    TeachingInteractionResponse,
    TeachingEvaluationRequest,
    TeachingEvaluationResponse,
)


@pytest.fixture
def test_db_user():
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        user = User(
            id=1,
            email="dhanyasri@test.com",
            username="dhanyasrik",
            full_name="Dhanyasri K",
            hashed_password="hashedpassword123",
            is_active=True,
        )
    yield db, user
    db.close()


# ── TEST 1: CHROMADB INITIALIZATION FAILURE & SAFE FALLBACK ──────────────────
def test_chromadb_initialization_panic_and_safe_fallback():
    """
    Simulates a Rust PyO3 panic in chromadb.PersistentClient.
    Verifies that _default_collection safely falls back to in-memory Client
    without crashing or pretending retrieval succeeded.
    """
    _default_collection.cache_clear()

    # Create a dummy BaseException with PanicException in its type name
    class PanicException(BaseException):
        pass

    with patch("chromadb.PersistentClient", side_effect=PanicException("range start index 10 out of range")):
        col = _default_collection()
        assert col is not None
        # Must be operational ephemeral collection
        assert hasattr(col, "name")
        assert hasattr(col, "count")
        # An unpopulated collection reports count 0 and does not pretend it has fresh data
        res = search_fresh_technical_sources("Python asyncio", collection=col)
        assert res["status"] in ("not_refreshed", "unavailable", "stale")
        assert res["sources"] == []

    _default_collection.cache_clear()


# ── TEST 2: RELEVANT VS IRRELEVANT RETRIEVAL ──────────────────────────────────
def test_relevant_vs_irrelevant_retrieval():
    """
    Verifies that relevant technical topics produce sufficient grounding,
    whereas irrelevant/out-of-domain topics are marked as insufficient.
    """
    # Case A: Relevant topic with matching catalog entry
    relevant_result = evaluate_teaching_evidence_sufficiency(
        user_query="How does FastAPI dependency injection handle database sessions with yield?",
        target_topic="FastAPI",
        technical_sources=[],
        catalog_resources=[
            {
                "id": "res-fastapi-di",
                "title": "FastAPI Dependency Injection",
                "concepts_covered": ["FastAPI", "Dependency Injection", "Database Sessions"],
                "canonical_url": "https://fastapi.tiangolo.com/tutorial/dependencies/",
            }
        ],
    )
    assert relevant_result.is_sufficient is True
    assert relevant_result.status == "sufficient"
    assert relevant_result.grounding_type == "source_grounded"
    assert len(relevant_result.matched_sources) >= 1

    # Case B: Irrelevant topic with no matching concepts
    irrelevant_result = evaluate_teaching_evidence_sufficiency(
        user_query="How do astronauts perform space vehicle rendezvous in Martian orbit?",
        target_topic="Martian Orbital Transfer",
        technical_sources=[],
        catalog_resources=[],
    )
    assert irrelevant_result.is_sufficient is False
    assert irrelevant_result.status == "insufficient"
    assert irrelevant_result.grounding_type == "general_knowledge"
    assert irrelevant_result.matched_sources == []
    assert "not covered in your active course materials" in irrelevant_result.insufficient_evidence_notice


# ── TEST 3: AMBIGUOUS QUESTION HANDLING ───────────────────────────────────────
def test_ambiguous_question_handling(test_db_user):
    """
    Verifies that vague queries ('performance', 'how to optimize', 'code?')
    trigger a clarification request and NEVER hallucinate an ungrounded masterclass or fake citations.
    """
    db, user = test_db_user

    # Sub-test 3a: Detection helper
    is_ambig, msg = is_ambiguous_query("performance?")
    assert is_ambig is True
    assert "clarify" in msg.lower()

    is_ambig_2, msg_2 = is_ambiguous_query("how to optimize")
    assert is_ambig_2 is True

    # Contextual query with clear topic is NOT ambiguous
    is_ambig_3, _ = is_ambiguous_query("Why do we use return in two sum?", active_lesson_topic="Two Sum")
    assert is_ambig_3 is False

    # Sub-test 3b: Live chat response for ambiguous question
    req = TeachingChatRequest(
        mode="skill",
        target_id="General",
        message="performance?",
        is_assessment=False,
    )
    res = chat_with_teaching_mentor(db, user, req)
    assert res.evidence_sufficiency == "ambiguous"
    assert res.citations == []
    assert "clarify" in res.reply.lower() or "broad" in res.reply.lower()
    assert len(res.suggested_follow_ups) >= 2


# ── TEST 4: QUESTIONS ABSENT FROM KNOWLEDGE BASE ──────────────────────────────
def test_questions_absent_from_knowledge_base(test_db_user):
    """
    When the query is absent from the knowledge base (e.g. quantum computing):
    1. Returns evidence_sufficiency='insufficient'.
    2. Explicitly provides a course materials boundary notice.
    3. Citations list is strictly empty (NO fabricated URLs or docs).
    """
    db, user = test_db_user

    req = TeachingChatRequest(
        mode="skill",
        target_id="Quantum Computing",
        message="How do I build a quantum teleportation circuit using Qiskit?",
        is_assessment=False,
    )
    res = chat_with_teaching_mentor(db, user, req)
    assert res.evidence_sufficiency == "insufficient"
    assert res.citations == []  # Strictly verified: zero fabricated citations
    assert res.technical_source_status == "unsupported_topic"
    assert "Course Materials" in res.reply or "not covered" in res.reply.lower()


# ── TEST 5: SECTION-AWARE BOUNDED CHUNKING & METADATA ────────────────────────
def test_section_aware_bounded_chunking():
    """
    Verifies that HTML documentation is parsed into section blocks with preserved
    headings and split into bounded overlapping chunks under 1200 characters.
    """
    sample_html = """
    <html>
      <body>
        <h1>Asyncio Event Loop Invariants</h1>
        <p>Asyncio runs on a single OS thread using cooperative multitasking.</p>
        <p>Coroutines yield control explicitly using the await keyword.</p>
        <h2>Task Groups and Exception Handling</h2>
        <p>Python 3.11 introduced asyncio.TaskGroup which guarantees that all spawned tasks complete or cancel cleanly on error.</p>
      </body>
    </html>
    """
    parser = _SectionAwareTextParser()
    parser.feed(sample_html)
    sections = parser.get_sections()
    assert len(sections) >= 2
    headings = [s.heading for s in sections]
    assert any("Asyncio" in h for h in headings)
    assert any("Task Groups" in h for h in headings)

    chunks = chunk_sections(sections, chunk_size=300, overlap=50)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c.text) <= 300
        assert c.section_heading in headings


# ── TEST 6: CITATION VALIDITY & CITATION FORMATTING ──────────────────────────
def test_citation_validity_and_formatting():
    """
    Verifies that render_technical_sources_context includes section headings
    and produces clean markdown anchors.
    """
    search_result = {
        "status": "fresh",
        "sources": [
            {
                "id": "res-python-asyncio",
                "title": "Python Official Documentation",
                "section_heading": "Asyncio Coroutines & Event Loop",
                "source": "Python Software Foundation",
                "canonical_url": "https://docs.python.org/3/library/asyncio.html",
                "last_checked_at": "2026-10-19T10:00:00Z",
                "source_last_modified": "2026-10-15T08:00:00Z",
                "excerpt": "Asyncio uses an event loop to schedule cooperative coroutines.",
            }
        ],
    }
    rendered = render_technical_sources_context(search_result)
    assert "Python Official Documentation" in rendered
    assert "§ Asyncio Coroutines & Event Loop" in rendered
    assert "https://docs.python.org/3/library/asyncio.html" in rendered


# ── TEST 7: PROVIDER FAILURE GRACEFUL DEGRADATION ────────────────────────────
def test_provider_failure_graceful_degradation(test_db_user):
    """
    Verifies that when LLM provider throws an exception, the teaching mentor
    degrades gracefully without throwing an unhandled 500.
    """
    db, user = test_db_user

    req = TeachingChatRequest(
        mode="skill",
        target_id="React",
        lesson_id="skill-react-s3-l1-useeffect",
        message="What is the mental model for useEffect?",
        is_assessment=False,
    )

    with patch("app.ai.providers.factory.get_model_provider", side_effect=RuntimeError("Provider timed out")):
        res = chat_with_teaching_mentor(db, user, req)
        assert res is not None
        assert res.reply is not None
        assert len(res.reply) > 20
        assert res.teaching_mode == "skill"


# ── TEST 8: RESPONSE SCHEMA BACKWARDS COMPATIBILITY ──────────────────────────
def test_response_schema_backwards_compatibility(test_db_user):
    """
    Ensures that TeachingChatResponse and TeachingInteractionResponse preserve
    all expected legacy fields while adding evidence_sufficiency.
    """
    db, user = test_db_user

    # 1. Chat Response Schema Check
    chat_req = TeachingChatRequest(
        mode="skill",
        target_id="Python",
        message="Explain the GIL memory model",
        is_assessment=False,
    )
    chat_res = chat_with_teaching_mentor(db, user, chat_req)
    assert isinstance(chat_res, TeachingChatResponse)
    assert hasattr(chat_res, "reply")
    assert hasattr(chat_res, "citations")
    assert hasattr(chat_res, "evidence_sufficiency")
    assert chat_res.evidence_sufficiency in ("sufficient", "insufficient", "ambiguous")

    # 2. Lesson Interaction Schema Check
    interact_req = TeachingInteractionRequest(
        section_id="dsa",
        lesson_id="dsa-two-sum",
        action="hint",
    )
    interact_res = interact_with_teaching_lesson(db, user, interact_req)
    assert isinstance(interact_res, TeachingInteractionResponse)
    assert hasattr(interact_res, "teaching_message")
    assert hasattr(interact_res, "evidence_sufficiency")
    assert interact_res.evidence_sufficiency == "sufficient"
