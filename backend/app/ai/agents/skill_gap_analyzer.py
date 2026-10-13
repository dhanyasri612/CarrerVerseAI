"""
Deterministic Skill-Gap Analyzer for CareerVerse AI.

Compares candidate evidence from the Neo4j Knowledge Graph and Unified Profile
against system-defined target-role requirements before LLM synthesis.
Ensures factual grounding and research reproducibility.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from app.ai.agents.role_requirements import get_role_requirements
from app.ai.knowledge_graph.graph_queries import (
    CandidateGraphQueries,
    candidate_graph_queries,
)
from app.parsers.skill_normalizer import get_canonical_skill_name, normalize_skill
from app.schemas.knowledge_graph import CandidateSubgraphResponse
from app.schemas.skill_gap import GapLevel, SkillGapItem, SkillGapStatus

logger = logging.getLogger("careerverse.ai.agents.skill_gap_analyzer")


class SkillGapAnalyzer:
    """
    Deterministic evaluation engine.
    Extracts candidate evidence from Knowledge Graph and evaluates coverage
    against system-defined role skill requirements.
    """

    def __init__(self, graph_queries: CandidateGraphQueries = candidate_graph_queries):
        self.graph_queries = graph_queries

    def analyze_candidate_skill_gaps(
        self,
        candidate_id: int,
        target_role: str,
    ) -> Tuple[List[SkillGapItem], List[str], Dict[str, Any]]:
        """
        Performs deterministic comparison between candidate data and target role requirements.

        Returns:
            Tuple of:
            - skill_gaps: List of SkillGapItem with deterministic statuses and evidence
            - strengths: List of confirmed demonstrated skill names
            - audit_metrics: Dict of counts (demonstrated, partial, missing, insufficient)
        """
        role_reqs = get_role_requirements(target_role)
        if not role_reqs:
            raise ValueError(f"Unknown or unsupported target role: '{target_role}'")

        # 1. Retrieve Candidate Knowledge Graph Subgraph
        subgraph: Optional[CandidateSubgraphResponse] = self.graph_queries.get_candidate_subgraph(candidate_id)
        if not subgraph:
            logger.warning("No Knowledge Graph subgraph found for Candidate ID %d", candidate_id)
            # Empty candidate fallback
            candidate_skills = {}
            candidate_projects = []
            candidate_techs = set()
            candidate_certs = []
        else:
            candidate_skills = {
                get_canonical_skill_name(s.name) or s.name: s
                for s in subgraph.skills
            }
            candidate_projects = subgraph.projects
            candidate_techs = {t.lower() for t in subgraph.technologies}
            candidate_certs = subgraph.certifications

        # 2. Extract project evidence map: skill/tech -> [project_names]
        tech_to_projects: Dict[str, List[str]] = {}
        for proj in candidate_projects:
            proj_name = getattr(proj, "title", getattr(proj, "name", "Project"))
            for tech in proj.technologies:
                canon_tech = get_canonical_skill_name(tech) or tech
                tech_to_projects.setdefault(canon_tech.lower(), []).append(proj_name)

        # 3. Evaluate each target requirement
        required_skills: List[str] = role_reqs.get("required_skills", [])
        optional_skills: List[str] = role_reqs.get("optional_skills", [])

        all_target_skills: List[Tuple[str, str]] = [
            (s, "required") for s in required_skills
        ] + [
            (s, "optional") for s in optional_skills
        ]

        skill_gap_items: List[SkillGapItem] = []
        strengths: List[str] = []

        demonstrated_count = 0
        partial_count = 0
        missing_count = 0
        insufficient_count = 0

        for skill_name, req_type in all_target_skills:
            canonical_target, category = normalize_skill(skill_name)
            target_lower = canonical_target.lower()

            evidence_items: List[str] = []
            evidence_sources: List[str] = []
            status: SkillGapStatus = "missing"
            gap_level: GapLevel = "high" if req_type == "required" else "low"
            explanation: str = ""

            # Check matching skill node in graph
            matched_skill = candidate_skills.get(canonical_target)
            if not matched_skill:
                # Check case-insensitive match
                for cand_skill_name, cand_skill_obj in candidate_skills.items():
                    if cand_skill_name.lower() == target_lower:
                        matched_skill = cand_skill_obj
                        break

            # Check project applications
            matched_projects = tech_to_projects.get(target_lower, [])

            # Check certification match
            matched_certs = [
                c.name for c in candidate_certs
                if target_lower in c.name.lower()
            ]

            # Case A: Strong graph evidence
            if matched_skill and matched_skill.confidence_score >= 0.70:
                status = "demonstrated"
                gap_level = "none"
                evidence_sources = list(matched_skill.sources)
                evidence_items.append(
                    f"Verified in Knowledge Graph with {int(matched_skill.confidence_score * 100)}% confidence."
                )
                if matched_skill.sources:
                    evidence_items.append(
                        f"Sources: {', '.join(matched_skill.sources)}"
                    )
                if matched_projects:
                    evidence_items.append(
                        f"Applied in projects: {', '.join(matched_projects[:3])}"
                    )
                if matched_certs:
                    evidence_items.append(
                        f"Relevant certifications: {', '.join(matched_certs[:2])}"
                    )
                explanation = f"Strong multi-source demonstration for {canonical_target} ({req_type})."
                demonstrated_count += 1
                strengths.append(canonical_target)

            # Case B: Moderate graph evidence or project-only usage
            elif (matched_skill and matched_skill.confidence_score >= 0.40) or matched_projects or matched_certs:
                status = "partially_demonstrated"
                gap_level = "medium" if req_type == "required" else "low"
                if matched_skill:
                    evidence_sources = list(matched_skill.sources)
                    evidence_items.append(
                        f"Present in graph with {int(matched_skill.confidence_score * 100)}% confidence."
                    )
                if matched_projects:
                    evidence_items.append(
                        f"Referenced in project technologies: {', '.join(matched_projects[:3])}"
                    )
                if matched_certs:
                    evidence_items.append(
                        f"Referenced in certifications: {', '.join(matched_certs[:2])}"
                    )
                explanation = f"Partial candidate evidence found for {canonical_target} ({req_type})."
                partial_count += 1

            # Case C: Minimal / Related traces
            elif target_lower in candidate_techs:
                status = "insufficient_evidence"
                gap_level = "medium" if req_type == "required" else "low"
                evidence_items.append("Mentioned in candidate technology list without verified deep demonstration.")
                explanation = f"Insufficient verifiable evidence for {canonical_target} in candidate history."
                insufficient_count += 1

            # Case D: Completely Missing
            else:
                status = "missing"
                gap_level = "high" if req_type == "required" else "low"
                evidence_items.append("No record found across candidate profile, resume, GitHub, or coding platforms.")
                explanation = f"No verified evidence found for {canonical_target} ({req_type})."
                missing_count += 1

            item = SkillGapItem(
                skill=canonical_target,
                category=category,
                target_requirement=req_type,
                candidate_evidence=evidence_items,
                evidence_sources=evidence_sources,
                status=status,
                gap_level=gap_level,
                explanation=explanation,
            )
            skill_gap_items.append(item)

        audit_metrics = {
            "target_role": role_reqs["title"],
            "total_target_skills": len(all_target_skills),
            "demonstrated_count": demonstrated_count,
            "partial_count": partial_count,
            "missing_count": missing_count,
            "insufficient_count": insufficient_count,
        }

        logger.info(
            "Skill-Gap deterministic analysis complete for Candidate ID %d, Role '%s': %s",
            candidate_id,
            target_role,
            audit_metrics,
        )

        return skill_gap_items, strengths, audit_metrics


# Global singleton instance
skill_gap_analyzer = SkillGapAnalyzer()
