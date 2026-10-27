from types import SimpleNamespace

from app.ai.stores.candidate_store_sync import persist_candidate_ai_stores
from app.ai.vector_store.chroma_client import ChromaVectorStore
from app.schemas.candidate_intelligence import (
    CertificationsSummary,
    GitHubSummary,
    HackerRankSummary,
    LeetCodeSummary,
    LinkedInSummary,
    ProfileCompleteness,
    ResumeSummary,
    SkillsByCategory,
    UnifiedProfileResponse,
    UserProfileSummary,
)
from app.schemas.embedding import CandidateEmbeddingOutput


def make_profile(candidate_id: int, summary: str = "Initial profile") -> UnifiedProfileResponse:
    return UnifiedProfileResponse(
        user_profile=UserProfileSummary(
            id=candidate_id,
            name=f"Candidate {candidate_id}",
            email=f"candidate-{candidate_id}@example.com",
            summary=summary,
        ),
        resume_summary=ResumeSummary(),
        github_summary=GitHubSummary(),
        linkedin_summary=LinkedInSummary(),
        leetcode_summary=LeetCodeSummary(),
        hackerrank_summary=HackerRankSummary(),
        certifications_summary=CertificationsSummary(),
        skills_by_category=[SkillsByCategory(category="Tools & Technologies")],
        completeness=ProfileCompleteness(score=0),
    )


class FakeEncoder:
    def encode_candidate(self, document):
        return CandidateEmbeddingOutput(
            user_id=document.user_id,
            global_embedding=[0.1, 0.2],
            dimension=2,
            model_name="fake",
            metadata={"candidate_id": document.user_id},
        )


class FakeVectorStore:
    def __init__(self, fail=False):
        self.fail = fail
        self.upserts = []

    def store_candidate(self, embedding, document_text=None):
        if self.fail:
            raise RuntimeError("Chroma unavailable")
        doc_id = f"candidate_{embedding.user_id}"
        self.upserts.append((doc_id, document_text))
        return doc_id

    def get_candidate(self, candidate_id):
        return {
            "id": f"candidate_{candidate_id}",
            "metadata": {"candidate_id": candidate_id},
        }


class FakeGraphBuilder:
    def __init__(self, fail=False):
        self.fail = fail
        self.rebuilds = []

    def rebuild_candidate_graph(self, profile):
        if self.fail:
            raise RuntimeError("Neo4j unavailable")
        candidate_id = profile.user_profile.id
        self.rebuilds.append(candidate_id)
        return {"counts": {"candidate_nodes": 1}}


def test_new_candidate_sync_generates_embedding_upserts_chroma_and_updates_neo4j():
    vector_store = FakeVectorStore()
    graph_builder = FakeGraphBuilder()

    result = persist_candidate_ai_stores(
        make_profile(101),
        vector_store=vector_store,
        encoder=FakeEncoder(),
        graph_builder=graph_builder,
    )

    assert result.candidate_id == 101
    assert result.chroma_status == "success"
    assert result.neo4j_status == "success"
    assert vector_store.upserts[0][0] == "candidate_101"
    assert graph_builder.rebuilds == [101]


def test_existing_candidate_update_upserts_same_id_without_duplicate_records():
    vector_store = FakeVectorStore()
    graph_builder = FakeGraphBuilder()

    persist_candidate_ai_stores(make_profile(102, "one"), vector_store=vector_store, encoder=FakeEncoder(), graph_builder=graph_builder)
    persist_candidate_ai_stores(make_profile(102, "two"), vector_store=vector_store, encoder=FakeEncoder(), graph_builder=graph_builder)

    assert [item[0] for item in vector_store.upserts] == ["candidate_102", "candidate_102"]
    assert graph_builder.rebuilds == [102, 102]


def test_chroma_failure_does_not_block_neo4j_or_raise():
    result = persist_candidate_ai_stores(
        make_profile(103),
        vector_store=FakeVectorStore(fail=True),
        encoder=FakeEncoder(),
        graph_builder=FakeGraphBuilder(),
    )

    assert result.chroma_status == "failed"
    assert result.neo4j_status == "success"
    assert "Chroma unavailable" in result.chroma_error


def test_neo4j_failure_does_not_change_chroma_result_or_raise():
    result = persist_candidate_ai_stores(
        make_profile(104),
        vector_store=FakeVectorStore(),
        encoder=FakeEncoder(),
        graph_builder=FakeGraphBuilder(fail=True),
    )

    assert result.chroma_status == "success"
    assert result.neo4j_status == "failed"
    assert "Neo4j unavailable" in result.neo4j_error


class FakeCollection:
    def __init__(self, record):
        self.record = record

    def get(self, **kwargs):
        return {
            "ids": [self.record["id"]],
            "embeddings": [[0.1]],
            "metadatas": [self.record.get("metadata")],
            "documents": ["candidate document"],
        }


def test_missing_chroma_vector_is_empty_and_wrong_candidate_is_never_fallback():
    store = ChromaVectorStore.__new__(ChromaVectorStore)
    store._collection = FakeCollection({"id": "candidate_201", "metadata": {"candidate_id": 201}})

    assert store.get_candidate(200) is None


def test_chroma_record_without_matching_metadata_is_rejected():
    store = ChromaVectorStore.__new__(ChromaVectorStore)
    store._collection = FakeCollection({"id": "candidate_200", "metadata": {"candidate_id": 201}})

    assert store.get_candidate(200) is None