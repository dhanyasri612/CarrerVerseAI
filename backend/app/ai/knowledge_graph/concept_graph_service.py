import logging
from typing import Any, Dict, List, Optional, Set
from app.ai.knowledge_graph.neo4j_client import Neo4jClient, neo4j_client
from app.schemas.learner_knowledge import ConceptMapEdge, ConceptMapNode, ConceptMapResponse
from app.services.learner_knowledge_service import CONCEPT_PREREQUISITES

logger = logging.getLogger("careerverse.ai.knowledge_graph.concepts")

# Extended taxonomy of concept relationships
RELATED_CONCEPTS_GRAPH: Dict[str, List[str]] = {
    "arrays and hash maps": ["two pointers", "sliding window", "caching"],
    "two pointers": ["sliding window", "binary search"],
    "sliding window": ["two pointers", "arrays and hash maps"],
    "binary search": ["two pointers", "trees and graphs"],
    "trees and graphs": ["heaps", "dynamic programming"],
    "heaps": ["priority queues", "top-k frequent elements"],
    "dynamic programming": ["recursion and call stacks", "memoization and caching"],
    "python": ["fastapi", "async programming", "docker"],
    "fastapi": ["http and rest apis", "pydantic", "postgresql", "dependency injection"],
    "postgresql": ["database modeling", "transactions and indexing", "b-tree indexes"],
    "react": ["javascript", "hooks", "state management", "virtual dom"],
    "docker": ["ci/cd pipelines", "containerization", "microservices"],
    "system design": ["caching", "database modeling", "scalability and distribution", "load balancing"],
}


class ConceptGraphService:
    """
    Manages Neo4j Concept, Prerequisite, and Learning Graph modeling.
    Provides parameterized Cypher queries, constraint handling, and resilient
    offline fallbacks so visual concept maps never break.
    """

    def __init__(self, client: Neo4jClient = neo4j_client):
        self.client = client

    def sync_candidate_concept_graph(
        self,
        candidate_id: int,
        skills_inventory: Dict[str, Any],
        verified_projects: List[Dict[str, Any]],
        completed_lessons: List[str],
        mastered_lessons: List[str],
    ) -> bool:
        """
        Idempotently merges candidate concept relationships into Neo4j when available.
        """
        try:
            # 1. Merge Candidate Node
            candidate_cypher = """
            MERGE (c:Candidate {candidate_id: $candidate_id})
            RETURN c
            """
            self.client.execute_write(candidate_cypher, {"candidate_id": int(candidate_id)})

            # 2. Merge Concept Nodes & Candidate Relationships
            for c_key, rec in skills_inventory.items():
                c_name = getattr(rec, "concept_name", c_key).title()
                cat = getattr(rec, "category", "General")
                status = getattr(rec, "status", "not_started")
                conf = float(getattr(rec, "confidence_score", 0.5))
                is_gap = bool(getattr(rec, "is_knowledge_gap", False))

                concept_cypher = """
                MERGE (con:Concept {name: $concept_name})
                ON CREATE SET con.category = $category
                WITH con
                MATCH (c:Candidate {candidate_id: $candidate_id})
                MERGE (c)-[r:HAS_SKILL]->(con)
                SET r.status = $status,
                    r.confidence_score = $confidence,
                    r.is_gap = $is_gap
                """
                self.client.execute_write(
                    concept_cypher,
                    {
                        "candidate_id": int(candidate_id),
                        "concept_name": c_name,
                        "category": cat,
                        "status": status,
                        "confidence": conf,
                        "is_gap": is_gap,
                    },
                )

                # Merge Prerequisite Edges: (prereq)-[:REQUIRES]->(concept)
                for prereq in getattr(rec, "prerequisites", []):
                    prereq_name = prereq.title()
                    prereq_cypher = """
                    MERGE (p:Concept {name: $prereq_name})
                    MERGE (con:Concept {name: $concept_name})
                    MERGE (con)-[:REQUIRES]->(p)
                    """
                    self.client.execute_write(
                        prereq_cypher,
                        {"prereq_name": prereq_name, "concept_name": c_name},
                    )

            # 3. Merge Project DEMONSTRATES Concept Edges
            for proj in verified_projects:
                p_title = proj.get("title", "Project")
                p_id = str(proj.get("id") or p_title.lower())
                proj_cypher = """
                MATCH (c:Candidate {candidate_id: $candidate_id})
                MERGE (p:Project {project_id: $project_id})
                ON CREATE SET p.title = $title
                MERGE (c)-[:HAS_PROJECT]->(p)
                """
                self.client.execute_write(
                    proj_cypher,
                    {"candidate_id": int(candidate_id), "project_id": p_id, "title": p_title},
                )

                for tech in proj.get("technologies", []):
                    tech_cypher = """
                    MATCH (p:Project {project_id: $project_id})
                    MERGE (con:Concept {name: $tech_name})
                    MERGE (p)-[:DEMONSTRATES]->(con)
                    """
                    self.client.execute_write(
                        tech_cypher,
                        {"project_id": p_id, "tech_name": tech.strip().title()},
                    )

            logger.info("Successfully synchronized concept graph for candidate %d into Neo4j.", candidate_id)
            return True
        except Exception as exc:
            logger.warning("Neo4j offline or concept sync skipped for candidate %d: %s", candidate_id, exc)
            return False

    def get_concept_map(
        self,
        candidate_id: int,
        current_lesson_id: Optional[str] = None,
        skills_inventory: Optional[Dict[str, Any]] = None,
        verified_projects: Optional[List[Dict[str, Any]]] = None,
    ) -> ConceptMapResponse:
        """
        Builds an interactive concept map with nodes (concepts, projects) and edges (prerequisites, related).
        Executes Cypher when Neo4j is online, or uses deterministic relational graph synthesis when offline.
        """
        nodes: List[ConceptMapNode] = []
        edges: List[ConceptMapEdge] = []
        node_id_set: Set[str] = set()

        curr_key = (current_lesson_id or "dsa-two-sum").lower().replace("dsa-", "").replace("-", " ")

        # 1. Try querying live Neo4j instance if online
        try:
            records = self.client.execute_query(
                """
                MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_SKILL]->(con:Concept)
                OPTIONAL MATCH (con)-[:REQUIRES]->(pre:Concept)
                OPTIONAL MATCH (p:Project)-[:DEMONSTRATES]->(con)
                RETURN con.name AS concept_name,
                       con.category AS category,
                       r.status AS status,
                       r.confidence_score AS confidence,
                       r.is_gap AS is_gap,
                       collect(DISTINCT pre.name) AS prerequisites,
                       collect(DISTINCT p.title) AS projects
                LIMIT 30
                """,
                {"candidate_id": int(candidate_id)},
            )
            if records and len(records) > 0:
                for row in records:
                    c_name = row.get("concept_name", "")
                    if not c_name:
                        continue
                    n_id = c_name.lower().replace(" ", "_")
                    status = row.get("status", "not_started")
                    if row.get("is_gap"):
                        status = "gap"
                    projs = row.get("projects", [])
                    has_proj = bool(projs and len(projs) > 0)
                    is_curr = n_id in curr_key or curr_key in n_id

                    if n_id not in node_id_set:
                        node_id_set.add(n_id)
                        nodes.append(
                            ConceptMapNode(
                                id=n_id,
                                label=c_name,
                                category=row.get("category", "General"),
                                status=status,
                                difficulty="Medium",
                                confidence_score=float(row.get("confidence", 0.5)),
                                is_current=is_curr,
                                has_project_evidence=has_proj,
                                project_name=projs[0] if has_proj else None,
                            )
                        )

                    for pr in row.get("prerequisites", []):
                        if pr:
                            pr_id = pr.lower().replace(" ", "_")
                            edges.append(
                                ConceptMapEdge(
                                    source=pr_id,
                                    target=n_id,
                                    relationship="REQUIRES",
                                    label="Prerequisite For",
                                )
                            )

                lesson_concept_key = (current_lesson_id or "").lower().replace("dsa-", "").replace("-", "_")
                if lesson_concept_key and lesson_concept_key not in node_id_set:
                    node_id_set.add(lesson_concept_key)
                    nodes.append(
                        ConceptMapNode(
                            id=lesson_concept_key,
                            label=lesson_concept_key.replace("_", " ").title(),
                            category="Algorithms & DSA",
                            status="learning",
                            difficulty="Medium",
                            confidence_score=0.7,
                            is_current=True,
                            has_project_evidence=False,
                        )
                    )

                if nodes:
                    return ConceptMapResponse(
                        candidate_id=candidate_id,
                        current_concept_id=curr_key,
                        nodes=nodes,
                        edges=edges,
                        total_nodes=len(nodes),
                        total_edges=len(edges),
                    )
        except Exception as exc:
            logger.debug("Falling back to deterministic concept graph generator: %s", exc)

        # 2. Resilient Deterministic Graph Synthesis (Ensures concept map is ALWAYS functional)
        inv = skills_inventory or {}
        projs = verified_projects or []

        # Populate nodes from inventory
        for c_key, rec in inv.items():
            c_name = getattr(rec, "concept_name", c_key).title()
            cat = getattr(rec, "category", "General")
            status = getattr(rec, "status", "not_started")
            if getattr(rec, "is_knowledge_gap", False):
                status = "gap"
            conf = float(getattr(rec, "confidence_score", 0.5))
            n_id = c_key.lower().replace(" ", "_")

            # Check matching project
            matching_proj = next((p.get("title") for p in projs if any(c_key in str(t).lower() for t in p.get("technologies", []))), None)
            is_curr = n_id in curr_key or curr_key in n_id or c_key in curr_key

            if n_id not in node_id_set:
                node_id_set.add(n_id)
                nodes.append(
                    ConceptMapNode(
                        id=n_id,
                        label=c_name,
                        category=cat,
                        status=status,
                        confidence_score=conf,
                        is_current=is_curr,
                        has_project_evidence=bool(matching_proj),
                        project_name=matching_proj,
                    )
                )

        # Add prerequisite edges
        for c_key, prereqs in CONCEPT_PREREQUISITES.items():
            target_id = c_key.lower().replace(" ", "_")
            if target_id in node_id_set:
                for pr in prereqs:
                    source_id = pr.lower().replace(" ", "_")
                    if source_id not in node_id_set:
                        node_id_set.add(source_id)
                        nodes.append(
                            ConceptMapNode(
                                id=source_id,
                                label=pr.title(),
                                category="Prerequisite Foundation",
                                status="learning",
                                confidence_score=0.6,
                                is_current=False,
                            )
                        )
                    edges.append(
                        ConceptMapEdge(
                            source=source_id,
                            target=target_id,
                            relationship="REQUIRES",
                            label="Prerequisite For",
                        )
                    )

        # Add related edges
        for c_key, rels in RELATED_CONCEPTS_GRAPH.items():
            source_id = c_key.lower().replace(" ", "_")
            if source_id in node_id_set:
                for rel in rels[:2]:  # Bound edges to keep visual map clean
                    target_id = rel.lower().replace(" ", "_")
                    if target_id in node_id_set and source_id != target_id:
                        edges.append(
                            ConceptMapEdge(
                                source=source_id,
                                target=target_id,
                                relationship="RELATED_TO",
                                label="Connected Concept",
                            )
                        )

        # Ensure active lesson node is present and marked current
        curr_node_id = curr_key.lower().replace(" ", "_")
        if curr_node_id not in node_id_set:
            node_id_set.add(curr_node_id)
            nodes.insert(
                0,
                ConceptMapNode(
                    id=curr_node_id,
                    label=curr_key.title(),
                    category="Active Concept",
                    status="learning",
                    confidence_score=0.7,
                    is_current=True,
                )
            )
        else:
            for n in nodes:
                if n.id == curr_node_id:
                    n.is_current = True
                    break

        if not any(n.is_current for n in nodes) and nodes:
            nodes[0].is_current = True

        return ConceptMapResponse(
            candidate_id=candidate_id,
            current_concept_id=curr_key,
            nodes=nodes[:25],  # Keep graph readable
            edges=edges[:35],
            total_nodes=len(nodes[:25]),
            total_edges=len(edges[:35]),
        )


concept_graph_service = ConceptGraphService()
