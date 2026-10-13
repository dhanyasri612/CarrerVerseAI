import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.teaching_progress import TeachingProgress
from app.schemas.learner_knowledge import LearnerKnowledgeProfile, SkillEvidenceRecord
from app.services.unified_profile_service import build_unified_candidate_profile
from app.parsers.skill_normalizer import normalize_skill

logger = logging.getLogger("careerverse.ai.learner_knowledge")

# Canonical role requirements and concept prerequisites taxonomy
ROLE_REQUIRED_CONCEPTS: Dict[str, List[str]] = {
    "software engineer": [
        "arrays and hash maps", "two pointers", "sliding window", "binary search",
        "linked lists", "trees and graphs", "heaps", "dynamic programming",
        "python", "fastapi", "postgresql", "docker", "git", "system design"
    ],
    "backend developer": [
        "http and rest apis", "authentication and authorization", "fastapi", "python",
        "database modeling", "transactions and indexing", "postgresql", "caching",
        "redis", "async programming", "docker", "api testing", "system design"
    ],
    "full stack engineer": [
        "javascript", "react", "html and css", "http and rest apis", "python", "fastapi",
        "database modeling", "postgresql", "state management", "git", "docker"
    ],
    "ai engineer": [
        "python", "embeddings", "semantic search", "vector databases",
        "retrieval-augmented generation", "knowledge graphs", "prompt design",
        "llm evaluation", "agent orchestration", "fastapi", "docker"
    ],
    "data engineer": [
        "python", "sql", "postgresql", "data pipelines", "caching", "docker",
        "database modeling", "transactions and indexing", "git"
    ],
}

# Concept Prerequisite DAG (Dependency mappings)
CONCEPT_PREREQUISITES: Dict[str, List[str]] = {
    # DSA
    "two pointers": ["arrays and hash maps"],
    "sliding window": ["arrays and hash maps", "two pointers"],
    "binary search": ["arrays and hash maps"],
    "linked lists": ["pointers and memory references"],
    "trees and graphs": ["recursion and call stacks", "linked lists"],
    "heaps": ["binary trees", "arrays and hash maps"],
    "dynamic programming": ["recursion and call stacks", "memoization and caching"],
    # Backend
    "authentication and authorization": ["http and rest apis"],
    "transactions and indexing": ["database modeling", "postgresql"],
    "caching": ["http and rest apis", "database modeling"],
    "async programming": ["python", "event loops and non-blocking i/o"],
    # AI & RAG
    "semantic search": ["embeddings"],
    "vector databases": ["embeddings", "semantic search"],
    "retrieval-augmented generation": ["embeddings", "vector databases", "prompt design"],
    "knowledge graphs": ["database modeling", "graph data structures"],
    "agent orchestration": ["retrieval-augmented generation", "prompt design"],
    # System Design
    "scalability and distribution": ["caching", "database modeling", "transactions and indexing"],
}


def _match_target_role_category(target_role: Optional[str]) -> str:
    role_str = (target_role or "software engineer").strip().lower()
    for key in ROLE_REQUIRED_CONCEPTS:
        if key in role_str or role_str in key:
            return key
    if "backend" in role_str:
        return "backend developer"
    if "ai" in role_str or "machine learning" in role_str or "ml" in role_str:
        return "ai engineer"
    if "full" in role_str or "stack" in role_str or "frontend" in role_str:
        return "full stack engineer"
    return "software engineer"


def build_learner_knowledge_profile(db: Session, user: User) -> LearnerKnowledgeProfile:
    """
    Constructs an authentic, evidence-backed knowledge profile for the learner.
    Gathers evidence across Resumes, GitHub, LeetCode, HackerRank, Certifications, and Teaching Progress.
    Distinguishes observed evidence from inferences and unknown skills from unskilled.
    """
    candidate_id = user.id
    candidate_name = getattr(user, "name", None) or getattr(user, "full_name", None) or user.username or "Candidate"
    target_role = getattr(user, "target_role", None) or "Software Engineer (SDE)"
    matched_role_key = _match_target_role_category(target_role)
    required_concepts = ROLE_REQUIRED_CONCEPTS.get(matched_role_key, ROLE_REQUIRED_CONCEPTS["software engineer"])

    # 1. Fetch Unified Profile
    prof = None
    try:
        prof = build_unified_candidate_profile(db, user)
    except Exception as exc:
        logger.warning("Could not load unified profile for learner %d: %s", candidate_id, exc)

    # 2. Fetch Teaching Progress from PostgreSQL
    progress_records = db.query(TeachingProgress).filter(TeachingProgress.candidate_id == candidate_id).all()
    progress_by_lesson: Dict[str, TeachingProgress] = {p.lesson_id: p for p in progress_records}

    # 3. Build Structured Skills Inventory
    skills_inventory: Dict[str, SkillEvidenceRecord] = {}
    verified_projects: List[Dict[str, Any]] = []

    if prof:
        # Extract Projects
        for p in (prof.projects or []):
            p_dict = {
                "id": getattr(p, "id", None),
                "title": getattr(p, "title", "Project"),
                "description": getattr(p, "description", ""),
                "technologies": getattr(p, "technologies", []) or [],
                "source": getattr(p, "source", "portfolio"),
                "url": getattr(p, "url", None),
                "stars": getattr(p, "stars", 0) or 0,
            }
            verified_projects.append(p_dict)

        # Process Unified Skills
        for us in (prof.unified_skills or []):
            s_name = us.name.strip()
            s_lower = s_name.lower()
            category = us.category or "General"
            sources = us.sources or []

            # Evidence classification rules
            # Mentioned on resume != mastered.
            # Connected GitHub != proficiency.
            # Solved LeetCode != mastery of every concept.
            evidence_type = "explicitly_declared"
            evidence_source = "resume"
            description_parts: List[str] = []

            has_github = any("github" in str(s).lower() for s in sources)
            has_leetcode = any("leetcode" in str(s).lower() for s in sources)
            has_hackerrank = any("hackerrank" in str(s).lower() for s in sources)
            has_cert = any("cert" in str(s).lower() for s in sources)
            has_resume = any("resume" in str(s).lower() for s in sources)

            if has_leetcode or has_hackerrank or has_cert:
                evidence_type = "assessed"
                evidence_source = "leetcode" if has_leetcode else ("hackerrank" if has_hackerrank else "certification")
                description_parts.append(f"Assessed via coding performance / credential in {evidence_source}")
            elif has_github:
                evidence_type = "observed"
                evidence_source = "github"
                description_parts.append("Observed in connected candidate GitHub repositories")
            elif has_resume:
                evidence_type = "explicitly_declared"
                evidence_source = "resume"
                description_parts.append("Explicitly declared on candidate resume")

            # Check if learner has completed or mastered teaching lessons on this concept
            matching_progress = [
                p for l_id, p in progress_by_lesson.items()
                if s_lower in l_id.lower() or l_id.lower() in s_lower
            ]
            status = "not_started"
            if matching_progress:
                best_p = matching_progress[0]
                if best_p.status == "mastered":
                    status = "mastered"
                    evidence_type = "assessed"
                    description_parts.append("Mastered in Socratic Masterclass assessment (Score >= 80%)")
                elif best_p.status == "completed":
                    status = "demonstrated_understanding"
                    description_parts.append("Completed Socratic Masterclass lesson walkthrough")
                else:
                    status = "learning"
            elif evidence_type == "assessed":
                status = "demonstrated_understanding"
            elif evidence_type == "observed":
                status = "learning"

            # Compute calibrated confidence score
            base_conf = float(us.confidence_score or 0.5)
            if status == "mastered":
                base_conf = max(base_conf, 0.95)
            elif status == "demonstrated_understanding":
                base_conf = max(base_conf, 0.85)
            elif evidence_type == "observed":
                base_conf = max(base_conf, 0.70)
            elif evidence_type == "explicitly_declared":
                base_conf = min(base_conf, 0.60)

            # Determine prerequisites
            prereqs = CONCEPT_PREREQUISITES.get(s_lower, [])

            skills_inventory[s_lower] = SkillEvidenceRecord(
                concept_name=s_name,
                category=category,
                evidence_source=evidence_source,
                evidence_identifier=sources[0] if sources else None,
                evidence_description="; ".join(description_parts) or f"Evidence documented in {evidence_source}",
                last_verified_at=datetime.utcnow().isoformat(),
                evidence_type=evidence_type,
                confidence_score=round(base_conf, 2),
                prerequisites=prereqs,
                status=status,
                is_knowledge_gap=False,
                why_matters_for_role=f"Essential capability for {target_role} roles.",
                learning_priority="high" if s_lower in required_concepts else "medium",
                estimated_effort_hours=4 if prereqs else 2,
            )

    # 4. Identify Knowledge Gaps for Target Role
    knowledge_gaps: List[str] = []
    demonstrated_strengths: List[str] = []

    for req in required_concepts:
        found_key = next((k for k in skills_inventory if k == req or req in k or k in req), None)
        if not found_key:
            # Missing evidence means UNKNOWN, not necessarily unskilled
            skills_inventory[req] = SkillEvidenceRecord(
                concept_name=req.title(),
                category="Role Requirement",
                evidence_source="inferred",
                evidence_identifier=None,
                evidence_description=f"Standard competency expected for {target_role}. No observed candidate evidence yet (Status: Unknown).",
                last_verified_at=datetime.utcnow().isoformat(),
                evidence_type="inferred",
                confidence_score=0.10,
                prerequisites=CONCEPT_PREREQUISITES.get(req, []),
                status="unknown",
                is_knowledge_gap=True,
                why_matters_for_role=f"Core architectural requirement for {target_role}.",
                learning_priority="high",
                estimated_effort_hours=6,
            )
            knowledge_gaps.append(req)
        else:
            rec = skills_inventory[found_key]
            if rec.status in ("demonstrated_understanding", "mastered"):
                demonstrated_strengths.append(rec.concept_name)
            elif rec.status in ("unknown", "not_started"):
                rec.is_knowledge_gap = True
                knowledge_gaps.append(rec.concept_name)

    # 5. Topologically Sort Recommended Learning Order (Prerequisites First)
    recommended_order: List[str] = []
    visited: Set[str] = set()

    def visit(concept: str):
        if concept in visited:
            return
        visited.add(concept)
        for prereq in CONCEPT_PREREQUISITES.get(concept, []):
            if prereq in skills_inventory and skills_inventory[prereq].status not in ("mastered", "demonstrated_understanding"):
                visit(prereq)
        recommended_order.append(concept)

    # Focus priority on gaps first, then incomplete concepts
    for gap in knowledge_gaps:
        visit(gap)
    for c_key, c_rec in skills_inventory.items():
        if c_rec.status not in ("mastered", "demonstrated_understanding"):
            visit(c_key)

    return LearnerKnowledgeProfile(
        candidate_id=candidate_id,
        candidate_name=candidate_name,
        target_role=target_role,
        career_goals=[f"Excel as a high-performing {target_role}", "Master core production architecture & design"],
        skills_inventory=skills_inventory,
        verified_projects=verified_projects,
        target_role_required_skills=required_concepts,
        knowledge_gaps=knowledge_gaps,
        demonstrated_strengths=demonstrated_strengths,
        recommended_learning_order=recommended_order,
    )
