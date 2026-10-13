import logging
import re
from typing import Any, Dict, List, Optional
from app.ai.knowledge_graph.neo4j_client import Neo4jClient, neo4j_client
from app.schemas.candidate_intelligence import UnifiedProfileResponse

logger = logging.getLogger("careerverse.ai.knowledge_graph.builder")


def _sanitize_identifier(text: Optional[str]) -> str:
    """Converts a raw string into a stable alphanumeric slug."""
    if not text:
        return "unknown"
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip().lower())[:60]


class CandidateGraphBuilder:
    """
    Transforms multi-source UnifiedProfileResponse candidate intelligence
    into an interconnected Knowledge Graph inside Neo4j.
    Guarantees deterministic entity deduplication, stable identifiers, and idempotency.
    """

    def __init__(self, client: Neo4jClient = neo4j_client):
        self.client = client

    def purge_candidate_owned_graph(self, candidate_id: int) -> None:
        """
        Removes this candidate's owned entities and relationships so a rebuild
        cannot accumulate duplicate HAS_SKILL / HAS_PROJECT edges.
        Shared Skill and Technology nodes are left in place.
        """
        self.client.execute_write(
            """
            MATCH (c:Candidate {candidate_id: $candidate_id})
            OPTIONAL MATCH (c)-[hs:HAS_SKILL]->(:Skill)
            DELETE hs
            WITH c
            OPTIONAL MATCH (c)-[:HAS_PROJECT]->(p:Project)
            DETACH DELETE p
            WITH c
            OPTIONAL MATCH (c)-[:HAS_CERTIFICATION]->(cert:Certification)
            DETACH DELETE cert
            WITH c
            OPTIONAL MATCH (c)-[:HAS_EXPERIENCE]->(e:Experience)
            DETACH DELETE e
            WITH c
            OPTIONAL MATCH (c)-[:HAS_EDUCATION]->(edu:Education)
            DETACH DELETE edu
            """,
            {"candidate_id": int(candidate_id)},
        )

    def rebuild_candidate_graph(self, profile: UnifiedProfileResponse) -> Dict[str, Any]:
        """Purge candidate-owned graph data, then MERGE the current unified profile."""
        candidate_id = int(profile.user_profile.id)
        try:
            self.client.init_constraints()
        except Exception as exc:
            logger.warning("Neo4j constraint init warning during rebuild: %s", exc)
        self.purge_candidate_owned_graph(candidate_id)
        return self.build_candidate_graph(profile)

    def build_candidate_graph(self, profile: UnifiedProfileResponse) -> Dict[str, Any]:
        """
        Builds or idempotently updates all nodes and explicit relationships
        for a given unified candidate profile in Neo4j.
        """
        user_profile = profile.user_profile
        candidate_id = user_profile.id

        # 1. Ensure constraints are established
        self.client.init_constraints()

        logger.info("Building Knowledge Graph for Candidate ID: %d (%s)", candidate_id, user_profile.name)

        with self.client.driver.session(database=self.client.database) as session:
            # 2. Ingest Candidate Node
            candidate_props = {
                "candidate_id": int(candidate_id),
                "name": str(user_profile.name or ""),
                "email": str(user_profile.email or ""),
                "phone": str(user_profile.phone or ""),
                "college": str(user_profile.college or ""),
                "degree": str(user_profile.degree or ""),
                "graduation_year": int(user_profile.graduation_year) if user_profile.graduation_year else None,
                "location": str(user_profile.location or ""),
                "summary": str(user_profile.summary or user_profile.bio or ""),
                "completeness_score": int(profile.completeness.score) if profile.completeness else 0,
                "total_skills": len(profile.unified_skills),
            }

            session.run(
                """
                MERGE (c:Candidate {candidate_id: $candidate_id})
                SET c.name = $name,
                    c.email = $email,
                    c.phone = $phone,
                    c.college = $college,
                    c.degree = $degree,
                    c.graduation_year = $graduation_year,
                    c.location = $location,
                    c.summary = $summary,
                    c.completeness_score = $completeness_score,
                    c.total_skills = $total_skills,
                    c.last_synced_at = datetime()
                RETURN c
                """,
                candidate_props,
            )

            # 3. Ingest Unified Skills & HAS_SKILL Relationships
            for skill in profile.unified_skills:
                skill_name = skill.name.strip()
                if not skill_name:
                    continue

                session.run(
                    """
                    MERGE (c:Candidate {candidate_id: $candidate_id})
                    MERGE (s:Skill {name: $skill_name})
                    ON CREATE SET s.category = $category
                    ON MATCH SET s.category = $category
                    MERGE (c)-[r:HAS_SKILL]->(s)
                    SET r.confidence_score = $confidence_score,
                        r.supporting_sources_count = $supporting_sources_count,
                        r.sources = $sources
                    """,
                    {
                        "candidate_id": candidate_id,
                        "skill_name": skill_name,
                        "category": skill.category or "General",
                        "confidence_score": float(skill.confidence_score),
                        "supporting_sources_count": int(skill.supporting_sources_count),
                        "sources": list(skill.sources),
                    },
                )

            # 4. Ingest Projects & HAS_PROJECT Relationships
            for idx, proj in enumerate(profile.projects):
                title = proj.title.strip() if proj.title else f"Project_{idx + 1}"
                slug = _sanitize_identifier(title)
                project_id = f"cand_{candidate_id}_proj_{slug}"

                session.run(
                    """
                    MERGE (c:Candidate {candidate_id: $candidate_id})
                    MERGE (p:Project {project_id: $project_id})
                    SET p.title = $title,
                        p.description = $description,
                        p.source = $source,
                        p.url = $url,
                        p.stars = $stars
                    MERGE (c)-[r:HAS_PROJECT]->(p)
                    SET r.source = $source
                    """,
                    {
                        "candidate_id": candidate_id,
                        "project_id": project_id,
                        "title": title,
                        "description": str(proj.description or ""),
                        "source": str(proj.source or "candidate_profile"),
                        "url": str(proj.url or ""),
                        "stars": int(proj.stars) if proj.stars is not None else 0,
                    },
                )

                # Connect Project to Technologies
                for tech in proj.technologies:
                    tech_clean = tech.strip()
                    if not tech_clean:
                        continue
                    session.run(
                        """
                        MERGE (p:Project {project_id: $project_id})
                        MERGE (t:Technology {name: $tech_name})
                        MERGE (p)-[:USES_TECHNOLOGY]->(t)
                        """,
                        {
                            "project_id": project_id,
                            "tech_name": tech_clean,
                        },
                    )

            # 5. Ingest Certifications & HAS_CERTIFICATION Relationships
            if profile.certifications_summary and profile.certifications_summary.items:
                for idx, cert in enumerate(profile.certifications_summary.items):
                    cert_name = cert.get("certification_name") or cert.get("title") or f"Cert_{idx + 1}"
                    cert_db_id = cert.get("id")
                    cert_slug = _sanitize_identifier(cert_name)
                    cert_id = f"cand_{candidate_id}_cert_{cert_db_id if cert_db_id else cert_slug}"

                    session.run(
                        """
                        MERGE (c:Candidate {candidate_id: $candidate_id})
                        MERGE (cert:Certification {certification_id: $cert_id})
                        SET cert.name = $name,
                            cert.issuing_organization = $issuing_organization,
                            cert.issue_date = $issue_date,
                            cert.credential_id = $credential_id,
                            cert.credential_url = $credential_url,
                            cert.source = $source,
                            cert.verification_status = $verification_status,
                            cert.confidence_score = $confidence_score
                        MERGE (c)-[r:HAS_CERTIFICATION]->(cert)
                        SET r.verification_status = $verification_status,
                            r.confidence_score = $confidence_score
                        """,
                        {
                            "candidate_id": candidate_id,
                            "cert_id": cert_id,
                            "name": cert_name,
                            "issuing_organization": str(cert.get("issuing_organization") or "Unknown"),
                            "issue_date": str(cert.get("issue_date") or ""),
                            "credential_id": str(cert.get("credential_id") or ""),
                            "credential_url": str(cert.get("credential_url") or ""),
                            "source": str(cert.get("source") or "MANUAL"),
                            "verification_status": str(cert.get("verification_status") or "UNVERIFIED"),
                            "confidence_score": float(cert.get("confidence_score") or 0.5),
                        },
                    )

            # 6. Ingest Work Experience & HAS_EXPERIENCE Relationships
            for idx, exp in enumerate(profile.experience):
                company = exp.company.strip() if exp.company else f"Company_{idx + 1}"
                role = exp.role.strip() if exp.role else "Software Engineer"
                slug = _sanitize_identifier(f"{company}_{role}_{idx}")
                experience_id = f"cand_{candidate_id}_exp_{slug}"

                session.run(
                    """
                    MERGE (c:Candidate {candidate_id: $candidate_id})
                    MERGE (e:Experience {experience_id: $experience_id})
                    SET e.company = $company,
                        e.role = $role,
                        e.duration = $duration,
                        e.description = $description
                    MERGE (c)-[:HAS_EXPERIENCE]->(e)
                    """,
                    {
                        "candidate_id": candidate_id,
                        "experience_id": experience_id,
                        "company": company,
                        "role": role,
                        "duration": str(exp.duration or ""),
                        "description": str(exp.description or ""),
                    },
                )

                # Connect Experience to Technologies
                for tech in exp.technologies:
                    tech_clean = tech.strip()
                    if not tech_clean:
                        continue
                    session.run(
                        """
                        MERGE (e:Experience {experience_id: $experience_id})
                        MERGE (t:Technology {name: $tech_name})
                        MERGE (e)-[:USES_TECHNOLOGY]->(t)
                        """,
                        {
                            "experience_id": experience_id,
                            "tech_name": tech_clean,
                        },
                    )

            # 7. Ingest Education & HAS_EDUCATION Relationships
            for idx, edu in enumerate(profile.education):
                inst = edu.institution.strip() if edu.institution else f"Institution_{idx + 1}"
                deg = edu.degree.strip() if edu.degree else "Degree"
                slug = _sanitize_identifier(f"{inst}_{deg}_{idx}")
                education_id = f"cand_{candidate_id}_edu_{slug}"

                session.run(
                    """
                    MERGE (c:Candidate {candidate_id: $candidate_id})
                    MERGE (edu:Education {education_id: $education_id})
                    SET edu.institution = $institution,
                        edu.degree = $degree,
                        edu.field_of_study = $field_of_study,
                        edu.start_date = $start_date,
                        edu.end_date = $end_date,
                        edu.grade = $grade
                    MERGE (c)-[:HAS_EDUCATION]->(edu)
                    """,
                    {
                        "candidate_id": candidate_id,
                        "education_id": education_id,
                        "institution": inst,
                        "degree": deg,
                        "field_of_study": str(edu.field_of_study or ""),
                        "start_date": str(edu.start_date or ""),
                        "end_date": str(edu.end_date or ""),
                        "grade": str(edu.grade or ""),
                    },
                )

        counts = self.get_candidate_graph_counts(candidate_id)
        logger.info("Successfully built Knowledge Graph for Candidate ID %d: %s", candidate_id, counts)
        return {
            "candidate_id": candidate_id,
            "status": "SUCCESS",
            "counts": counts,
        }

    def get_candidate_graph_counts(self, candidate_id: int) -> Dict[str, int]:
        """
        Queries Neo4j for the exact counts of nodes and relationships
        associated with a specific candidate.
        """
        query = """
        MATCH (c:Candidate {candidate_id: $candidate_id})
        OPTIONAL MATCH (c)-[r_skill:HAS_SKILL]->(s:Skill)
        OPTIONAL MATCH (c)-[r_proj:HAS_PROJECT]->(p:Project)
        OPTIONAL MATCH (p)-[r_ptech:USES_TECHNOLOGY]->(t:Technology)
        OPTIONAL MATCH (c)-[r_cert:HAS_CERTIFICATION]->(cert:Certification)
        OPTIONAL MATCH (c)-[r_exp:HAS_EXPERIENCE]->(e:Experience)
        OPTIONAL MATCH (c)-[r_edu:HAS_EDUCATION]->(edu:Education)
        RETURN
            count(DISTINCT c) AS candidate_nodes,
            count(DISTINCT s) AS skill_nodes,
            count(DISTINCT r_skill) AS has_skill_relationships,
            count(DISTINCT p) AS project_nodes,
            count(DISTINCT r_proj) AS has_project_relationships,
            count(DISTINCT t) AS technology_nodes,
            count(DISTINCT r_ptech) AS uses_technology_relationships,
            count(DISTINCT cert) AS certification_nodes,
            count(DISTINCT r_cert) AS has_certification_relationships,
            count(DISTINCT e) AS experience_nodes,
            count(DISTINCT r_exp) AS has_experience_relationships,
            count(DISTINCT edu) AS education_nodes,
            count(DISTINCT r_edu) AS has_education_relationships
        """
        records = self.client.execute_query(query, {"candidate_id": candidate_id})
        if not records:
            return {}
        return records[0]

    def get_candidate_subgraph(self, candidate_id: int) -> Dict[str, Any]:
        """
        Retrieves the complete structured knowledge graph for a candidate.
        """
        candidate_rec = self.client.execute_query(
            "MATCH (c:Candidate {candidate_id: $candidate_id}) RETURN properties(c) AS candidate",
            {"candidate_id": candidate_id},
        )
        if not candidate_rec:
            return {}

        skills_rec = self.client.execute_query(
            """
            MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_SKILL]->(s:Skill)
            RETURN s.name AS name, s.category AS category, r.confidence_score AS confidence_score, r.sources AS sources
            ORDER BY r.confidence_score DESC, s.name ASC
            """,
            {"candidate_id": candidate_id},
        )

        projects_rec = self.client.execute_query(
            """
            MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_PROJECT]->(p:Project)
            OPTIONAL MATCH (p)-[:USES_TECHNOLOGY]->(t:Technology)
            RETURN p.title AS title, p.source AS source, p.description AS description, p.stars AS stars,
                   collect(DISTINCT t.name) AS technologies
            ORDER BY p.title ASC
            """,
            {"candidate_id": candidate_id},
        )

        certs_rec = self.client.execute_query(
            """
            MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_CERTIFICATION]->(cert:Certification)
            RETURN cert.name AS name, cert.issuing_organization AS organization, cert.verification_status AS status,
                   r.confidence_score AS confidence_score
            ORDER BY cert.name ASC
            """,
            {"candidate_id": candidate_id},
        )

        exp_rec = self.client.execute_query(
            """
            MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_EXPERIENCE]->(e:Experience)
            OPTIONAL MATCH (e)-[:USES_TECHNOLOGY]->(t:Technology)
            RETURN e.company AS company, e.role AS role, e.duration AS duration, collect(DISTINCT t.name) AS technologies
            """,
            {"candidate_id": candidate_id},
        )

        edu_rec = self.client.execute_query(
            """
            MATCH (c:Candidate {candidate_id: $candidate_id})-[r:HAS_EDUCATION]->(edu:Education)
            RETURN edu.institution AS institution, edu.degree AS degree, edu.field_of_study AS field_of_study, edu.grade AS grade
            """,
            {"candidate_id": candidate_id},
        )

        return {
            "candidate": candidate_rec[0]["candidate"],
            "skills": skills_rec,
            "projects": projects_rec,
            "certifications": certs_rec,
            "experience": exp_rec,
            "education": edu_rec,
        }


# Global CandidateGraphBuilder singleton instance
candidate_graph_builder = CandidateGraphBuilder()
