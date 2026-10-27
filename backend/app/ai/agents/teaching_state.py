"""
Teaching State definition for CareerVerse AI LangGraph Teaching Agent.

Defines the shared typed state dictionary flowing across Phase 3 teaching workflow nodes:
- analyze_query: Validates query, detects intent, checks ambiguity
- prepare_teaching_decision: Evaluates evidence sufficiency, selects pedagogical strategy
- finalize_response: Synthesizes structured tutor response with citations and follow-ups
"""

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class TeachingState(TypedDict, total=False):
    """
    Typed state container for CareerVerse AI LangGraph teaching workflow.
    Adheres to LangGraph state standards and project typing conventions.
    """
    # ── Learner Query & Session Context ──────────────────────────────────────
    learner_query: str
    original_query: str
    user_id: Optional[int]
    user_name: Optional[str]
    mode: str                             # "skill" | "project" | "materials" | "curriculum"
    target_id: str                        # skill name (e.g. "React"), repo id, or course document name
    lesson_id: Optional[str]
    lesson_title: Optional[str]
    chat_history: List[Dict[str, Any]]
    language: str                         # "en", "ta", "hi", etc.
    is_assessment: bool

    # ── Analysis & Intent ────────────────────────────────────────────────────
    is_ambiguous: bool
    ambiguity_reason: Optional[str]
    learner_intent: str                   # "clarification" | "concept_explanation" | "socratic_hint" | "code_walkthrough" | "general_inquiry"
    extracted_keywords: List[str]

    # ── Evidence & Grounding Context ─────────────────────────────────────────
    retrieved_evidence: Optional[List[Dict[str, Any]]]  # Unified evidence items passed to graph or populated by retrieval
    course_materials: List[Dict[str, Any]]              # Uploaded course materials
    technical_sources: List[Dict[str, Any]]             # Fresh technical references
    catalog_resources: List[Dict[str, Any]]             # Curated catalog resources
    retrieval_status: str                               # "success" | "no_results" | "error" | "degraded" | "skipped" | "pre_supplied"
    course_materials_status: str                        # "found" | "no_results" | "error" | "skipped"
    technical_sources_status: str                       # "fresh" | "not_refreshed" | "no_results" | "error"
    retrieval_error: Optional[str]
    evidence_sufficiency: str                           # "sufficient" | "insufficient" | "ambiguous"
    grounding_type: str                                # "source_grounded" | "course_material_grounded" | "general_knowledge" | "clarification_needed"
    best_similarity: float
    matched_sources: List[Dict[str, Any]]
    insufficient_evidence_notice: Optional[str]
    clarification_prompt: Optional[str]
    citations: List[Dict[str, Any]]
    technical_source_status: str                       # "fresh" | "stale" | "not_refreshed" | "no_matching_fresh_sources" | "error"
    skip_retrieval: bool
    force_retrieval: bool

    # ── Pedagogical Decision & Assessment ────────────────────────────────────
    pedagogical_decision: str                      # "clarify" | "explain" | "socratic_hint" | "code_demonstration" | "evaluate_response" | "general_overview"
    socratic_stage: str                            # "explanation" | "objective" | "practice" | "assessment"
    suggested_follow_ups: List[str]
    learner_response: Optional[str]
    workspace_code: Optional[str]
    assessment_evaluation: Optional[Dict[str, Any]]
    demonstrated_understanding: Optional[bool]
    assessment_score: Optional[int]
    recommended_next_action: Optional[str]
    audio_narrative: Optional[str]

    # ── Final Structured Output & Error Tracking ─────────────────────────────
    tutor_reply: Optional[str]
    structured_response: Optional[Dict[str, Any]]  # Matches TeachingChatResponse contract
    errors: List[str]
    error_metadata: Optional[Dict[str, Any]]
    execution_time_ms: float
    status: str                                    # "initialized" | "analyzed" | "decided" | "completed" | "error"
