"""
Evidence Sufficiency Gate for CareerVerse AI Teaching Room.

Evaluates student questions against retrieved technical sources and knowledge bank:
1. Ambiguity Detection: Identifies broad, underspecified questions and formulates targeted clarifying questions.
2. Sufficiency Check: Assesses whether retrieved evidence is strong enough to ground the answer.
3. Grounding Classifier: Distinguishes between source-grounded claims and general knowledge.
4. Anti-Hallucination: Prevents fabrication of citations when sources are absent.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

# Common words that don't indicate technical specificity
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "explain", "few", "for", "from",
    "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "help",
    "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into",
    "is", "isn't", "it", "it's", "its", "itself", "just", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "please", "same", "shan't", "she", "should",
    "shouldn't", "so", "some", "such", "tell", "than", "that", "that's", "the", "their", "theirs",
    "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very",
    "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's",
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "build", "builds", "building", "built", "use", "uses", "used", "using", "run", "runs", "running",
    "make", "makes", "making", "create", "creates", "creating", "learn", "learning", "session",
    "technical", "concept", "concepts", "topic", "topics", "question", "questions", "example",
    "examples", "guide", "tutorial", "write", "writing", "show", "give", "need", "like", "want",
}

# Generic inquiry tokens that, if appearing alone, indicate ambiguity
AMBIGUOUS_GENERIC_PATTERNS: List[str] = [
    r"^(?:how\s+does\s+)?performance(?:\s+work)?\??$",
    r"^(?:explain|tell\s+me\s+about)\s+(?:it|this|that|code|system)\??$",
    r"^(?:how\s+to\s+)?optimize\??$",
    r"^(?:how\s+does\s+it\s+work|what\s+is\s+it)\??$",
    r"^code\??$",
    r"^help(?:\s+me)?\??$",
    r"^architecture\??$",
    r"^interview\??$",
]

# Minimum similarity threshold for considering a technical source strongly relevant
SIMILARITY_SUFFICIENCY_THRESHOLD = 0.28


@dataclass(frozen=True)
class EvidenceSufficiencyResult:
    is_sufficient: bool
    status: str  # "sufficient" | "insufficient" | "ambiguous"
    grounding_type: str  # "source_grounded" | "general_knowledge" | "clarification_needed"
    best_similarity: float = 0.0
    matched_sources: List[Dict[str, Any]] = field(default_factory=list)
    clarification_message: Optional[str] = None
    insufficient_evidence_notice: Optional[str] = None
    meaningful_keywords: List[str] = field(default_factory=list)


def extract_meaningful_keywords(text: str) -> List[str]:
    """Extract clean, meaningful technical keywords from text, excluding stop-words."""
    if not text:
        return []
    words = re.findall(r"[a-zA-Z0-9_+#.-]+", text.lower())
    return [w for w in words if len(w) >= 2 and w not in STOP_WORDS]


def is_ambiguous_query(query: str, active_lesson_topic: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Determines if a query is too vague to resolve without clarification.
    If an active lesson topic is strongly established (e.g. 'Two Sum' or 'FastAPI'),
    short queries like 'why do we use return?' are contextual and NOT ambiguous.
    """
    clean_q = query.strip().lower()
    
    # Check regex patterns
    for pat in AMBIGUOUS_GENERIC_PATTERNS:
        if re.search(pat, clean_q):
            return True, (
                "Your question is quite broad. To give you the most accurate explanation grounded "
                "in your learning materials, could you clarify what specific topic or context you'd like to explore? "
                "(For example: Python asyncio concurrency, React re-render memoization, or PostgreSQL B-Tree indexing?)"
            )

    keywords = extract_meaningful_keywords(clean_q)
    
    # If 0 or 1 vague keyword with no active context
    if len(keywords) <= 1 and (not active_lesson_topic or active_lesson_topic.lower() in {"technical scenario", "general", "topic"}):
        if len(keywords) == 0:
            return True, (
                "Could you provide a bit more detail on what concept or problem you would like to work through? "
                "I'm ready to walk you through step-by-step notes, examples, or practice questions."
            )
        word = keywords[0]
        if word in {"fast", "slow", "good", "bad", "better", "best", "speed", "test", "run", "style"}:
            return True, (
                f"You asked about '{word}'. To give you a grounded masterclass, could you tell me which language, "
                f"framework, or problem context you have in mind?"
            )

    return False, None


def evaluate_teaching_evidence_sufficiency(
    user_query: str,
    target_topic: str = "",
    technical_sources: Optional[List[Dict[str, Any]]] = None,
    catalog_resources: Optional[List[Any]] = None,
    candidate_projects: Optional[List[Dict[str, Any]]] = None,
    course_materials: Optional[List[Any]] = None,
    is_assessment: bool = False,
) -> EvidenceSufficiencyResult:
    """
    Evaluates evidence sufficiency across retrieved sources:
    - Ambiguous queries trigger clarification.
    - Strong course materials and technical source matches enable source_grounded / course_material_grounded teaching.
    - Absent/insufficient queries trigger ungrounded general knowledge mode with explicit notice.
    """
    tech_sources = technical_sources or []
    cat_resources = catalog_resources or []
    cand_projects = candidate_projects or []
    c_materials = course_materials or []

    # 1. Check ambiguity (skip ambiguity check during assessments where candidate submits answer code/thoughts)
    if not is_assessment:
        ambiguous, clarif_msg = is_ambiguous_query(user_query, active_lesson_topic=target_topic)
        if ambiguous:
            return EvidenceSufficiencyResult(
                is_sufficient=False,
                status="ambiguous",
                grounding_type="clarification_needed",
                clarification_message=clarif_msg,
            )

    keywords = extract_meaningful_keywords(f"{user_query} {target_topic}")
    best_similarity = 0.0

    # 2. Check candidate uploaded course materials
    valid_course_material_matches: List[Dict[str, Any]] = []
    for cm in c_materials:
        sim = float(
            getattr(cm, "similarity_score", 0.0)
            if hasattr(cm, "similarity_score")
            else (cm.get("similarity_score", 0.0) if isinstance(cm, dict) else 0.0)
        )
        if sim > best_similarity:
            best_similarity = sim
        if sim >= SIMILARITY_SUFFICIENCY_THRESHOLD:
            cm_dict = (
                cm.model_dump()
                if hasattr(cm, "model_dump")
                else (dict(cm) if isinstance(cm, dict) else vars(cm))
            )
            valid_course_material_matches.append(cm_dict)

    if valid_course_material_matches:
        return EvidenceSufficiencyResult(
            is_sufficient=True,
            status="sufficient",
            grounding_type="course_material_grounded",
            best_similarity=best_similarity,
            matched_sources=valid_course_material_matches,
            meaningful_keywords=keywords,
        )

    # 3. Check fresh technical sources from Chroma
    valid_tech_matches: List[Dict[str, Any]] = []
    for src in tech_sources:
        sim = float(src.get("similarity_score", 0.0))
        if sim > best_similarity:
            best_similarity = sim
        if sim >= SIMILARITY_SUFFICIENCY_THRESHOLD:
            valid_tech_matches.append(src)

    if valid_tech_matches:
        return EvidenceSufficiencyResult(
            is_sufficient=True,
            status="sufficient",
            grounding_type="source_grounded",
            best_similarity=best_similarity,
            matched_sources=valid_tech_matches,
            meaningful_keywords=keywords,
        )

    # 3. Check curated catalog matches (verifying meaningful keyword overlap)
    valid_catalog_matches: List[Dict[str, Any]] = []
    for res in cat_resources:
        res_dict = res.model_dump() if hasattr(res, "model_dump") else (res if isinstance(res, dict) else {})
        res_concepts = [str(c).lower() for c in res_dict.get("concepts_covered", [])]
        res_title = str(res_dict.get("title", "")).lower()

        # Check if at least one meaningful keyword matches the catalog item
        has_match = any(
            kw in res_title or any(kw in c for c in res_concepts)
            for kw in keywords
        )
        if has_match:
            valid_catalog_matches.append(res_dict)

    if valid_catalog_matches:
        return EvidenceSufficiencyResult(
            is_sufficient=True,
            status="sufficient",
            grounding_type="source_grounded",
            best_similarity=max(0.35, best_similarity),
            matched_sources=valid_catalog_matches,
            meaningful_keywords=keywords,
        )

    # 4. Check candidate verified projects (if relevant)
    if cand_projects:
        valid_proj_matches = []
        for p in cand_projects:
            title = str(p.get("title", "")).lower()
            techs = [str(t).lower() for t in p.get("technologies", [])]
            if any(kw in title or any(kw in t for t in techs) for kw in keywords):
                valid_proj_matches.append(p)
        if valid_proj_matches:
            return EvidenceSufficiencyResult(
                is_sufficient=True,
                status="sufficient",
                grounding_type="source_grounded",
                best_similarity=0.40,
                matched_sources=valid_proj_matches,
                meaningful_keywords=keywords,
            )

    # 5. Insufficient evidence: The topic is not covered in course materials
    clean_topic = target_topic.strip() or user_query.strip()[:60]
    notice = (
        f"📚 Knowledge Base Scope Notice: The concept '{clean_topic}' is not covered in your active course "
        f"materials or approved technical references. The guidance below is provided as general software "
        f"engineering principles and is unverified against your specific course syllabus."
    )

    return EvidenceSufficiencyResult(
        is_sufficient=False,
        status="insufficient",
        grounding_type="general_knowledge",
        best_similarity=best_similarity,
        insufficient_evidence_notice=notice,
        meaningful_keywords=keywords,
    )
