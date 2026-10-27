import unittest
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

_SOURCE_MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "ai"
    / "rag"
    / "technical_sources.py"
)
_SPEC = spec_from_file_location("careerverse_technical_sources_tested", _SOURCE_MODULE_PATH)
_TECHNICAL_SOURCES = module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _TECHNICAL_SOURCES
_SPEC.loader.exec_module(_TECHNICAL_SOURCES)

FetchResponse = _TECHNICAL_SOURCES.FetchResponse
build_resource_specs = _TECHNICAL_SOURCES.build_resource_specs
extract_visible_text = _TECHNICAL_SOURCES.extract_visible_text
fetch_official_page = _TECHNICAL_SOURCES.fetch_official_page
refresh_technical_sources = _TECHNICAL_SOURCES.refresh_technical_sources
render_technical_sources_context = _TECHNICAL_SOURCES.render_technical_sources_context
search_fresh_technical_sources = _TECHNICAL_SOURCES.search_fresh_technical_sources


class FakeCollection:
    def __init__(self):
        self.records = {}
        self.distance = 0.1

    def get(self, ids, include):
        rows = [(record_id, self.records[record_id]) for record_id in ids if record_id in self.records]
        return {
            "ids": [record_id for record_id, _ in rows],
            "metadatas": [record["metadata"] for _, record in rows],
            "documents": [record["document"] for _, record in rows],
        }

    def upsert(self, ids, embeddings, metadatas, documents):
        for record_id, embedding, metadata, document in zip(ids, embeddings, metadatas, documents):
            self.records[record_id] = {
                "embedding": embedding,
                "metadata": dict(metadata),
                "document": document,
            }

    def update(self, ids, metadatas):
        for record_id, metadata in zip(ids, metadatas):
            self.records[record_id]["metadata"] = dict(metadata)

    def count(self):
        return len(self.records)

    def query(self, query_embeddings, n_results, where, include):
        cutoff = where["checked_at_epoch"]["$gte"]
        rows = [
            (record_id, record)
            for record_id, record in self.records.items()
            if record["metadata"]["checked_at_epoch"] >= cutoff
        ][:n_results]
        return {
            "ids": [[record_id for record_id, _ in rows]],
            "metadatas": [[record["metadata"] for _, record in rows]],
            "documents": [[record["document"] for _, record in rows]],
            "distances": [[self.distance for _ in rows]],
        }


class TechnicalSourceSyncTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 17, 12, tzinfo=timezone.utc)
        self.collection = FakeCollection()
        self.spec = {
            "id": "python-async",
            "title": "Python asyncio documentation",
            "canonical_url": "https://docs.python.org/3/library/asyncio.html",
            "source": "Python Software Foundation",
        }

    def test_extract_visible_text_omits_script_and_navigation(self):
        text = extract_visible_text(
            "<html><nav>Navigation</nav><main><h1>Async I/O</h1>"
            "<p>Event loop and coroutines.</p><script>fake advice</script></main></html>"
        )
        self.assertIn("Async I/O", text)
        self.assertIn("Event loop and coroutines.", text)
        self.assertNotIn("Navigation", text)
        self.assertNotIn("fake advice", text)

    def test_catalog_flattener_keeps_only_allowlisted_official_urls(self):
        specs = build_resource_specs({
            "python": [
                self.spec,
                {**self.spec, "id": "unsafe", "canonical_url": "http://127.0.0.1/internal"},
            ]
        })
        self.assertEqual([spec["id"] for spec in specs], ["python-async"])

    def test_fetch_rejects_non_allowlisted_url_before_network_access(self):
        with self.assertRaisesRegex(ValueError, "allowlist"):
            fetch_official_page("http://127.0.0.1/private")

    def test_empty_source_index_reports_not_refreshed(self):
        search = search_fresh_technical_sources(
            "Python asyncio",
            collection=self.collection,
            embed=lambda text: self.fail("An empty source index should not load embeddings."),
            now=self.now,
        )
        self.assertEqual(search, {"status": "not_refreshed", "sources": []})

    def test_refresh_stores_source_dates_and_search_returns_fresh_citation(self):
        response = FetchResponse(
            status_code=200,
            body="<main><h1>Async I/O</h1><p>Use coroutines with an event loop.</p></main>",
            headers={
                "ETag": '"rev-12"',
                "Last-Modified": "Fri, 16 Oct 2026 10:00:00 GMT",
            },
            final_url=self.spec["canonical_url"],
        )
        result = refresh_technical_sources(
            [self.spec],
            collection=self.collection,
            embed=lambda text: [0.25] * 384,
            fetch=lambda url, headers: response,
            now=self.now,
        )

        self.assertEqual(result["refreshed"], 1)
        stored = self.collection.records["technical:python-async"]
        self.assertEqual(stored["metadata"]["last_checked_at"], self.now.isoformat())
        self.assertEqual(stored["metadata"]["source_last_modified"], "2026-10-16T10:00:00+00:00")
        self.assertEqual(stored["metadata"]["etag"], '"rev-12"')

        search = search_fresh_technical_sources(
            "asyncio event loop",
            collection=self.collection,
            embed=lambda text: [0.25] * 384,
            now=self.now,
        )
        self.assertEqual(search["status"], "fresh")
        self.assertEqual(search["sources"][0]["canonical_url"], self.spec["canonical_url"])
        self.assertIn("event loop", search["sources"][0]["excerpt"])
        context = render_technical_sources_context(search)
        self.assertIn(self.spec["canonical_url"], context)
        self.assertIn("2026-10-16", context)

    def test_stale_documents_are_not_returned_as_current(self):
        old_time = self.now - timedelta(days=31)
        refresh_technical_sources(
            [self.spec],
            collection=self.collection,
            embed=lambda text: [0.25] * 384,
            fetch=lambda url, headers: FetchResponse(
                200,
                "<main><p>Current API documentation with enough readable content.</p></main>",
                {},
                self.spec["canonical_url"],
            ),
            now=old_time,
        )
        search = search_fresh_technical_sources(
            "API documentation",
            collection=self.collection,
            embed=lambda text: [0.25] * 384,
            now=self.now,
        )
        self.assertEqual(search["status"], "stale")
        self.assertEqual(search["sources"], [])
        self.assertIn("No freshly checked", render_technical_sources_context(search))

    def test_unrelated_fresh_document_is_not_cited_as_topic_guidance(self):
        refresh_technical_sources(
            [self.spec],
            collection=self.collection,
            embed=lambda text: [0.25] * 384,
            fetch=lambda url, headers: FetchResponse(
                200,
                "<main><p>Official coroutines documentation with enough readable content.</p></main>",
                {},
                self.spec["canonical_url"],
            ),
            now=self.now,
        )
        self.collection.distance = 0.95
        search = search_fresh_technical_sources(
            "unrelated topic",
            collection=self.collection,
            embed=lambda text: [0.25] * 384,
            now=self.now,
        )
        self.assertEqual(search["status"], "no_matching_fresh_sources")
        self.assertEqual(search["sources"], [])
        self.assertIn("none matched this topic", render_technical_sources_context(search))

    def test_not_modified_response_keeps_document_and_advances_check_time(self):
        self.collection.upsert(
            ids=["technical:python-async"],
            embeddings=[[0.25] * 384],
            metadatas=[{
                "resource_id": "python-async",
                "title": self.spec["title"],
                "source": self.spec["source"],
                "canonical_url": self.spec["canonical_url"],
                "last_checked_at": "2026-10-10T12:00:00+00:00",
                "checked_at_epoch": (self.now - timedelta(days=7)).timestamp(),
                "etag": '"rev-12"',
            }],
            documents=["Previously fetched official documentation content."],
        )
        result = refresh_technical_sources(
            [self.spec],
            collection=self.collection,
            embed=lambda text: self.fail("A 304 response should not trigger re-embedding."),
            fetch=lambda url, headers: (
                self.assertEqual(headers["If-None-Match"], '"rev-12"')
                or FetchResponse(304, "", {}, url)
            ),
            now=self.now,
        )
        stored = self.collection.records["technical:python-async"]
        self.assertEqual(result["not_modified"], 1)
        self.assertEqual(stored["document"], "Previously fetched official documentation content.")
        self.assertEqual(stored["metadata"]["checked_at_epoch"], self.now.timestamp())


if __name__ == "__main__":
    unittest.main()
