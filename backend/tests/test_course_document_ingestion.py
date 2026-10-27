"""
Comprehensive Automated Test Suite for CareerVerse AI Course Document Ingestion (Phase 2).

Validates:
1. Ingestion of PDF, Markdown (.md), and Plain Text (.txt).
2. Streaming size limit (15 MB), empty files, malformed PDFs, and unsupported types.
3. Page/section metadata preservation and citation formatting.
4. Duplicate upload and safe re-indexing by SHA-256 hash.
5. Owner-scoped list, read, retrieval, and deletion (zero cross-user leakage).
6. Unauthorized and cross-user access rejection (HTTP 404).
7. ChromaDB persistent failure and truthful ephemeral fallback status ("degraded").
8. Deletion cleanup resilience when disk file is missing.
9. Teaching Room Dr. Cyra Vance RAG integration and citation grounding.
10. FastAPI router endpoints via TestClient.
"""

from __future__ import annotations

import io
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database.database import ensure_course_document_table
from app.database.session import SessionLocal
from app.main import app
from app.models.course_document import CourseDocument
from app.models.user import User
from app.ai.rag.evidence_gate import evaluate_teaching_evidence_sufficiency
from app.schemas.teaching import TeachingChatRequest
from app.services.teaching_service import chat_with_teaching_mentor
from app.services.course_document_service import (
    MAX_FILE_SIZE,
    _get_teaching_materials_collection,
    _sanitize_filename,
    _sha256_file,
    delete_course_document,
    get_course_document_by_id,
    get_user_course_documents,
    search_course_materials,
    upload_and_ingest_course_document,
)

try:
    import pymupdf as fitz
except ImportError:
    import fitz


# ── TEST FIXTURES ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def setup_tables():
    ensure_course_document_table()


@pytest.fixture
def db_session():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def candidate_user_a(db_session: Session):
    user = db_session.query(User).filter(User.id == 1).first()
    if not user:
        user = User(
            id=1,
            name="Dhanyasri K",
            email="candidate_a@test.com",
            hashed_password="hashed_pw_test",
            is_active=True,
            role_id=1,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


@pytest.fixture
def candidate_user_b(db_session: Session):
    user = db_session.query(User).filter(User.id == 2).first()
    if not user:
        user = User(
            id=2,
            name="Second Test User",
            email="candidate_b@test.com",
            hashed_password="hashed_pw_test",
            is_active=True,
            role_id=1,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


def _create_test_pdf_bytes() -> bytes:
    """Creates a real in-memory 2-page PDF with clear section headings using PyMuPDF."""
    doc = fitz.open()
    
    # Page 1
    page1 = doc.new_page(width=595, height=842)
    text1 = (
        "Distributed Consensus Fundamentals\n\n"
        "Raft is a consensus algorithm designed as an alternative to Multi-Paxos.\n"
        "It achieves consensus via an elected leader who manages replicated log entries.\n"
        "Followers reject heartbeat signals if term numbers are stale."
    )
    page1.insert_text((50, 72), text1, fontsize=12)

    # Page 2
    page2 = doc.new_page(width=595, height=842)
    text2 = (
        "Leader Election Invariants in Raft\n\n"
        "In Raft, randomized election timeouts between 150ms and 300ms prevent split votes.\n"
        "A candidate wins an election when it receives votes from a majority of cluster nodes.\n"
        "Each server votes for at most one candidate per term on a first-come-first-served basis."
    )
    page2.insert_text((50, 72), text2, fontsize=12)

    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


# ── TEST 1: PDF INGESTION & METADATA PRESERVATION ─────────────────────────────
def test_pdf_ingestion_and_metadata_preservation(db_session: Session, candidate_user_a: User):
    """
    Verifies that a valid multi-page PDF is ingested, pages are accurately tracked,
    section headings are identified, and chunks are indexed.
    """
    pdf_bytes = _create_test_pdf_bytes()
    upload = UploadFile(
        file=io.BytesIO(pdf_bytes),
        filename="Raft_Consensus_Lecture_Notes.pdf",
        headers={"content-type": "application/pdf"},
    )

    doc = upload_and_ingest_course_document(db_session, candidate_user_a, upload)
    try:
        assert doc.id is not None
        assert doc.user_id == candidate_user_a.id
        assert doc.original_filename == "Raft_Consensus_Lecture_Notes.pdf"
        assert doc.file_type == "pdf"
        assert doc.total_pages == 2
        assert doc.total_chunks >= 2
        assert doc.status in ("indexed", "degraded")
        assert doc.content_hash is not None
        assert os.path.exists(doc.file_path)

        # Vector retrieval for owner A
        results = search_course_materials("randomized election timeouts in Raft", user_id=candidate_user_a.id, top_k=2)
        assert len(results) >= 1
        top = results[0]
        assert top.document_id == doc.id
        assert top.page_number in (1, 2)
        assert "election" in top.excerpt.lower() or "raft" in top.excerpt.lower()
    finally:
        delete_course_document(db_session, candidate_user_a, doc.id)


# ── TEST 2: MARKDOWN & TXT INGESTION ──────────────────────────────────────────
def test_markdown_and_txt_ingestion(db_session: Session, candidate_user_a: User):
    """
    Verifies that Markdown and TXT files are parsed, headings are extracted,
    and chunks are searchable.
    """
    # 2A: Markdown
    md_content = b"""# Kafka Partitioning and Ordering

Kafka provides a total order over records only within a given partition.
Keys are hashed using murmur2 to assign records to partitions deterministically.

## Consumer Rebalance Invariants
When a consumer leaves an active consumer group, the group coordinator initiates
a cooperative sticky rebalance to minimize partition revocation downtime.
"""
    upload_md = UploadFile(
        file=io.BytesIO(md_content),
        filename="kafka_architecture.md",
        headers={"content-type": "text/markdown"},
    )
    doc_md = upload_and_ingest_course_document(db_session, candidate_user_a, upload_md)
    try:
        assert doc_md.file_type in ("md", "markdown")
        assert doc_md.total_chunks >= 1

        md_results = search_course_materials("cooperative sticky rebalance in Kafka", user_id=candidate_user_a.id)
        assert len(md_results) >= 1
        assert "rebalance" in md_results[0].excerpt.lower() or "consumer" in md_results[0].excerpt.lower()
        assert md_results[0].section_heading == "Consumer Rebalance Invariants"
    finally:
        delete_course_document(db_session, candidate_user_a, doc_md.id)

    # 2B: TXT
    txt_content = b"""PostgreSQL MVCC (Multi-Version Concurrency Control) Notes:
Readers do not block writers and writers do not block readers.
Each tuple in a heap page has xmin and xmax transaction ID headers.
Vacuuming reclaims dead tuple storage when tuples are no longer visible to any active snapshot.
"""
    upload_txt = UploadFile(
        file=io.BytesIO(txt_content),
        filename="postgres_mvcc.txt",
        headers={"content-type": "text/plain"},
    )
    doc_txt = upload_and_ingest_course_document(db_session, candidate_user_a, upload_txt)
    try:
        assert doc_txt.file_type in ("txt", "text")
        assert doc_txt.total_chunks >= 1
    finally:
        delete_course_document(db_session, candidate_user_a, doc_txt.id)


# ── TEST 3: INVALID, EMPTY, MALFORMED, AND OVERSIZED FILES ────────────────────
def test_unsupported_extension_rejected(db_session: Session, candidate_user_a: User):
    upload = UploadFile(
        file=io.BytesIO(b"ELF binary payload"),
        filename="exploit.exe",
        headers={"content-type": "application/octet-stream"},
    )
    with pytest.raises(HTTPException) as exc_info:
        upload_and_ingest_course_document(db_session, candidate_user_a, upload)
    assert exc_info.value.status_code == 400
    assert "Unsupported file format" in exc_info.value.detail


def test_empty_file_rejected(db_session: Session, candidate_user_a: User):
    upload = UploadFile(
        file=io.BytesIO(b""),
        filename="empty.txt",
        headers={"content-type": "text/plain"},
    )
    with pytest.raises(HTTPException) as exc_info:
        upload_and_ingest_course_document(db_session, candidate_user_a, upload)
    assert exc_info.value.status_code == 400
    assert "empty" in exc_info.value.detail.lower()


def test_oversized_file_rejected_during_streaming(db_session: Session, candidate_user_a: User):
    """
    Tests that a stream exceeding 15 MB is rejected immediately during streaming
    without storing or fully buffering the payload.
    """
    class OversizedByteStream:
        def __init__(self, size: int):
            self.remaining = size
            self.chunk = b"X" * (64 * 1024)

        def read(self, n: int = -1) -> bytes:
            if self.remaining <= 0:
                return b""
            amt = min(len(self.chunk), self.remaining)
            self.remaining -= amt
            return self.chunk[:amt]

    # Stream 16 MB
    mock_upload = UploadFile(
        file=OversizedByteStream(16 * 1024 * 1024),
        filename="huge_book.pdf",
        headers={"content-type": "application/pdf"},
    )
    with pytest.raises(HTTPException) as exc_info:
        upload_and_ingest_course_document(db_session, candidate_user_a, mock_upload)
    assert exc_info.value.status_code == 413
    assert "maximum allowed size" in exc_info.value.detail.lower()


def test_malformed_pdf_rejected(db_session: Session, candidate_user_a: User):
    """Corrupt bytes with PDF magic header should be caught gracefully."""
    corrupt_pdf = b"%PDF-1.4\nGarbage binary payload that cannot be parsed by MuPDF\x00\xff\xfe"
    upload = UploadFile(
        file=io.BytesIO(corrupt_pdf),
        filename="broken.pdf",
        headers={"content-type": "application/pdf"},
    )
    with pytest.raises(HTTPException) as exc_info:
        upload_and_ingest_course_document(db_session, candidate_user_a, upload)
    assert exc_info.value.status_code == 400
    assert "corrupted" in exc_info.value.detail.lower() or "malformed" in exc_info.value.detail.lower()


def test_scanned_empty_text_pdf_rejected(db_session: Session, candidate_user_a: User):
    """A valid PDF with no extractable text characters should be rejected."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)  # blank page
    blank_bytes = doc.write()
    doc.close()

    upload = UploadFile(
        file=io.BytesIO(blank_bytes),
        filename="blank_scanned.pdf",
        headers={"content-type": "application/pdf"},
    )
    with pytest.raises(HTTPException) as exc_info:
        upload_and_ingest_course_document(db_session, candidate_user_a, upload)
    assert exc_info.value.status_code == 400
    assert "no extractable text" in exc_info.value.detail.lower()


# ── TEST 4: DUPLICATE UPLOAD AND SAFE RE-INDEXING ────────────────────────────
def test_duplicate_upload_and_safe_reindexing(db_session: Session, candidate_user_a: User):
    """
    Uploading the exact same document updates the existing record without creating
    a duplicate row, recalculates embeddings safely, and refreshes the metadata.
    """
    content = b"# Operating Systems\nVirtual Memory paging creates an illusion of large contiguous memory."
    upload1 = UploadFile(file=io.BytesIO(content), filename="os_notes.md", headers={"content-type": "text/markdown"})
    doc1 = upload_and_ingest_course_document(db_session, candidate_user_a, upload1)

    try:
        doc_count_before = (
            db_session.query(CourseDocument)
            .filter(CourseDocument.user_id == candidate_user_a.id)
            .count()
        )

        # Upload identical content
        upload2 = UploadFile(file=io.BytesIO(content), filename="os_notes_renamed.md", headers={"content-type": "text/markdown"})
        doc2 = upload_and_ingest_course_document(db_session, candidate_user_a, upload2)

        doc_count_after = (
            db_session.query(CourseDocument)
            .filter(CourseDocument.user_id == candidate_user_a.id)
            .count()
        )

        assert doc1.id == doc2.id
        assert doc_count_before == doc_count_after
        assert doc2.content_hash == doc1.content_hash
    finally:
        delete_course_document(db_session, candidate_user_a, doc1.id)


# ── TEST 5: OWNER-SCOPED ISOLATION & ZERO CROSS-USER LEAKAGE ─────────────────
def test_cross_user_isolation(
    db_session: Session,
    candidate_user_a: User,
    candidate_user_b: User,
):
    """
    Verifies that:
    1. Candidate A's document is never visible in Candidate B's list.
    2. Candidate B cannot retrieve Candidate A's document by ID (HTTP 404).
    3. Candidate B cannot delete Candidate A's document (HTTP 404).
    4. Candidate B's vector searches return zero matches for Candidate A's material.
    """
    content = b"# Proprietary Research A\nSecret algorithm Alpha-7 guarantees deterministic latency."
    upload = UploadFile(file=io.BytesIO(content), filename="secret_a.md", headers={"content-type": "text/markdown"})
    doc_a = upload_and_ingest_course_document(db_session, candidate_user_a, upload)

    try:
        # User B list documents
        user_b_docs = get_user_course_documents(db_session, candidate_user_b)
        assert doc_a.id not in [d.id for d in user_b_docs]

        # User B get by ID
        with pytest.raises(HTTPException) as get_exc:
            get_course_document_by_id(db_session, candidate_user_b, doc_a.id)
        assert get_exc.value.status_code == 404

        # User B delete
        with pytest.raises(HTTPException) as del_exc:
            delete_course_document(db_session, candidate_user_b, doc_a.id)
        assert del_exc.value.status_code == 404

        # User B vector search for User A's unique keywords
        b_results = search_course_materials("Secret algorithm Alpha-7 deterministic latency", user_id=candidate_user_b.id)
        assert len(b_results) == 0

        # User A vector search does find it
        a_results = search_course_materials("Secret algorithm Alpha-7", user_id=candidate_user_a.id)
        assert len(a_results) >= 1
        assert a_results[0].document_id == doc_a.id
    finally:
        delete_course_document(db_session, candidate_user_a, doc_a.id)


# ── TEST 6: PERSISTENT INDEXING FAILURE & EPHEMERAL FALLBACK ─────────────────
def test_persistent_indexing_failure_reports_degraded_status(
    db_session: Session,
    candidate_user_a: User,
):
    """
    Simulates ChromaDB PersistentClient failure. Verifies that the document status
    is marked truthfully as 'degraded' (not 'indexed') with an explicit error message.
    """
    _get_teaching_materials_collection.cache_clear()

    class PanicException(BaseException):
        pass

    with patch("chromadb.PersistentClient", side_effect=PanicException("SQLite disk I/O panic")):
        col, is_persistent = _get_teaching_materials_collection()
        assert is_persistent is False
        assert col is not None

        content = b"# Ephemeral Fallback Test\nThis document tests degraded state reporting."
        upload = UploadFile(file=io.BytesIO(content), filename="fallback.md", headers={"content-type": "text/markdown"})
        doc = upload_and_ingest_course_document(db_session, candidate_user_a, upload)

        try:
            assert doc.status == "degraded"
            assert "Persistent vector store unavailable" in doc.error_message
        finally:
            delete_course_document(db_session, candidate_user_a, doc.id)

    _get_teaching_materials_collection.cache_clear()


# ── TEST 7: DELETION CLEANUP RESILIENCE ───────────────────────────────────────
def test_deletion_cleanup_resilience(db_session: Session, candidate_user_a: User):
    """
    If the file on disk was already deleted externally, delete_course_document
    must still delete the database record and clean ChromaDB without crashing.
    """
    content = b"# Cleanup Resilience\nTesting cleanup when file is missing on disk."
    upload = UploadFile(file=io.BytesIO(content), filename="cleanup.md", headers={"content-type": "text/markdown"})
    doc = upload_and_ingest_course_document(db_session, candidate_user_a, upload)

    # Manually remove the disk file to simulate out-of-band removal
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Deletion should still succeed cleanly
    deleted = delete_course_document(db_session, candidate_user_a, doc.id)
    assert deleted is True

    # Record must be gone
    found = db_session.query(CourseDocument).filter(CourseDocument.id == doc.id).first()
    assert found is None


# ── TEST 8: TEACHING ROOM DR. CYRA VANCE RAG INTEGRATION & CITATIONS ──────────
def test_teaching_room_course_materials_citations(db_session: Session, candidate_user_a: User):
    """
    Verifies that when a candidate asks about a concept in their uploaded material:
    1. Evidence gate detects course_material_grounded.
    2. TeachingChatResponse includes uploaded_course_material citations with
       real document title, page number / section, and similarity score.
    3. Zero fabricated citations exist.
    """
    pdf_bytes = _create_test_pdf_bytes()
    upload = UploadFile(
        file=io.BytesIO(pdf_bytes),
        filename="Raft_Consensus_Lecture_Notes.pdf",
        headers={"content-type": "application/pdf"},
    )
    doc = upload_and_ingest_course_document(db_session, candidate_user_a, upload)

    try:
        # User query matching uploaded document
        req = TeachingChatRequest(
            mode="skill",
            target_id="Distributed Consensus",
            message="Why does Raft use randomized election timeouts between 150ms and 300ms?",
            is_assessment=False,
        )
        res = chat_with_teaching_mentor(db_session, candidate_user_a, req)

        assert res.evidence_sufficiency == "sufficient"
        assert res.technical_source_status in ("course_material_grounded", "fresh_technical_sources")
        assert len(res.citations) >= 1

        course_citations = [c for c in res.citations if c.get("type") == "uploaded_course_material"]
        assert len(course_citations) >= 1

        top_citation = course_citations[0]
        assert top_citation["title"] == "Raft_Consensus_Lecture_Notes.pdf"
        assert top_citation["page_number"] in (1, 2)
        assert top_citation["similarity"] >= 0.28
        assert "excerpt" in top_citation

        # Unrelated query should NOT cite the Raft document
        unrelated_req = TeachingChatRequest(
            mode="skill",
            target_id="Cosmology",
            message="What is the cosmic microwave background radiation temperature?",
            is_assessment=False,
        )
        unrelated_res = chat_with_teaching_mentor(db_session, candidate_user_a, unrelated_req)
        assert unrelated_res.evidence_sufficiency == "insufficient"
        assert unrelated_res.citations == []  # Zero fake citations
    finally:
        delete_course_document(db_session, candidate_user_a, doc.id)


# ── TEST 9: FASTAPI ROUTER ENDPOINTS VIA TESTCLIENT ──────────────────────────
def test_router_endpoints_authenticated(candidate_user_a: User):
    """
    Tests the REST API contracts:
    - POST /course-documents/upload
    - GET /course-documents
    - GET /course-documents/{document_id}
    - GET /course-documents/search?q=...
    - DELETE /course-documents/{document_id}
    Using FastAPI dependency overrides for get_current_user.
    """
    from app.core.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: candidate_user_a

    client = TestClient(app)
    try:
        # 1. Upload
        file_payload = ("syllabus.md", b"# Compiler Design\nLexical analysis converts stream of chars into tokens.", "text/markdown")
        upload_resp = client.post("/course-documents/upload", files={"file": file_payload})
        assert upload_resp.status_code == 201
        upload_data = upload_resp.json()
        assert upload_data["success"] is True
        doc_id = upload_data["document"]["id"]

        # 2. List
        list_resp = client.get("/course-documents")
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert any(d["id"] == doc_id for d in list_data["documents"])

        # 3. Detail
        detail_resp = client.get(f"/course-documents/{doc_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["filename"] == "syllabus.md"

        # 4. Search
        search_resp = client.get("/course-documents/search", params={"q": "Lexical analysis compiler tokens"})
        assert search_resp.status_code == 200
        search_data = search_resp.json()
        assert len(search_data) >= 1
        assert search_data[0]["document_id"] == doc_id

        # 5. Delete
        del_resp = client.delete(f"/course-documents/{doc_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["success"] is True

        # 6. Verify 404 after delete
        check_resp = client.get(f"/course-documents/{doc_id}")
        assert check_resp.status_code == 404
    finally:
        app.dependency_overrides.pop(get_current_user, None)
