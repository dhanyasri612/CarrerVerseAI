import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.ai.knowledge_graph.graph_queries import CandidateGraphQueries, candidate_graph_queries
from app.ai.vector_store.semantic_search import SemanticSearchEngine, semantic_search_engine
from app.ai.rag.technical_sources import (
    render_technical_sources_context,
    search_fresh_technical_sources,
)
from app.schemas.knowledge_graph import CandidateSubgraphResponse
from app.schemas.rag import RAGRetrievedContext
from app.schemas.semantic_search import SemanticSearchResultItem

logger = logging.getLogger("careerverse.ai.rag.context_builder")


class RAGContextBuilder:
    """
    Combines unstructured semantic vector retrieval (ChromaDB) and explicit relational
    knowledge graph retrieval (Neo4j) into a unified, deterministic grounding context for candidate intelligence.
    """

    def __init__(
        self,
        semantic_engine: SemanticSearchEngine = semantic_search_engine,
        graph_queries: CandidateGraphQueries = candidate_graph_queries,
    ):
        self.semantic_engine = semantic_engine
        self.graph_queries = graph_queries

    def build_retrieval_context(
        self,
        candidate_id: int,
        query: str,
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> RAGRetrievedContext:
        """
        Executes dual retrieval:
        1. Semantic vector search across candidate embeddings in ChromaDB.
        2. Knowledge graph subgraph traversal in Neo4j.
        Synthesizes a structured, deterministic grounding context without LLM inference.
        """
        logger.info("Building RAG retrieval context for Candidate ID: %d, Query: '%s'", candidate_id, query[:50])

        warnings: List[str] = []
        chroma_status = "available"
        neo4j_status = "available"
        sources: List[str] = []

        # ----------------------------------------------------
        # 1. ChromaDB Semantic Vector Retrieval (this candidate only)
        # ----------------------------------------------------
        semantic_items: List[SemanticSearchResultItem] = []
        filter_dict = where_filter or {"candidate_id": int(candidate_id)}
        try:
            owned = self.semantic_engine.vector_store.get_candidate(int(candidate_id))
            semantic_response = self.semantic_engine.search_candidates(
                query=query,
                top_k=top_k,
                where=filter_dict,
                owner_candidate_id=int(candidate_id),
            )
            semantic_items = [
                item
                for item in (semantic_response.results if semantic_response else [])
                if int(item.candidate_id) == int(candidate_id)
            ]
            if owned:
                owned_cid = int((owned.get("metadata") or {}).get("candidate_id") or candidate_id)
                if owned_cid != int(candidate_id):
                    chroma_status = "missing_vector"
                    semantic_items = []
                    warnings.append(
                        "ChromaDB document metadata did not match the authenticated candidate; ignored."
                    )
                else:
                    sources.append("chromadb")
                    if not semantic_items:
                        semantic_items = [
                            SemanticSearchResultItem(
                                id=owned["id"],
                                candidate_id=int(candidate_id),
                                similarity_score=1.0,
                                distance=0.0,
                                metadata=owned.get("metadata") or {},
                                document=owned.get("document") or "",
                            )
                        ]
            else:
                chroma_status = "missing_vector"
                semantic_items = []
                warnings.append(
                    "ChromaDB has no embedding for this candidate. Semantic retrieval is empty."
                )
        except Exception as exc:
            chroma_status = "unavailable"
            warnings.append(f"ChromaDB retrieval unavailable: {exc}")
            logger.warning("ChromaDB retrieval unavailable for candidate %s: %s", candidate_id, exc)
            semantic_items = []

        # ----------------------------------------------------
        # 2. Neo4j Knowledge Graph Subgraph Retrieval
        # ----------------------------------------------------
        graph_subgraph: Optional[CandidateSubgraphResponse] = None
        try:
            graph_subgraph = self.graph_queries.get_candidate_subgraph(candidate_id)
            if graph_subgraph and graph_subgraph.candidate:
                sources.append("neo4j")
            else:
                neo4j_status = "missing_candidate"
                warnings.append(
                    "Neo4j has no knowledge-graph node for this candidate."
                )
                graph_subgraph = None
        except Exception as exc:
            neo4j_status = "unavailable"
            warnings.append(f"Neo4j retrieval unavailable: {exc}")
            logger.warning("Neo4j retrieval unavailable for candidate %s: %s", candidate_id, exc)
            graph_subgraph = None

        # ----------------------------------------------------
        # 3. Deterministic Structured Text Synthesis
        # ----------------------------------------------------
        context_text = self._synthesize_grounded_text(
            candidate_id=candidate_id,
            query=query,
            graph_context=graph_subgraph,
            semantic_items=semantic_items,
            retrieval_warnings=warnings,
        )
        try:
            technical_result = search_fresh_technical_sources(query, top_k=4)
        except Exception as exc:
            logger.warning("Fresh technical-source retrieval unavailable: %s", exc)
            technical_result = {"status": "unavailable", "sources": []}
        context_text = (
            f"{context_text}\n\n"
            f"{render_technical_sources_context(technical_result)}"
        )

        # ----------------------------------------------------
        # 4. Metadata Compilation
        # ----------------------------------------------------
        metadata: Dict[str, Any] = {
            "candidate_id": candidate_id,
            "query": query,
            "sources": sources,
            "chroma_status": chroma_status,
            "neo4j_status": neo4j_status,
            "retrieval_warnings": warnings,
            "semantic_matches_count": len(semantic_items),
            "semantic_chunks_count": len(semantic_items),
            "graph_skills_count": len(graph_subgraph.skills) if graph_subgraph else 0,
            "graph_projects_count": len(graph_subgraph.projects) if graph_subgraph else 0,
            "graph_technologies_count": len(graph_subgraph.technologies) if graph_subgraph else 0,
            "graph_certifications_count": len(graph_subgraph.certifications) if graph_subgraph else 0,
            "graph_education_count": len(graph_subgraph.education) if graph_subgraph else 0,
            "graph_experience_count": len(graph_subgraph.experience) if graph_subgraph else 0,
            "context_text_length": len(context_text),
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "technical_source_status": technical_result.get("status", "unavailable"),
            "technical_sources": technical_result.get("sources", []),
        }

        return RAGRetrievedContext(
            candidate_id=candidate_id,
            query=query,
            semantic_results=semantic_items,
            graph_context=graph_subgraph,
            context_text=context_text,
            metadata=metadata,
        )

    def _synthesize_grounded_text(
        self,
        candidate_id: int,
        query: str,
        graph_context: Optional[CandidateSubgraphResponse],
        semantic_items: List[SemanticSearchResultItem],
        retrieval_warnings: Optional[List[str]] = None,
    ) -> str:
        """
        Synthesizes a clean, deterministic Markdown context text grounded strictly in retrieved data.
        """
        sections: List[str] = []
        sections.append(f"# CANDIDATE INTELLIGENCE RETRIEVAL CONTEXT\n**Query**: \"{query}\"")
        if retrieval_warnings:
            warn_lines = ["## Retrieval Service Status"]
            for warning in retrieval_warnings:
                warn_lines.append(f"- {warning}")
            sections.append("\n".join(warn_lines))

        if graph_context and graph_context.candidate:
            c = graph_context.candidate
            profile_lines = [
                "## 1. Candidate Overview",
                f"- **Candidate ID**: {c.candidate_id}",
                f"- **Name**: {c.name}",
                f"- **Email**: {c.email}",
            ]
            if c.degree and c.college:
                profile_lines.append(f"- **Degree & College**: {c.degree} from {c.college}")
            elif c.degree:
                profile_lines.append(f"- **Degree**: {c.degree}")
            if c.location:
                profile_lines.append(f"- **Location**: {c.location}")
            if c.summary:
                profile_lines.append(f"- **Professional Summary**: {c.summary}")
            profile_lines.append(f"- **Profile Completeness**: {c.completeness_score}%")
            sections.append("\n".join(profile_lines))

            # Skills
            if graph_context.skills:
                skill_lines = ["## 2. Verified Technical Skills (Knowledge Graph)"]
                for s in graph_context.skills:
                    conf_pct = int(s.confidence_score * 100)
                    src_str = ", ".join(s.sources) if s.sources else "verified"
                    skill_lines.append(f"- **{s.name}** ({s.category}) — Confidence: {conf_pct}% [Sources: {src_str}]")
                sections.append("\n".join(skill_lines))

            # Projects
            if graph_context.projects:
                proj_lines = ["## 3. Technical Projects Portfolio (Knowledge Graph)"]
                for p in graph_context.projects:
                    tech_str = f" | Techs: {', '.join(p.technologies)}" if p.technologies else ""
                    desc_str = f"\n  - Description: {p.description}" if p.description else ""
                    stars_str = f" ({p.stars} stars)" if p.stars else ""
                    proj_lines.append(f"- **{p.title}** (Source: {p.source}{stars_str}{tech_str}){desc_str}")
                sections.append("\n".join(proj_lines))

            # Technologies
            if graph_context.technologies:
                tech_lines = [
                    "## 4. Technologies & Tools In Use (Knowledge Graph)",
                    f"- **Active Stack**: {', '.join(graph_context.technologies)}",
                ]
                sections.append("\n".join(tech_lines))

            # Certifications
            if graph_context.certifications:
                cert_lines = ["## 5. Certifications & Credentials (Knowledge Graph)"]
                for cert in graph_context.certifications:
                    cert_lines.append(
                        f"- **{cert.name}** | Issuer: {cert.issuing_organization} | Status: {cert.verification_status}"
                    )
                sections.append("\n".join(cert_lines))

            # Education
            if graph_context.education:
                edu_lines = ["## 6. Academic Milestones (Knowledge Graph)"]
                for edu in graph_context.education:
                    edu_lines.append(
                        f"- **{edu.institution}** | Degree: {edu.degree or 'N/A'} | Field: {edu.field_of_study or 'N/A'} | Grade: {edu.grade or 'N/A'}"
                    )
                sections.append("\n".join(edu_lines))

            # Experience
            if graph_context.experience:
                exp_lines = ["## 7. Professional Work Experience (Knowledge Graph)"]
                for exp in graph_context.experience:
                    tech_str = f" | Techs: {', '.join(exp.technologies)}" if exp.technologies else ""
                    exp_lines.append(f"- **{exp.role}** at {exp.company} ({exp.duration or 'N/A'}{tech_str})")
                sections.append("\n".join(exp_lines))
        else:
            sections.append("## Knowledge Graph\n- No explicit knowledge graph records found for this candidate ID.")

        # Semantic Results
        if semantic_items:
            semantic_lines = ["## 8. Semantic Search Embeddings Relevance (ChromaDB)"]
            for idx, item in enumerate(semantic_items, start=1):
                sim_pct = int(item.similarity_score * 100)
                preview = item.document[:200].replace("\n", " ") if item.document else "N/A"
                semantic_lines.append(
                    f"- Match #{idx} [{item.id}] — Cosine Similarity: {sim_pct}% (Distance: {item.distance:.4f})\n  - Text Snippet: {preview}..."
                )
            sections.append("\n".join(semantic_lines))
        else:
            sections.append("## 8. Semantic Search Embeddings Relevance (ChromaDB)\n- No vector matches returned.")

        return "\n\n".join(sections)


# Global singleton instance
rag_context_builder = RAGContextBuilder()
