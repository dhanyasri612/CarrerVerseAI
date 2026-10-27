"""Refresh and retrieve dated technical references independently of candidate data."""

from __future__ import annotations

import hashlib
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from functools import lru_cache
from html.parser import HTMLParser
from typing import Any, Callable, Dict, Iterable, List, Optional

logger = logging.getLogger("careerverse.ai.rag.technical_sources")

TECHNICAL_SOURCE_COLLECTION = "technical_resources"
TECHNICAL_SOURCE_MAX_AGE_DAYS = 30
MIN_TECHNICAL_SOURCE_SIMILARITY = 0.45
MAX_SOURCE_BODY_BYTES = 2_000_000
MAX_SOURCE_TEXT_CHARS = 40_000
EMBEDDING_TEXT_CHARS = 8_000
CHUNK_SIZE_CHARS = 1_200
CHUNK_OVERLAP_CHARS = 200

# Refreshing is restricted to the official sites already listed in the curated catalog.
ALLOWED_SOURCE_HOSTS = {
    "docs.python.org",
    "fastapi.tiangolo.com",
    "react.dev",
    "www.postgresql.org",
    "leetcode.com",
    "docs.docker.com",
    "redis.io",
    "python.langchain.com",
    "langchain-ai.github.io",
    "go.dev",
    "en.cppreference.com",
    "isocpp.github.io",
    "www.typescriptlang.org",
    "kubernetes.io",
    "docs.aws.amazon.com",
    "www.mongodb.com",
    "help.figma.com",
    "www.w3.org",
    "docs.anthropic.com",
    "arxiv.org",
    "genai.owasp.org",
    "www.geeksforgeeks.org",
}


@dataclass(frozen=True)
class FetchResponse:
    status_code: int
    body: str
    headers: Dict[str, str]
    final_url: str


@dataclass(frozen=True)
class SectionBlock:
    heading: str
    text: str


@dataclass(frozen=True)
class DocumentChunk:
    chunk_index: int
    section_heading: str
    text: str


class _SectionAwareTextParser(HTMLParser):
    _IGNORED_TAGS = {"script", "style", "nav", "header", "footer", "svg", "noscript"}
    _BLOCK_TAGS = {"article", "br", "div", "li", "main", "p", "section", "tr", "pre"}
    _HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self._in_heading = False
        self._current_heading = "Overview"
        self._heading_buffer: List[str] = []
        self._current_text: List[str] = []
        self.sections: List[SectionBlock] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag in self._IGNORED_TAGS:
            self._ignored_depth += 1
        elif not self._ignored_depth:
            if tag in self._HEADING_TAGS:
                self._flush_section()
                self._in_heading = True
                self._heading_buffer = []
            elif tag in self._BLOCK_TAGS:
                self._current_text.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._IGNORED_TAGS and self._ignored_depth:
            self._ignored_depth -= 1
        elif not self._ignored_depth:
            if tag in self._HEADING_TAGS:
                self._in_heading = False
                heading_str = re.sub(r"\s+", " ", " ".join(self._heading_buffer)).strip()
                if heading_str:
                    self._current_heading = heading_str[:120]
                self._heading_buffer = []
            elif tag in self._BLOCK_TAGS:
                self._current_text.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            if self._in_heading:
                self._heading_buffer.append(data)
            else:
                self._current_text.append(data)

    def _flush_section(self) -> None:
        raw_text = re.sub(r"\s+", " ", " ".join(self._current_text)).strip()
        if raw_text:
            self.sections.append(SectionBlock(heading=self._current_heading, text=raw_text))
        self._current_text = []

    def get_sections(self) -> List[SectionBlock]:
        self._flush_section()
        if not self.sections:
            return [SectionBlock(heading="Overview", text="")]
        return self.sections


def chunk_sections(
    sections: List[SectionBlock],
    chunk_size: int = CHUNK_SIZE_CHARS,
    overlap: int = CHUNK_OVERLAP_CHARS,
) -> List[DocumentChunk]:
    """Break section blocks into bounded, overlapping chunks preserving section headings."""
    chunks: List[DocumentChunk] = []
    chunk_idx = 0

    for sec in sections:
        text = sec.text.strip()
        if not text:
            continue

        if len(text) <= chunk_size:
            chunks.append(DocumentChunk(chunk_index=chunk_idx, section_heading=sec.heading, text=text))
            chunk_idx += 1
            continue

        start = 0
        text_len = len(text)
        step = max(100, chunk_size - overlap)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            if end < text_len:
                last_space = text.rfind(" ", start + step // 2, end)
                if last_space != -1 and last_space > start:
                    end = last_space

            chunk_content = text[start:end].strip()
            if len(chunk_content) >= 40:
                chunks.append(DocumentChunk(chunk_index=chunk_idx, section_heading=sec.heading, text=chunk_content))
                chunk_idx += 1

            if end >= text_len:
                break
            start = end - overlap if (end - overlap) > start else end

    if not chunks:
        chunks.append(DocumentChunk(chunk_index=0, section_heading="Overview", text=""))
    return chunks


class _VisibleTextParser(HTMLParser):
    _IGNORED_TAGS = {"script", "style", "nav", "header", "footer", "svg", "noscript"}
    _BLOCK_TAGS = {"article", "br", "div", "h1", "h2", "h3", "li", "main", "p", "section"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self._text: List[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag in self._IGNORED_TAGS:
            self._ignored_depth += 1
        elif not self._ignored_depth and tag in self._BLOCK_TAGS:
            self._text.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._IGNORED_TAGS and self._ignored_depth:
            self._ignored_depth -= 1
        elif not self._ignored_depth and tag in self._BLOCK_TAGS:
            self._text.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self._text.append(data)

    def get_text(self) -> str:
        text = " ".join(self._text)
        return re.sub(r"\s+", " ", text).strip()[:MAX_SOURCE_TEXT_CHARS]


def extract_visible_text(html: str) -> str:
    parser = _VisibleTextParser()
    parser.feed(html)
    return parser.get_text()


def extract_structured_sections(html: str) -> List[SectionBlock]:
    parser = _SectionAwareTextParser()
    parser.feed(html)
    return parser.get_sections()


def build_resource_specs(resource_bank: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    """Flatten the existing curated resource catalog into a stable refresh allowlist."""
    specs: Dict[str, Dict[str, str]] = {}
    for entries in resource_bank.values():
        for item in entries:
            resource_id = str(item.get("id") or "").strip()
            url = str(item.get("canonical_url") or "").strip()
            title = str(item.get("title") or "").strip()
            source = str(item.get("source") or "").strip()
            if not resource_id or not title or not source or not _is_allowed_source_url(url):
                continue
            specs[resource_id] = {
                "id": resource_id,
                "title": title,
                "canonical_url": url,
                "source": source,
            }
    return list(specs.values())


def _is_allowed_source_url(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname in ALLOWED_SOURCE_HOSTS
        and not parsed.username
        and not parsed.password
    )


class _SameHostRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, expected_host: str) -> None:
        super().__init__()
        self.expected_host = expected_host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        if parsed.scheme != "https" or parsed.hostname != self.expected_host:
            raise ValueError("Source redirected outside its approved HTTPS host.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_official_page(url: str, headers: Optional[Dict[str, str]] = None) -> FetchResponse:
    """Fetch a catalog URL with a byte cap and same-host HTTPS redirect policy."""
    if not _is_allowed_source_url(url):
        raise ValueError("Technical source URL is not on the approved HTTPS allowlist.")

    host = urllib.parse.urlsplit(url).hostname
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "CareerVerse-Technical-Source-Refresh/1.0",
            "Accept": "text/html,application/xhtml+xml",
            **(headers or {}),
        },
    )
    opener = urllib.request.build_opener(_SameHostRedirectHandler(host or ""))
    try:
        response = opener.open(request, timeout=15)
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            return FetchResponse(
                status_code=304,
                body="",
                headers=dict(exc.headers.items()),
                final_url=exc.geturl(),
            )
        raise

    with response:
        final_url = response.geturl()
        if not _is_allowed_source_url(final_url) or urllib.parse.urlsplit(final_url).hostname != host:
            raise ValueError("Source resolved outside its approved HTTPS host.")
        content_type = response.headers.get_content_type()
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ValueError(f"Expected an HTML document, received {content_type}.")
        body = response.read(MAX_SOURCE_BODY_BYTES + 1)
        if len(body) > MAX_SOURCE_BODY_BYTES:
            raise ValueError("Technical source exceeded the maximum download size.")
        charset = response.headers.get_content_charset() or "utf-8"
        return FetchResponse(
            status_code=int(response.status),
            body=body.decode(charset, errors="replace"),
            headers=dict(response.headers.items()),
            final_url=final_url,
        )


def _utc_datetime(value: Optional[datetime] = None) -> datetime:
    value = value or datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _get_existing_record(collection: Any, record_id: str) -> tuple[Dict[str, Any], str]:
    result = collection.get(ids=[record_id], include=["metadatas", "documents"])
    if not result or not result.get("ids"):
        return {}, ""
    metadatas = result.get("metadatas") or []
    documents = result.get("documents") or []
    return (metadatas[0] or {}, documents[0] or "")


def _parse_source_last_modified(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        return _utc_datetime(parsed).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


@lru_cache(maxsize=1)
def _default_collection():
    from app.core.config import CHROMADB_DIR
    import chromadb
    from chromadb.config import Settings

    # Attempt PersistentClient first
    try:
        client = chromadb.PersistentClient(
            path=CHROMADB_DIR,
            settings=Settings(anonymized_telemetry=False, is_persistent=True),
        )
        try:
            return client.get_or_create_collection(
                name=TECHNICAL_SOURCE_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception:
            return client.get_collection(name=TECHNICAL_SOURCE_COLLECTION)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as exc:
        logger.warning("Chroma PersistentClient failed (%s); activating in-memory Client", exc)
    except BaseException as exc:
        # Handle PyO3/Rust panics specifically without swallowing other system errors
        exc_str = f"{type(exc)} {type(exc).__name__}".lower()
        if "panic" in exc_str or "pyo3" in exc_str or "chroma" in exc_str:
            logger.warning(
                "ChromaDB persistent client panic encountered (%s: %s); falling back to ephemeral Client",
                type(exc).__name__,
                exc,
            )
        else:
            raise

    # Fallback: Ephemeral in-memory client
    try:
        client = chromadb.Client(
            Settings(anonymized_telemetry=False, is_persistent=False, allow_reset=True)
        )
        return client.get_or_create_collection(
            name=TECHNICAL_SOURCE_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as fb_exc:
        logger.error("Chroma ephemeral Client fallback failed (%s); technical collection unavailable", fb_exc)
        return None



def _default_embed(text: str) -> List[float]:
    """Use the project's real sentence-transformer model; never invent fallback vectors."""
    from app.ai.embeddings.encoder import EXPECTED_EMBEDDING_DIMENSION, embedding_encoder

    vector = embedding_encoder.model.encode(
        text[:EMBEDDING_TEXT_CHARS],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    values = vector.tolist()
    if len(values) != EXPECTED_EMBEDDING_DIMENSION:
        raise ValueError(
            f"Technical source embedding dimension {len(values)} did not match "
            f"the configured dimension {EXPECTED_EMBEDDING_DIMENSION}."
        )
    return values


def refresh_technical_sources(
    resource_specs: Iterable[Dict[str, str]],
    *,
    collection: Any = None,
    embed: Optional[Callable[[str], List[float]]] = None,
    fetch: Callable[[str, Optional[Dict[str, str]]], FetchResponse] = fetch_official_page,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Fetch and upsert the allowlisted official references into section-aware, bounded overlapping chunks."""
    collection = collection or _default_collection()
    embed = embed or _default_embed
    checked_at = _utc_datetime(now)
    summary: Dict[str, Any] = {
        "checked_at": checked_at.isoformat(),
        "refreshed": 0,
        "not_modified": 0,
        "failed": 0,
        "results": [],
    }

    if collection is None:
        summary["failed"] = len(list(resource_specs))
        summary["error"] = "ChromaDB collection unavailable"
        return summary

    for spec in resource_specs:
        source_id = str(spec.get("id") or "").strip()
        url = str(spec.get("canonical_url") or "").strip()
        if not source_id or not _is_allowed_source_url(url):
            summary["failed"] += 1
            summary["results"].append({
                "id": source_id or None,
                "status": "failed",
                "error": "Missing ID or URL is not on the approved HTTPS allowlist.",
            })
            continue

        primary_rec_id = f"technical:{source_id}"
        previous_metadata, previous_document = _get_existing_record(collection, primary_rec_id)
        conditional_headers: Dict[str, str] = {}
        if previous_metadata.get("etag"):
            conditional_headers["If-None-Match"] = str(previous_metadata["etag"])
        if previous_metadata.get("source_last_modified_header"):
            conditional_headers["If-Modified-Since"] = str(
                previous_metadata["source_last_modified_header"]
            )

        try:
            response = fetch(url, conditional_headers)
            if response.status_code == 304 and previous_document:
                metadata = dict(previous_metadata)
                metadata["last_checked_at"] = checked_at.isoformat()
                metadata["checked_at_epoch"] = checked_at.timestamp()
                if response.headers.get("Last-Modified"):
                    metadata["source_last_modified"] = (
                        _parse_source_last_modified(response.headers["Last-Modified"])
                        or metadata.get("source_last_modified", "")
                    )
                    metadata["source_last_modified_header"] = response.headers["Last-Modified"]
                collection.update(ids=[primary_rec_id], metadatas=[metadata])
                summary["not_modified"] += 1
                summary["results"].append({"id": source_id, "status": "not_modified"})
                continue

            if response.status_code < 200 or response.status_code >= 300:
                raise ValueError(f"Unexpected HTTP status {response.status_code}.")
            if not _is_allowed_source_url(response.final_url):
                raise ValueError("Fetched URL is not on the approved HTTPS allowlist.")

            sections = extract_structured_sections(response.body)
            chunks = chunk_sections(sections, chunk_size=CHUNK_SIZE_CHARS, overlap=CHUNK_OVERLAP_CHARS)
            if not chunks or (len(chunks) == 1 and not chunks[0].text):
                raw_doc = extract_visible_text(response.body)
                if len(raw_doc) < 40:
                    raise ValueError("Fetched page did not contain enough readable text.")
                chunks = [DocumentChunk(chunk_index=0, section_heading="Overview", text=raw_doc[:MAX_SOURCE_TEXT_CHARS])]

            last_modified_header = response.headers.get("Last-Modified")
            etag = response.headers.get("ETag")
            parsed_last_mod = _parse_source_last_modified(last_modified_header) if last_modified_header else None

            chunk_ids: List[str] = []
            chunk_embeddings: List[List[float]] = []
            chunk_metadatas: List[Dict[str, Any]] = []
            chunk_documents: List[str] = []

            for chunk in chunks:
                chunk_rec_id = f"technical:{source_id}#chunk_{chunk.chunk_index}"
                chunk_emb = embed(chunk.text)
                chunk_meta: Dict[str, Any] = {
                    "resource_id": source_id,
                    "chunk_index": chunk.chunk_index,
                    "total_chunks": len(chunks),
                    "section_heading": chunk.section_heading,
                    "title": str(spec.get("title") or source_id),
                    "source": str(spec.get("source") or "Official documentation"),
                    "canonical_url": url,
                    "last_checked_at": checked_at.isoformat(),
                    "checked_at_epoch": checked_at.timestamp(),
                    "content_sha256": hashlib.sha256(chunk.text.encode("utf-8")).hexdigest(),
                    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                }
                if parsed_last_mod:
                    chunk_meta["source_last_modified"] = parsed_last_mod
                if last_modified_header:
                    chunk_meta["source_last_modified_header"] = last_modified_header
                if etag:
                    chunk_meta["etag"] = etag

                chunk_ids.append(chunk_rec_id)
                chunk_embeddings.append(chunk_emb)
                chunk_metadatas.append(chunk_meta)
                chunk_documents.append(chunk.text)

            # Ensure backward-compatible primary record
            chunk_ids.append(primary_rec_id)
            chunk_embeddings.append(chunk_embeddings[0])
            primary_meta = dict(chunk_metadatas[0])
            primary_meta["is_primary_index"] = True
            chunk_metadatas.append(primary_meta)
            chunk_documents.append(chunk_documents[0])

            collection.upsert(
                ids=chunk_ids,
                embeddings=chunk_embeddings,
                metadatas=chunk_metadatas,
                documents=chunk_documents,
            )
            summary["refreshed"] += 1
            summary["results"].append({"id": source_id, "status": "refreshed", "chunks": len(chunks)})
        except Exception as exc:
            summary["failed"] += 1
            summary["results"].append({
                "id": source_id,
                "status": "failed",
                "error": str(exc),
            })

    return summary


def search_fresh_technical_sources(
    query: str,
    *,
    top_k: int = 4,
    collection: Any = None,
    embed: Optional[Callable[[str], List[float]]] = None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return only sources successfully checked within the configured freshness window."""
    if not query or not query.strip():
        return {"status": "not_refreshed", "sources": []}

    collection = collection or _default_collection()
    embed = embed or _default_embed
    if collection is None or collection.count() == 0:
        return {"status": "not_refreshed", "sources": []}

    cutoff = _utc_datetime(now) - timedelta(days=TECHNICAL_SOURCE_MAX_AGE_DAYS)
    result = collection.query(
        query_embeddings=[embed(query.strip())],
        n_results=max(1, min(top_k * 2, 25)),
        where={"checked_at_epoch": {"$gte": cutoff.timestamp()}},
        include=["metadatas", "documents", "distances"],
    )

    ids = (result.get("ids") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    documents = (result.get("documents") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]
    sources: List[Dict[str, Any]] = []
    seen_headings: Set[str] = set()

    for record_id, metadata, document, distance in zip(ids, metadatas, documents, distances):
        metadata = metadata or {}
        similarity = max(0.0, min(1.0, 1.0 - float(distance)))
        if similarity < MIN_TECHNICAL_SOURCE_SIMILARITY:
            continue

        res_id = str(metadata.get("resource_id") or record_id)
        sec_heading = str(metadata.get("section_heading") or "")
        heading_key = f"{res_id}::{sec_heading}"
        if heading_key in seen_headings:
            continue
        seen_headings.add(heading_key)

        sources.append({
            "id": res_id,
            "record_id": record_id,
            "title": str(metadata.get("title") or "Technical reference"),
            "section_heading": sec_heading,
            "chunk_index": int(metadata.get("chunk_index", 0)),
            "source": str(metadata.get("source") or "Official documentation"),
            "canonical_url": str(metadata.get("canonical_url") or ""),
            "last_checked_at": str(metadata.get("last_checked_at") or ""),
            "source_last_modified": str(metadata.get("source_last_modified") or ""),
            "freshness_status": "fresh",
            "similarity_score": similarity,
            "excerpt": str(document or "")[:1200],
        })
        if len(sources) >= top_k:
            break

    if sources:
        return {"status": "fresh", "sources": sources}
    if ids:
        return {"status": "no_matching_fresh_sources", "sources": []}
    return {
        "status": "stale" if collection.count() else "not_refreshed",
        "sources": [],
    }


def render_technical_sources_context(search_result: Dict[str, Any]) -> str:
    """Render concise, dated citation data for an LLM prompt."""
    sources = search_result.get("sources") or []
    if not sources:
        status = str(search_result.get("status") or "unavailable")
        if status == "no_matching_fresh_sources":
            return (
                "## Technical source freshness\n"
                "Fresh official documentation exists, but none matched this topic closely enough to cite."
            )
        return (
            "## Technical source freshness\n"
            f"No freshly checked technical documentation was available (status: {status}). "
            "Do not claim that external technical guidance is current or cite an unverified source."
        )

    lines = ["## Fresh technical references (verified by successful refresh)"]
    for index, source in enumerate(sources, start=1):
        updated = source.get("source_last_modified") or "source update date not reported"
        heading_part = f" § {source['section_heading']}" if source.get("section_heading") else ""
        lines.extend([
            f"[{index}] {source.get('title')}{heading_part} — {source.get('source')}",
            f"URL: {source.get('canonical_url')}",
            f"Checked: {source.get('last_checked_at')}; source last modified: {updated}",
            f"Relevant excerpt: {source.get('excerpt')}",
        ])
    return "\n".join(lines)

