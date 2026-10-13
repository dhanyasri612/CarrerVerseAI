"""
CareerVerse AI LangGraph Agents Package.
"""

from app.ai.agents.evaluation_agent import EvaluationAgent, evaluation_agent
from app.ai.agents.orchestrator import CareerOrchestrator, career_orchestrator
from app.ai.agents.recommendation_agent import RecommendationAgent, recommendation_agent
from app.ai.agents.recommendation_prompt import (
    RecommendationPromptBuilder,
    recommendation_prompt_builder,
)
from app.ai.agents.role_requirements import (
    ROLE_REQUIREMENTS_REGISTRY,
    get_role_requirements,
    list_available_roles,
    normalize_role_name,
)
from app.ai.agents.service import (
    run_career_evaluation,
    run_career_intelligence,
    run_career_recommendation,
    run_skill_gap_evaluation,
)
from app.ai.agents.skill_gap_analyzer import (
    SkillGapAnalyzer,
    skill_gap_analyzer,
)
from app.ai.agents.skill_gap_prompt import (
    SkillGapPromptBuilder,
    skill_gap_prompt_builder,
)
from app.ai.agents.state import CareerIntelligenceState

run_career_evaluation = run_skill_gap_evaluation

__all__ = [
    "CareerIntelligenceState",
    "CareerOrchestrator",
    "career_orchestrator",
    "RecommendationAgent",
    "recommendation_agent",
    "RecommendationPromptBuilder",
    "recommendation_prompt_builder",
    "EvaluationAgent",
    "evaluation_agent",
    "SkillGapAnalyzer",
    "skill_gap_analyzer",
    "SkillGapPromptBuilder",
    "skill_gap_prompt_builder",
    "ROLE_REQUIREMENTS_REGISTRY",
    "get_role_requirements",
    "list_available_roles",
    "normalize_role_name",
    "run_career_intelligence",
    "run_career_recommendation",
    "run_skill_gap_evaluation",
    "run_career_evaluation",
]
