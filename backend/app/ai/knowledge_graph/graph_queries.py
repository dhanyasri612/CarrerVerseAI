import logging
from typing import Any, Dict, List, Optional

from app.ai.knowledge_graph.neo4j_client import Neo4jClient, neo4j_client
from app.schemas.knowledge_graph import (
    CandidateCertificationItem,
    CandidateEducationItem,
    CandidateExperienceItem,
    CandidateGraphNode,
    CandidateProjectItem,
    CandidateSkillItem,
    CandidateSubgraphResponse,
)

logger = logging.getLogger("careerverse.ai.knowledge_graph.queries")


class CandidateGraphQueries:
    """
    Reusable retrieval service for querying the Neo4j candidate knowledge graph.
    All Cypher queries are parameterized and return typed Pydantic models.
    """

    def __init__(self, client: Neo4jClient = neo4j_client):
        self.client = client

    def _get_fallback_subgraph_from_db(self, candidate_id: int) -> Optional[CandidateSubgraphResponse]:
        """
        Builds a CandidateSubgraphResponse from SQL database and Unified Profile
        when Neo4j is offline or has not synced this candidate yet.
        """
        try:
            from app.database.database import sessionLocal
            from app.models.user import User
            from app.services.unified_profile_service import build_unified_candidate_profile

            with sessionLocal() as db:
                user = db.query(User).filter(User.id == int(candidate_id)).first()
                if not user:
                    return None

                prof = build_unified_candidate_profile(db, user)

                candidate_node = CandidateGraphNode(
                    candidate_id=user.id,
                    name=getattr(user, "name", None) or getattr(user, "full_name", None) or "Candidate",
                    email=user.email or "",
                    primary_role=getattr(user, "target_role", None) or "Software Developer",
                )

                skills = [
                    CandidateSkillItem(
                        name=us.name,
                        category=us.category or "General",
                        confidence_score=float(us.confidence_score or 0.85),
                        supporting_sources_count=int(us.supporting_sources_count or len(us.sources) or 1),
                        sources=us.sources or ["Verified Profile"],
                    )
                    for us in prof.unified_skills
                ]

                projects = [
                    CandidateProjectItem(
                        project_id=str(getattr(p, "id", None) or (idx + 1)),
                        title=getattr(p, "title", "Project"),
                        description=getattr(p, "description", "") or "",
                        source=getattr(p, "source", "GitHub"),
                        url=getattr(p, "url", None),
                        stars=int(getattr(p, "stars", 0) or 0),
                        technologies=getattr(p, "technologies", []) or [],
                    )
                    for idx, p in enumerate(prof.projects or [])
                ]

                cert_items = getattr(prof.certifications_summary, "items", []) if getattr(prof, "certifications_summary", None) else []
                certifications = [
                    CandidateCertificationItem(
                        certification_id=str(c.get("id") if isinstance(c, dict) else getattr(c, "id", idx + 1)),
                        name=str(c.get("certification_name") if isinstance(c, dict) else getattr(c, "certification_name", getattr(c, "name", "Certification"))),
                        issuing_organization=str(c.get("issuing_organization") if isinstance(c, dict) else getattr(c, "issuing_organization", "Verified Organization") or "Verified Organization"),
                        issue_date=str(c.get("issue_date") if isinstance(c, dict) else getattr(c, "issue_date", "") or "") or None,
                        credential_id=c.get("credential_id") if isinstance(c, dict) else getattr(c, "credential_id", None),
                        credential_url=c.get("credential_url") if isinstance(c, dict) else getattr(c, "credential_url", None),
                        verification_status=c.get("verification_status") if isinstance(c, dict) else getattr(c, "verification_status", "UNVERIFIED"),
                        confidence_score=float(c.get("confidence_score") if isinstance(c, dict) else getattr(c, "confidence_score", 0.5) or 0.5),
                    )
                    for idx, c in enumerate(cert_items or [])
                ]

                education = [
                    CandidateEducationItem(
                        education_id=str(getattr(e, "id", None) or (idx + 1)),
                        institution=getattr(e, "institution", "University") or "University",
                        degree=getattr(e, "degree", None),
                        field_of_study=getattr(e, "field_of_study", None),
                        grade=str(getattr(e, "grade", getattr(e, "graduation_year", None)) or "") or None,
                    )
                    for idx, e in enumerate(prof.education or [])
                ]

                experience = [
                    CandidateExperienceItem(
                        experience_id=str(getattr(exp, "id", None) or (idx + 1)),
                        company=getattr(exp, "company", "Company") or "Company",
                        role=getattr(exp, "role", "Engineer") or "Engineer",
                        duration=getattr(exp, "duration", None),
                        description=getattr(exp, "description", None),
                        technologies=getattr(exp, "technologies", []) or [],
                    )
                    for idx, exp in enumerate(prof.experience or [])
                ]

                technologies = list({
                    s.name for s in skills
                } | {
                    t for p in projects for t in p.technologies
                })

                return CandidateSubgraphResponse(
                    candidate=candidate_node,
                    skills=skills,
                    projects=projects,
                    certifications=certifications,
                    education=education,
                    experience=experience,
                    technologies=technologies,
                )
        except Exception as exc:
            logger.warning("Error building fallback subgraph from SQL database for Candidate ID %d: %s", candidate_id, exc)
            return None

    # ----------------------------------------------------
    # 1. Get Candidate Node
    # ----------------------------------------------------
    def get_candidate(self, candidate_id: int) -> Optional[CandidateGraphNode]:
        """
        Retrieves the root Candidate graph node properties by candidate ID.
        Returns None if candidate does not exist.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})
        RETURN properties(c) AS candidate
        """
        records = self.client.execute_query(query, {"candidate_id": int(candidate_id)})
        if not records or not records[0].get("candidate"):
            fallback = self._get_fallback_subgraph_from_db(candidate_id)
            if fallback:
                return fallback.candidate
            return None
        return CandidateGraphNode.model_validate(records[0]["candidate"])

    # ----------------------------------------------------
    # 2. Get Candidate Skills
    # ----------------------------------------------------
    def get_candidate_skills(self, candidate_id: int) -> List[CandidateSkillItem]:
        """
        Retrieves all verified and multi-source skills connected to the candidate via HAS_SKILL,
        ordered by confidence score descending.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_SKILL]->(s:Skill)
        RETURN s.name AS name,
               coalesce(s.category, 'General') AS category,
               coalesce(r.confidence_score, 0.5) AS confidence_score,
               coalesce(r.supporting_sources_count, 1) AS supporting_sources_count,
               coalesce(r.sources, []) AS sources
        ORDER BY r.confidence_score DESC, s.name ASC
        """
        records = self.client.execute_query(query, {"candidate_id": int(candidate_id)})
        results = [CandidateSkillItem.model_validate(r) for r in records]
        if not results:
            fallback = self._get_fallback_subgraph_from_db(candidate_id)
            if fallback and fallback.skills:
                return fallback.skills
        return results

    # ----------------------------------------------------
    # 3. Get Candidate Projects
    # ----------------------------------------------------
    def get_candidate_projects(self, candidate_id: int) -> List[CandidateProjectItem]:
        """
        Retrieves all technical projects linked to the candidate via HAS_PROJECT,
        along with their connected USES_TECHNOLOGY technologies.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_PROJECT]->(p:Project)
        RETURN p.project_id AS project_id,
               p.title AS title,
               p.description AS description,
               p.source AS source,
               p.url AS url,
               coalesce(p.stars, 0) AS stars,
               [(p)-[:USES_TECHNOLOGY]->(t:Technology) | t.name] AS technologies
        ORDER BY p.title ASC
        """
        records = self.client.execute_query(query, {"candidate_id": int(candidate_id)})
        return [CandidateProjectItem.model_validate(r) for r in records]

    # ----------------------------------------------------
    # 4. Get Candidate Certifications
    # ----------------------------------------------------
    def get_candidate_certifications(self, candidate_id: int) -> List[CandidateCertificationItem]:
        """
        Retrieves all certifications linked to the candidate via HAS_CERTIFICATION.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_CERTIFICATION]->(cert:Certification)
        RETURN cert.certification_id AS certification_id,
               cert.name AS name,
               cert.issuing_organization AS issuing_organization,
               cert.issue_date AS issue_date,
               cert.credential_id AS credential_id,
               cert.credential_url AS credential_url,
               cert.source AS source,
               coalesce(r.verification_status, cert.verification_status, 'UNVERIFIED') AS verification_status,
               coalesce(r.confidence_score, cert.confidence_score, 0.5) AS confidence_score
        ORDER BY cert.name ASC
        """
        records = self.client.execute_query(query, {"candidate_id": int(candidate_id)})
        return [CandidateCertificationItem.model_validate(r) for r in records]

    # ----------------------------------------------------
    # 5. Get Candidate Education
    # ----------------------------------------------------
    def get_candidate_education(self, candidate_id: int) -> List[CandidateEducationItem]:
        """
        Retrieves education milestones linked to the candidate via HAS_EDUCATION.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_EDUCATION]->(edu:Education)
        RETURN edu.education_id AS education_id,
               edu.institution AS institution,
               edu.degree AS degree,
               edu.field_of_study AS field_of_study,
               edu.start_date AS start_date,
               edu.end_date AS end_date,
               edu.grade AS grade
        ORDER BY edu.institution ASC
        """
        records = self.client.execute_query(query, {"candidate_id": int(candidate_id)})
        return [CandidateEducationItem.model_validate(r) for r in records]

    # ----------------------------------------------------
    # 6. Get Candidate Experience
    # ----------------------------------------------------
    def get_candidate_experience(self, candidate_id: int) -> List[CandidateExperienceItem]:
        """
        Retrieves professional work experiences linked via HAS_EXPERIENCE.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_EXPERIENCE]->(e:Experience)
        RETURN e.experience_id AS experience_id,
               e.company AS company,
               e.role AS role,
               e.duration AS duration,
               e.description AS description,
               [(e)-[:USES_TECHNOLOGY]->(t:Technology) | t.name] AS technologies
        ORDER BY e.company ASC
        """
        records = self.client.execute_query(query, {"candidate_id": int(candidate_id)})
        return [CandidateExperienceItem.model_validate(r) for r in records]

    # ----------------------------------------------------
    # 7. Get Candidate Technologies
    # ----------------------------------------------------
    def get_candidate_technologies(self, candidate_id: int) -> List[str]:
        """
        Retrieves distinct technology tags utilized across the candidate's projects and experiences.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})
        OPTIONAL MATCH (c)-[:HAS_PROJECT]->(p:Project)-[:USES_TECHNOLOGY]->(t1:Technology)
        WHERE t1.name IS NOT NULL
        OPTIONAL MATCH (c)-[:HAS_EXPERIENCE]->(e:Experience)-[:USES_TECHNOLOGY]->(t2:Technology)
        WHERE t2.name IS NOT NULL
        WITH [x IN collect(DISTINCT t1.name) WHERE x IS NOT NULL] + [y IN collect(DISTINCT t2.name) WHERE y IS NOT NULL] AS all_techs
        UNWIND all_techs AS tech
        WITH DISTINCT tech WHERE tech IS NOT NULL
        RETURN tech
        ORDER BY tech ASC
        """
        records = self.client.execute_query(query, {"candidate_id": int(candidate_id)})
        return [r["tech"] for r in records if "tech" in r and r["tech"]]

    # ----------------------------------------------------
    # 8. Get Projects Using Technology
    # ----------------------------------------------------
    def get_projects_using_technology(
        self,
        candidate_id: int,
        technology: str,
    ) -> List[CandidateProjectItem]:
        """
        Queries candidate projects that utilize a specific technology (case-insensitive).
        """
        if not technology or not technology.strip():
            return []

        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_PROJECT]->(p:Project)
        MATCH (p)-[:USES_TECHNOLOGY]->(t:Technology)
        WHERE toLower(trim(t.name)) = toLower(trim($technology))
        RETURN p.project_id AS project_id,
               p.title AS title,
               p.description AS description,
               p.source AS source,
               p.url AS url,
               coalesce(p.stars, 0) AS stars,
               [(p)-[:USES_TECHNOLOGY]->(all_t:Technology) | all_t.name] AS technologies
        ORDER BY p.title ASC
        """
        records = self.client.execute_query(
            query,
            {"candidate_id": int(candidate_id), "technology": technology.strip()},
        )
        return [CandidateProjectItem.model_validate(r) for r in records]


    # ----------------------------------------------------
    # 9. Get Skills By Category
    # ----------------------------------------------------
    def get_skills_by_category(
        self,
        candidate_id: int,
        category: str,
    ) -> List[CandidateSkillItem]:
        """
        Queries candidate skills within a specific taxonomy category (case-insensitive).
        """
        if not category or not category.strip():
            return []

        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_SKILL]->(s:Skill)
        WHERE toLower(trim(s.category)) = toLower(trim($category))
        RETURN s.name AS name,
               s.category AS category,
               coalesce(r.confidence_score, 0.5) AS confidence_score,
               coalesce(r.supporting_sources_count, 1) AS supporting_sources_count,
               coalesce(r.sources, []) AS sources
        ORDER BY r.confidence_score DESC, s.name ASC
        """
        records = self.client.execute_query(
            query,
            {"candidate_id": int(candidate_id), "category": category.strip()},
        )
        return [CandidateSkillItem.model_validate(r) for r in records]

    # ----------------------------------------------------
    # 10. Get Full Candidate Subgraph
    # ----------------------------------------------------
    def get_candidate_subgraph(self, candidate_id: int) -> Optional[CandidateSubgraphResponse]:
        """
        Retrieves the complete structured knowledge graph subgraph for a candidate.
        Falls back to the SQL Unified Profile if Neo4j graph is empty or offline.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})
        RETURN properties(c) AS candidate
        """
        records = self.client.execute_query(query, {"candidate_id": int(candidate_id)})
        if not records or not records[0].get("candidate"):
            return self._get_fallback_subgraph_from_db(candidate_id)

        candidate = CandidateGraphNode.model_validate(records[0]["candidate"])
        skills = self.get_candidate_skills(candidate_id)
        projects = self.get_candidate_projects(candidate_id)
        certifications = self.get_candidate_certifications(candidate_id)
        education = self.get_candidate_education(candidate_id)
        experience = self.get_candidate_experience(candidate_id)
        technologies = self.get_candidate_technologies(candidate_id)

        if not skills:
            fallback = self._get_fallback_subgraph_from_db(candidate_id)
            if fallback and fallback.skills:
                return fallback

        return CandidateSubgraphResponse(
            candidate=candidate,
            skills=skills,
            projects=projects,
            certifications=certifications,
            education=education,
            experience=experience,
            technologies=technologies,
        )


# Global singleton query service
candidate_graph_queries = CandidateGraphQueries()
GraphQueryService = CandidateGraphQueries
graph_query_service = candidate_graph_queries
