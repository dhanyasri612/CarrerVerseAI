# Neo4j Knowledge Graph Engine (`app/ai/knowledge_graph`)

The `app/ai/knowledge_graph` module models candidate competencies, career trajectories, and organizational dependencies as an explicit graph network inside **Neo4j**. While vector search captures unstructured semantic similarity, the knowledge graph provides **deterministic relational reasoning** and **multi-hop path traversal**.

---

## 🕸️ Graph Schema: Nodes & Relationships

```
              ┌──────────────┐
              │  Candidate   │ (candidate_id: UNIQUE)
              └──┬───┬───┬───┘
                 │   │   │
      HAS_SKILL  │   │   │  WORKED_AT
         ┌───────┘   │   └────────┐
         ▼           ▼            ▼
     ┌───────┐  WORKED_ON    ┌────────────┐
     │ Skill │   ┌───────┐   │ Experience │
     └───┬───┘   │Project│   └─────┬──────┘
         │       └───┬───┘         │
         │ REQUIRES  │ USES        │ INVOLVES
         ▼           ▼             ▼
     ┌────────────────────────────────────┐
     │             Technology             │
     └────────────────────────────────────┘
```

### Node Labels
- `:Candidate`: Authenticated candidate profile with ID, name, email, and metadata.
- `:Skill`: Specific competencies (e.g., `Python`, `FastAPI`, `Distributed Systems`).
- `:Technology`: Concrete frameworks, tools, and libraries (e.g., `Docker`, `PostgreSQL`, `Kafka`).
- `:Project`: Verified candidate projects (e.g., from resume, GitHub repos).
- `:Experience`: Employment roles and job experiences.
- `:Education`: Academic background, degree, and institution.
- `:Certification`: Verified credentials and certificates.

### Relationship Types
- `(:Candidate)-[:HAS_SKILL {source, confidence}]->(:Skill)`
- `(:Candidate)-[:WORKED_ON]->(:Project)`
- `(:Candidate)-[:WORKED_AT]->(:Experience)`
- `(:Project)-[:USES_TECHNOLOGY]->(:Technology)`
- `(:Experience)-[:UTILIZED_SKILL]->(:Skill)`
- `(:Skill)-[:RELATED_TO]->(:Skill)`

---

## 🛠️ Module Components

| File | Purpose |
| :--- | :--- |
| **`neo4j_client.py`** | Manages persistent Neo4j Driver lifecycle over Bolt protocol (`bolt://localhost:7687`), session acquisition, connectivity verification, and database constraints. |
| **`graph_builder.py`** | Translates parsed resumes and multi-source candidate profiles into idempotent Cypher `MERGE` queries, updating the graph atomically. |
| **`graph_queries.py`** | Pre-compiled Cypher queries for candidate context extraction, skill graph neighborhoods, missing skill paths, and tenant-isolated retrieval. |

---

## 🔒 Tenant Isolation in Cypher Queries

To guarantee that candidate data is never exposed across users, every Cypher read and traversal enforces a candidate boundary parameter:

```cypher
MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_SKILL]->(s:Skill)
OPTIONAL MATCH (c)-[:WORKED_ON]->(p:Project)-[:USES_TECHNOLOGY]->(t:Technology)
RETURN s.name AS skill, r.source AS source, collect(DISTINCT t.name) AS technologies
```

No node or edge can be traversed without originating from the authenticated `Candidate` root node.
