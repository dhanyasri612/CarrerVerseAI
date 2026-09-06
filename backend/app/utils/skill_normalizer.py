SKILL_ALIASES = {
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "js": "javascript",
    "javascript": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "react": "react",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "py": "python",
    "python": "python",
    "mongo": "mongodb",
    "mongodb": "mongodb",
}


def normalize_skill(skill: str) -> str:
    skill = skill.strip().lower()

    return SKILL_ALIASES.get(
        skill,
        skill
    )