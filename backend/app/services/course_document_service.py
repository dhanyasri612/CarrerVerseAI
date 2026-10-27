"""
Course Document Ingestion & Retrieval Service for CareerVerse AI Teaching Room.

Handles secure upload, validation, parsing, section-aware chunking, and isolated
vector indexing for candidate learning materials (PDF, Markdown, TXT).
Strictly scopes all vector and database operations to the authenticated user.
"""

from __future__ import annotations

import hashlib
import inspect
import logging
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import CHROMADB_DIR
from app.models.course_document import CourseDocument
from app.models.user import User
from app.schemas.course_document import CourseMaterialSearchResult

try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

logger = logging.getLogger("careerverse.ai.course_documents")

TEACHING_MATERIALS_COLLECTION = "teaching_materials"
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB
CHUNK_READ_SIZE = 64 * 1024       # 64 KB streaming buffer
CHUNK_SIZE_CHARS = 1000
CHUNK_OVERLAP_CHARS = 150
MIN_SIMILARITY_THRESHOLD = 0.25

ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/markdown",
    "text/plain",
    "text/x-markdown",
    "application/octet-stream",
}

STORAGE_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "course_documents"))
os.makedirs(STORAGE_BASE_DIR, exist_ok=True)


@dataclass(frozen=True)
class ParsedDocumentChunk:
    chunk_index: int
    text: str
    page_number: Optional[int]
    section_heading: str


def _sanitize_filename(name: str) -> str:
    """Strip directory traversal components and unsafe characters."""
    base = os.path.basename(name or "document.txt")
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", base)
    return clean[:180] or "document.txt"


def _sha256_file(file_path: str) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def _get_teaching_materials_collection() -> Tuple[Any, bool]:
    """
    Get or create the dedicated teaching_materials ChromaDB collection.
    Returns (collection, is_persistent: bool).
    If persistent ChromaDB panics or fails, safely falls back to ephemeral Client.
    """
    import chromadb
    from chromadb.config import Settings

    try:
        client = chromadb.PersistentClient(
            path=CHROMADB_DIR,
            settings=Settings(anonymized_telemetry=False, is_persistent=True),
        )
        try:
            col = client.get_or_create_collection(
                name=TEACHING_MATERIALS_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            col = client.get_collection(name=TEACHING_MATERIALS_COLLECTION)
        return col, True
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as exc:
        logger.warning("Persistent Chroma client failed for course materials (%s); activating in-memory Client", exc)
    except BaseException as exc:
        exc_str = f"{type(exc)} {type(exc).__name__}".lower()
        if "panic" in exc_str or "pyo3" in exc_str or "chroma" in exc_str:
            logger.warning(
                "ChromaDB persistent engine panic encountered for course materials (%s); falling back to ephemeral Client",
                type(exc).__name__,
            )
        else:
            raise

    # Ephemeral in-memory fallback
    try:
        client = chromadb.Client(
            Settings(anonymized_telemetry=False, is_persistent=False, allow_reset=True)
        )
        col = client.get_or_create_collection(
            name=TEACHING_MATERIALS_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        return col, False
    except Exception as fb_exc:
        logger.error("Chroma ephemeral Client fallback failed for course materials: %s", fb_exc)
        return None, False


def _default_embed(text: str) -> List[float]:
    from app.ai.embeddings.encoder import EXPECTED_EMBEDDING_DIMENSION, embedding_encoder

    vector = embedding_encoder.model.encode(
        text[:8000],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    values = vector.tolist()
    if len(values) != EXPECTED_EMBEDDING_DIMENSION:
        raise ValueError(f"Embedding dimension mismatch: expected {EXPECTED_EMBEDDING_DIMENSION}, got {len(values)}")
    return values


# ── SECTION-AWARE CHUNKING HELPERS ───────────────────────────────────────────
def _split_text_with_overlap(
    text: str,
    chunk_size: int = CHUNK_SIZE_CHARS,
    overlap: int = CHUNK_OVERLAP_CHARS,
) -> List[str]:
    """Splits a single block of text into bounded overlapping segments."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)
    step = max(50, chunk_size - overlap)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        if end < text_len:
            last_space = text.rfind(" ", start + step // 2, end)
            if last_space > start:
                end = last_space

        chunk = text[start:end].strip()
        if len(chunk) >= 30:
            chunks.append(chunk)

        if end >= text_len:
            break
        start = end - overlap if (end - overlap) > start else end

    return chunks


def _extract_pdf_chunks(file_path: str) -> Tuple[List[ParsedDocumentChunk], int]:
    """
    Extracts text from PDF with page numbers and bounded overlapping chunks.
    Raises HTTPException 400 on malformed or unextractable PDFs.
    """
    # 1. Validate magic bytes
    with open(file_path, "rb") as f:
        header = f.read(5)
        if not header.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Malformed PDF file: missing standard PDF header bytes.",
            )

    if fitz is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF parsing library (PyMuPDF) is not installed on the server.",
        )

    try:
        doc = fitz.open(file_path)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Malformed or corrupted PDF file: {str(exc)}",
        ) from exc

    try:
        total_pages = len(doc)
        if total_pages == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF file contains zero pages.",
            )

        all_chunks: List[ParsedDocumentChunk] = []
        chunk_idx = 0
        total_text_chars = 0

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_text = (page.get_text() or "").strip()
            total_text_chars += len(page_text)
            if not page_text:
                continue

            # Detect top heading on the page if present
            lines = [l.strip() for l in page_text.splitlines() if l.strip()]
            first_line = lines[0] if lines else "Page Content"
            section_heading = first_line[:80] if len(first_line) < 80 else f"Page {page_idx + 1}"

            page_segments = _split_text_with_overlap(page_text)
            for seg in page_segments:
                all_chunks.append(
                    ParsedDocumentChunk(
                        chunk_index=chunk_idx,
                        text=seg,
                        page_number=page_idx + 1,
                        section_heading=section_heading,
                    )
                )
                chunk_idx += 1

        if total_text_chars < 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF contains no extractable text. Scanned or image-only PDFs are not supported.",
            )

        return all_chunks, total_pages
    finally:
        doc.close()


def _extract_markdown_chunks(file_path: str) -> List[ParsedDocumentChunk]:
    """Parses Markdown content preserving #, ##, ### section headings."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.splitlines()
    sections: List[Tuple[str, List[str]]] = []
    current_heading = "Overview"
    current_lines: List[str] = []

    for line in lines:
        match = re.match(r"^(#{1,4})\s+(.+)$", line.strip())
        if match:
            if current_lines:
                sections.append((current_heading, current_lines))
                current_lines = []
            current_heading = match.group(2).strip()[:100]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_heading, current_lines))

    chunks: List[ParsedDocumentChunk] = []
    chunk_idx = 0
    for heading, sec_lines in sections:
        sec_text = "\n".join(sec_lines).strip()
        segments = _split_text_with_overlap(sec_text)
        for seg in segments:
            chunks.append(
                ParsedDocumentChunk(
                    chunk_index=chunk_idx,
                    text=seg,
                    page_number=None,
                    section_heading=heading,
                )
            )
            chunk_idx += 1

    if not chunks and content.strip():
        chunks.append(
            ParsedDocumentChunk(
                chunk_index=0,
                text=content.strip()[:CHUNK_SIZE_CHARS],
                page_number=None,
                section_heading="Overview",
            )
        )
    return chunks


def _extract_text_chunks(file_path: str) -> List[ParsedDocumentChunk]:
    """Parses plain text documents into bounded overlapping chunks."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read().strip()

    if not content:
        return []

    segments = _split_text_with_overlap(content)
    chunks = [
        ParsedDocumentChunk(
            chunk_index=i,
            text=seg,
            page_number=None,
            section_heading="Document Content",
        )
        for i, seg in enumerate(segments)
    ]
    return chunks


# ── INGESTION SERVICE IMPLEMENTATION ─────────────────────────────────────────
async def ingest_course_document(
    db: Session,
    current_user: User,
    file: UploadFile,
    embed_fn: Optional[Callable[[str], List[float]]] = None,
) -> CourseDocument:
    """
    Validates, stores, extracts, chunks, and indexes an uploaded course document.
    Enforces the 15 MB limit while streaming to prevent memory exhaustion.
    Scoping and deduplication are strictly isolated to current_user.id.
    """
    embed = embed_fn or _default_embed

    # 1. Validate filename & extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing from upload.",
        )

    clean_orig_name = _sanitize_filename(file.filename)
    file_ext = os.path.splitext(clean_orig_name)[1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: .pdf, .md, .txt",
        )

    file_type = "pdf" if file_ext == ".pdf" else ("markdown" if file_ext in {".md", ".markdown"} else "text")

    # 2. Setup user-isolated directory
    user_storage_dir = os.path.join(STORAGE_BASE_DIR, str(current_user.id))
    os.makedirs(user_storage_dir, exist_ok=True)

    temp_storage_name = f"{uuid.uuid4().hex}_{clean_orig_name}"
    temp_file_path = os.path.join(user_storage_dir, temp_storage_name)

    # 3. Stream upload with strict 15 MB cap
    bytes_read = 0
    try:
        with open(temp_file_path, "wb") as buffer:
            while True:
                chunk = file.read(CHUNK_READ_SIZE)
                if inspect.isawaitable(chunk):
                    chunk = await chunk
                if not chunk:
                    break
                bytes_read += len(chunk)
                if bytes_read > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File exceeds maximum allowed size of 15 MB.",
                    )
                buffer.write(chunk)
    except Exception:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise

    if bytes_read == 0:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes).",
        )

    content_hash = _sha256_file(temp_file_path)

    # 4. Extract text and chunks based on file type
    try:
        if file_type == "pdf":
            chunks, total_pages = _extract_pdf_chunks(temp_file_path)
        elif file_type == "markdown":
            chunks = _extract_markdown_chunks(temp_file_path)
            total_pages = None
        else:
            chunks = _extract_text_chunks(temp_file_path)
            total_pages = None

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable text or meaningful content found in document.",
            )
    except Exception:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise

    # 5. Embed chunks
    try:
        embeddings = [embed(c.text) for c in chunks]
    except Exception as exc:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector embedding generation failed: {str(exc)}",
        ) from exc

    # 6. Check existing duplicate upload by same user
    existing_doc = (
        db.query(CourseDocument)
        .filter(
            CourseDocument.user_id == current_user.id,
            CourseDocument.content_hash == content_hash,
        )
        .first()
    )

    col, is_persistent = _get_teaching_materials_collection()

    # Determine truthful indexing status
    indexing_status = "indexed" if (is_persistent and col is not None) else "degraded"
    error_msg = None if is_persistent else "Persistent vector store unavailable; indexing is ephemeral."

    if existing_doc:
        # ── RE-INDEXING PATH (Safe replacement) ──────────────────────────────
        target_doc = existing_doc
        target_doc.filename = clean_orig_name
        target_doc.original_filename = clean_orig_name
        target_doc.file_path = temp_file_path
        target_doc.file_size = bytes_read
        target_doc.total_pages = total_pages
        target_doc.total_chunks = len(chunks)
        target_doc.status = indexing_status
        target_doc.error_message = error_msg
        target_doc.updated_at = datetime.utcnow()

        if col is not None:
            try:
                # Remove prior chunks for this document
                col.delete(where={"$and": [{"document_id": target_doc.id}, {"owner_id": current_user.id}]})
            except Exception as del_exc:
                logger.debug("Prior chunk deletion for re-index: %s", del_exc)

            chunk_ids = [f"course_doc_{target_doc.id}#chunk_{c.chunk_index}" for c in chunks]
            chunk_metas = [
                {
                    "document_id": int(target_doc.id),
                    "owner_id": int(current_user.id),
                    "filename": str(clean_orig_name),
                    "page_number": int(c.page_number) if c.page_number is not None else 0,
                    "section_heading": str(c.section_heading or "Overview"),
                    "chunk_index": int(c.chunk_index),
                    "content_hash": str(content_hash),
                    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                }
                for c in chunks
            ]
            col.upsert(
                ids=chunk_ids,
                embeddings=embeddings,
                metadatas=chunk_metas,
                documents=[c.text for c in chunks],
            )
        db.commit()
        db.refresh(target_doc)
        return target_doc

    # ── NEW DOCUMENT CREATION PATH ───────────────────────────────────────────
    new_doc = CourseDocument(
        user_id=current_user.id,
        filename=clean_orig_name,
        original_filename=clean_orig_name,
        file_path=temp_file_path,
        file_type=file_type,
        mime_type=file.content_type or "application/octet-stream",
        file_size=bytes_read,
        content_hash=content_hash,
        status=indexing_status,
        error_message=error_msg,
        total_pages=total_pages,
        total_chunks=len(chunks),
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    if col is not None:
        chunk_ids = [f"course_doc_{new_doc.id}#chunk_{c.chunk_index}" for c in chunks]
        chunk_metas = [
            {
                "document_id": int(new_doc.id),
                "owner_id": int(current_user.id),
                "filename": str(clean_orig_name),
                "page_number": int(c.page_number) if c.page_number is not None else 0,
                "section_heading": str(c.section_heading or "Overview"),
                "chunk_index": int(c.chunk_index),
                "content_hash": str(content_hash),
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            }
            for c in chunks
        ]
        col.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            metadatas=chunk_metas,
            documents=[c.text for c in chunks],
        )

    return new_doc


def upload_and_ingest_course_document(
    db: Session,
    current_user: User,
    file: UploadFile,
    embed_fn: Optional[Callable[[str], List[float]]] = None,
) -> CourseDocument:
    """
    Synchronous entrypoint for course document ingestion.
    Runs ingest_course_document cleanly regardless of current thread or event loop state.
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, ingest_course_document(db, current_user, file, embed_fn))
                return future.result()
        return loop.run_until_complete(ingest_course_document(db, current_user, file, embed_fn))
    except RuntimeError:
        return asyncio.run(ingest_course_document(db, current_user, file, embed_fn))


def get_user_course_documents(db: Session, current_user: User) -> List[CourseDocument]:
    """Lists all uploaded course materials belonging to current_user."""
    return (
        db.query(CourseDocument)
        .filter(CourseDocument.user_id == current_user.id)
        .order_by(CourseDocument.created_at.desc())
        .all()
    )


def get_course_document_by_id(db: Session, current_user: User, document_id: int) -> CourseDocument:
    """Retrieves document detail ensuring ownership."""
    doc = (
        db.query(CourseDocument)
        .filter(CourseDocument.id == document_id, CourseDocument.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course document #{document_id} not found.",
        )
    return doc


def delete_course_document(db: Session, current_user: User, document_id: int) -> bool:
    """
    Deletes course document from database, disk storage, and Chroma vector index.
    Strictly verifies current_user ownership.
    """
    doc = get_course_document_by_id(db, current_user, document_id)

    # 1. Clean Chroma vector collection
    col, _ = _get_teaching_materials_collection()
    if col is not None:
        try:
            col.delete(where={"$and": [{"document_id": int(doc.id)}, {"owner_id": int(current_user.id)}]})
        except Exception as exc:
            logger.warning("Error deleting Chroma chunks for course doc %d: %s", doc.id, exc)

    # 2. Clean disk storage
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as exc:
            logger.warning("Error removing file from disk: %s", exc)

    # 3. Clean database record
    db.delete(doc)
    db.commit()
    return True


# ── OWNER-SCOPED VECTOR RETRIEVAL FOR TEACHING ROOM ──────────────────────────
def search_course_materials(
    query: str,
    user_id: int,
    top_k: int = 4,
    embed_fn: Optional[Callable[[str], List[float]]] = None,
) -> List[CourseMaterialSearchResult]:
    """
    Retrieves course materials strictly isolated by owner_id == user_id.
    Zero cross-user leakage.
    """
    if not query or not query.strip():
        return []

    col, _ = _get_teaching_materials_collection()
    if col is None or col.count() == 0:
        return []

    embed = embed_fn or _default_embed
    try:
        result = col.query(
            query_embeddings=[embed(query.strip())],
            n_results=max(1, min(top_k * 2, 20)),
            where={"owner_id": int(user_id)},
            include=["metadatas", "documents", "distances"],
        )
    except Exception as exc:
        logger.warning("Course materials Chroma query failed: %s", exc)
        return []

    ids = (result.get("ids") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    documents = (result.get("documents") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    results: List[CourseMaterialSearchResult] = []
    seen_keys = set()

    for rec_id, meta, doc, dist in zip(ids, metadatas, documents, distances):
        meta = meta or {}
        # Cosine distance to similarity
        similarity = max(0.0, min(1.0, 1.0 - float(dist)))
        if similarity < MIN_SIMILARITY_THRESHOLD:
            continue

        doc_id = int(meta.get("document_id") or 0)
        page_num = int(meta.get("page_number") or 0)
        sec_heading = str(meta.get("section_heading") or "Overview")

        key = f"{doc_id}:{page_num}:{sec_heading}"
        if key in seen_keys:
            continue
        seen_keys.add(key)

        results.append(
            CourseMaterialSearchResult(
                document_id=doc_id,
                filename=str(meta.get("filename") or "Course Material"),
                page_number=page_num if page_num > 0 else None,
                section_heading=sec_heading,
                similarity_score=similarity,
                excerpt=str(doc or "")[:1000],
                chunk_index=int(meta.get("chunk_index") or 0),
            )
        )
        if len(results) >= top_k:
            break

    return results
