"""
Skill normalizer compatibility wrapper.
Delegates to app.parsers.skill_normalizer as the single source of truth.
"""

from app.parsers.skill_normalizer import (
    normalize_skill as parser_normalize_skill,
    get_canonical_skill_name,
    CANONICAL_SKILL_DATABASE,
    SKILL_CATEGORIES,
)


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill string into its canonical name.
    Preserves backward compatibility while routing through the unified taxonomy.
    """
    if not skill or not isinstance(skill, str):
        return ""
    return get_canonical_skill_name(skill)