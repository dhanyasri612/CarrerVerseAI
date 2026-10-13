"""
Role Requirements Registry for CareerVerse AI.

Provides system-defined target-role skill profiles used by the Skill-Gap Agent.
Clearly labeled as 'System-defined target-role requirements' for research evaluation.
"""

import re
from typing import Any, Dict, List, Optional
from app.parsers.skill_normalizer import get_canonical_skill_name

# Registry of system-defined target roles for research evaluation
ROLE_REQUIREMENTS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "software_developer": {
        "role_key": "software_developer",
        "title": "Software Developer",
        "category": "Software Engineering",
        "description": "System-defined target-role requirements for core software engineering.",
        "required_skills": [
            "Python",
            "Java",
            "SQL",
            "REST APIs",
            "Git",
            "Data Structures & Algorithms",
        ],
        "optional_skills": [
            "C++",
            "Docker",
            "CI/CD",
            "Linux",
        ],
    },
    "frontend_developer": {
        "role_key": "frontend_developer",
        "title": "Frontend Developer",
        "category": "Frontend Engineering",
        "description": "System-defined target-role requirements for user interface and client applications.",
        "required_skills": [
            "JavaScript",
            "TypeScript",
            "React",
            "HTML",
            "CSS",
            "REST APIs",
            "Git",
        ],
        "optional_skills": [
            "Next.js",
            "Tailwind CSS",
            "Redux",
            "Figma",
        ],
    },
    "backend_developer": {
        "role_key": "backend_developer",
        "title": "Backend Developer",
        "category": "Backend Engineering",
        "description": "System-defined target-role requirements for backend services, APIs, and data stores.",
        "required_skills": [
            "Python",
            "Java",
            "REST APIs",
            "SQL",
            "PostgreSQL",
            "MySQL",
            "Git",
        ],
        "optional_skills": [
            "FastAPI",
            "Express.js",
            "Docker",
            "Kubernetes",
            "Redis",
            "CI/CD",
        ],
    },
    "machine_learning_engineer": {
        "role_key": "machine_learning_engineer",
        "title": "Machine Learning Engineer",
        "category": "Artificial Intelligence & Data Science",
        "description": "System-defined target-role requirements for applied ML models and data pipelines.",
        "required_skills": [
            "Python",
            "Pandas",
            "NumPy",
            "Scikit-Learn",
            "Machine Learning",
            "Data Structures & Algorithms",
        ],
        "optional_skills": [
            "TensorFlow",
            "PyTorch",
            "Deep Learning",
            "Computer Vision",
            "Natural Language Processing",
            "Docker",
        ],
    },
    "full_stack_developer": {
        "role_key": "full_stack_developer",
        "title": "Full Stack Developer",
        "category": "Full Stack Engineering",
        "description": "System-defined target-role requirements for end-to-end full stack development.",
        "required_skills": [
            "JavaScript",
            "React",
            "Python",
            "SQL",
            "REST APIs",
            "Git",
            "HTML",
            "CSS",
        ],
        "optional_skills": [
            "TypeScript",
            "PostgreSQL",
            "FastAPI",
            "Docker",
            "Next.js",
        ],
    },
    "data_scientist": {
        "role_key": "data_scientist",
        "title": "Data Scientist",
        "category": "Data Science & Analytics",
        "description": "System-defined target-role requirements for statistical modeling and data insights.",
        "required_skills": [
            "Python",
            "Pandas",
            "NumPy",
            "Data Science",
            "Machine Learning",
            "SQL",
            "Data Visualization",
        ],
        "optional_skills": [
            "Scikit-Learn",
            "TensorFlow",
            "Deep Learning",
            "R",
        ],
    },
    "ui_ux_designer": {
        "role_key": "ui_ux_designer",
        "title": "UI/UX Designer",
        "category": "Design & User Experience",
        "description": "System-defined target-role requirements for user interface and interaction design.",
        "required_skills": [
            "UI/UX Design",
            "Figma",
            "Wireframing",
            "Prototyping",
            "HTML",
            "CSS",
        ],
        "optional_skills": [
            "JavaScript",
            "User Research",
            "Design Systems",
            "Usability Testing",
        ],
    },
    "ai_nlp_engineer": {
        "role_key": "ai_nlp_engineer",
        "title": "AI & NLP Engineer",
        "category": "Artificial Intelligence & NLP",
        "description": "System-defined target-role requirements for NLP and artificial intelligence applications.",
        "required_skills": [
            "Python",
            "Machine Learning",
            "Natural Language Processing",
            "Data Structures & Algorithms",
            "SQL",
        ],
        "optional_skills": [
            "Deep Learning",
            "PyTorch",
            "Transformers",
            "Docker",
            "REST APIs",
        ],
    },
    "devops_cloud_engineer": {
        "role_key": "devops_cloud_engineer",
        "title": "DevOps & Cloud Engineer",
        "category": "Cloud & Infrastructure",
        "description": "System-defined target-role requirements for CI/CD, cloud, and deployment automation.",
        "required_skills": [
            "Linux",
            "Docker",
            "CI/CD",
            "Git",
            "Python",
            "SQL",
        ],
        "optional_skills": [
            "Kubernetes",
            "AWS",
            "Bash",
            "Cloud Computing",
            "Monitoring",
        ],
    },
}

# Role alias mappings to canonical role keys
ROLE_ALIASES: Dict[str, str] = {
    # Software Developer
    "software developer": "software_developer",
    "software engineer": "software_developer",
    "software engineering": "software_developer",
    "swe": "software_developer",
    "sde": "software_developer",
    "programmer": "software_developer",
    # Frontend Developer
    "frontend developer": "frontend_developer",
    "front end developer": "frontend_developer",
    "frontend engineer": "frontend_developer",
    "front-end developer": "frontend_developer",
    "react developer": "frontend_developer",
    "ui developer": "frontend_developer",
    "web developer": "frontend_developer",
    # Backend Developer
    "backend developer": "backend_developer",
    "back end developer": "backend_developer",
    "backend engineer": "backend_developer",
    "back-end developer": "backend_developer",
    "api developer": "backend_developer",
    "python backend developer": "backend_developer",
    "java backend developer": "backend_developer",
    # Machine Learning Engineer
    "machine learning engineer": "machine_learning_engineer",
    "ml engineer": "machine_learning_engineer",
    "ai engineer": "machine_learning_engineer",
    "machine learning": "machine_learning_engineer",
    "artificial intelligence engineer": "machine_learning_engineer",
    # Full Stack Developer
    "full stack developer": "full_stack_developer",
    "full-stack developer": "full_stack_developer",
    "full stack engineer": "full_stack_developer",
    "fullstack developer": "full_stack_developer",
    "full stack web development": "full_stack_developer",
    "full stack development": "full_stack_developer",
    "web development": "full_stack_developer",
    # Data Scientist
    "data scientist": "data_scientist",
    "data science": "data_scientist",
    "data analyst": "data_scientist",
    "data science and machine learning": "data_scientist",
    # UI/UX Designer
    "ui/ux design": "ui_ux_designer",
    "ui ux design": "ui_ux_designer",
    "ui/ux designer": "ui_ux_designer",
    "ui ux designer": "ui_ux_designer",
    "ui designer": "ui_ux_designer",
    "ux designer": "ui_ux_designer",
    "product designer": "ui_ux_designer",
    # AI & NLP
    "ai and nlp": "ai_nlp_engineer",
    "ai & nlp": "ai_nlp_engineer",
    "nlp engineer": "ai_nlp_engineer",
    "natural language processing": "ai_nlp_engineer",
    # DevOps & Cloud
    "devops engineer": "devops_cloud_engineer",
    "cloud engineer": "devops_cloud_engineer",
    "devops": "devops_cloud_engineer",
    "cloud": "devops_cloud_engineer",
}


def normalize_role_name(raw_role: str) -> Optional[str]:
    """
    Normalizes a role string to a canonical role key.
    Uses direct match, alias lookup, and keyword semantics.
    """
    if not raw_role or not isinstance(raw_role, str):
        return None

    cleaned = re.sub(r"[\-_/&]+", " ", raw_role.strip().lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # 1. Direct match in registry keys
    canonical_key = cleaned.replace(" ", "_")
    if canonical_key in ROLE_REQUIREMENTS_REGISTRY:
        return canonical_key

    # 2. Alias dictionary exact match
    if cleaned in ROLE_ALIASES:
        return ROLE_ALIASES[cleaned]

    # 3. Substring match against known role aliases
    for alias, mapped_key in ROLE_ALIASES.items():
        if alias in cleaned or cleaned in alias:
            return mapped_key

    # 4. Semantic keyword heuristics
    if any(k in cleaned for k in ["ui ux", "ux", "ui/ux", "figma", "designer", "design"]):
        return "ui_ux_designer"
    if any(k in cleaned for k in ["nlp", "natural language", "llm"]):
        return "ai_nlp_engineer"
    if any(k in cleaned for k in ["full stack", "fullstack", "web develop"]):
        return "full_stack_developer"
    if any(k in cleaned for k in ["data science", "data scientist", "data analyst", "analytics"]):
        return "data_scientist"
    if any(k in cleaned for k in ["machine learning", "ml engineer", "ai engineer", "deep learning"]):
        return "machine_learning_engineer"
    if any(k in cleaned for k in ["frontend", "front end", "react"]):
        return "frontend_developer"
    if any(k in cleaned for k in ["backend", "back end"]):
        return "backend_developer"
    if any(k in cleaned for k in ["devops", "cloud", "sre", "kubernetes", "docker"]):
        return "devops_cloud_engineer"
    if any(k in cleaned for k in ["software", "swe", "sde", "developer", "engineer", "programmer"]):
        return "software_developer"

    return "software_developer"


def get_role_requirements(role_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the system-defined requirements dictionary for a given role.
    Falls back gracefully to the closest matching role in the registry.
    """
    canonical_key = normalize_role_name(role_name)
    if not canonical_key or canonical_key not in ROLE_REQUIREMENTS_REGISTRY:
        canonical_key = "software_developer"

    role_dict = ROLE_REQUIREMENTS_REGISTRY[canonical_key]

    # Ensure canonical skill names
    required_canonical = [get_canonical_skill_name(s) or s for s in role_dict["required_skills"]]
    optional_canonical = [get_canonical_skill_name(s) or s for s in role_dict["optional_skills"]]

    return {
        "role_key": role_dict["role_key"],
        "title": role_dict["title"],
        "category": role_dict["category"],
        "description": role_dict["description"],
        "required_skills": required_canonical,
        "optional_skills": optional_canonical,
    }


def list_available_roles() -> List[str]:
    """Returns a list of all human-readable role titles in the registry."""
    return [r["title"] for r in ROLE_REQUIREMENTS_REGISTRY.values()]
