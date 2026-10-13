"""
Deterministic Task Analyzer and Router for CareerVerse AI Multi-Agent System.

Analyzes natural language queries and extracts:
1. Target Job Role (if present or deterministically matched against role registry)
2. Primary Intent (recommendation, evaluation, interview, combined, general_rag)
3. Required Specialized Agent Tasks (ordered deterministically for dependency flow)
"""

import logging
from typing import List, Optional, Tuple

from app.ai.agents.role_requirements import (
    get_role_requirements,
    list_available_roles,
    normalize_role_name,
)
from app.ai.language.normalizer import query_normalizer

logger = logging.getLogger("careerverse.ai.agents.task_router")


class TaskRouter:
    """
    Deterministic rule-based task analyzer for multi-agent career intelligence.
    Determines which specialized agents (Recommendation, Evaluation, Interview)
    must execute and in what order across English and multilingual queries (Tamil, Hindi, etc.).
    """

    KNOWN_ROLE_PATTERNS = [
        ("software developer", "Software Developer"),
        ("software engineer", "Software Developer"),
        ("software engineering", "Software Developer"),
        ("frontend developer", "Frontend Developer"),
        ("frontend development", "Frontend Developer"),
        ("frontend engineer", "Frontend Developer"),
        ("backend developer", "Backend Developer"),
        ("backend development", "Backend Developer"),
        ("backend engineer", "Backend Developer"),
        ("machine learning engineer", "Machine Learning Engineer"),
        ("machine learning engineering", "Machine Learning Engineer"),
        ("ml engineer", "Machine Learning Engineer"),
        ("full stack developer", "Full Stack Developer"),
        ("full-stack developer", "Full Stack Developer"),
        ("full stack engineer", "Full Stack Developer"),
        ("data scientist", "Data Scientist"),
        ("data science", "Data Scientist"),
        ("rocket propulsion engineer", "Rocket Propulsion Engineer"),
    ]

    RECOMMENDATION_KEYWORDS = [
        # English
        "recommend", "recommendation", "career role", "career roles",
        "career path", "career options", "career direction", "career trajectory",
        "suitable for me", "roles are suitable", "roles match", "roles fit",
        "fit my profile", "fits my profile", "match my profile", "matches my profile",
        "jobs match", "job match", "what role", "what roles", "which role", "which roles",
        "technology roles", "software development roles", "path should i explore",
        "suitable career", "suitable jobs", "what careers are suitable",
        # Tamil
        "பொருத்தமான", "பரிந்துரை", "பொருந்தும்", "வேலை வாய்ப்பு", "ரோல்", "பாதையை",
        # Hindi
        "उपयुक्त", "सुझाव", "करियर", "रोल्स", "नौकरी", "मार्ग",
    ]

    EVALUATION_KEYWORDS = [
        # English
        "skill gap", "skill gaps", "missing skill", "missing skills",
        "skills am i missing", "skills do i lack", "lack", "lacking",
        "evaluate my skills", "evaluate skills", "evaluate me",
        "evaluate my gaps", "evaluate my skill", "evaluate gaps",
        "my gaps", "my skill gaps",
        "evaluation", "what should i improve", "areas to improve",
        "improvement areas", "skill coverage", "how ready am i",
        "skills needed for", "am i missing",
        # Tamil
        "skills வேண்டும்", "விடுபட்டுள்ளன", "குறைபாடு", "தேவைப்படும்", "இடைவெளி",
        "கற்க வேண்டும்", "என்ன skills", "மதிப்பிடு",
        # Hindi
        "सीखने चाहिए", "कमी है", "कौशल सीखने", "कमी", "सीखना", "कौशल", "मूल्यांकन",
    ]

    INTERVIEW_KEYWORDS = [
        # English
        "interview", "interviews", "interview question", "interview questions",
        "mock interview", "prepare me for an interview", "prepare me for a",
        "prepare me for backend", "prepare me for software", "prepare me for frontend",
        "prepare me for machine", "prepare me for data", "prepare me for full",
        "ask me questions", "ask questions", "interview preparation",
        "technical questions", "questions based on my", "questions about my",
        "questions for my", "what questions might be asked", "questions might be asked",
        "interview questions for", "prepare interview questions",
        "how should i prepare", "how to prepare", "prepare for interviews",
        "prepare for interview", "interview prep",
        # Tamil
        "நேர்காணல்", "கேள்விகள்", "தயார் செய்வது", "தயாரிப்பு",
        # Hindi
        "साक्षात्कार", "तैयारी", "प्रश्न", "तैयारी कैसे", "सवाल",
    ]

    def extract_target_role(
        self, query: str, explicit_role: Optional[str] = None
    ) -> Optional[str]:
        """
        Deterministically extracts and normalizes the target role from explicit input or query text.
        Supports standard English phrases as well as multilingual script patterns.
        """
        if explicit_role and explicit_role.strip():
            # Check if canonical role exists
            reqs = get_role_requirements(explicit_role.strip())
            if reqs:
                return reqs["title"]
            return explicit_role.strip()

        # Check multilingual role translations
        ml_role = query_normalizer.extract_role_multilingual(query)
        if ml_role:
            return ml_role

        q = query.lower()
        for pattern, canonical in self.KNOWN_ROLE_PATTERNS:
            if pattern in q:
                reqs = get_role_requirements(pattern)
                if reqs:
                    return reqs["title"]
                return canonical

        return None

    def analyze_task(
        self, query: str, explicit_role: Optional[str] = None
    ) -> Tuple[str, List[str], Optional[str]]:
        """
        Analyzes query and explicit role to determine:
        - intent: 'recommendation' | 'evaluation' | 'interview' | 'combined' | 'career_intelligence'
        - tasks: list of agent names to execute, ordered deterministically
        - target_role: extracted or explicit target role
        """
        cleaned_query = query.strip()
        q = cleaned_query.lower()
        target_role = self.extract_target_role(cleaned_query, explicit_role)

        has_rec = any(kw.lower() in q for kw in self.RECOMMENDATION_KEYWORDS)
        has_eval = any(kw.lower() in q for kw in self.EVALUATION_KEYWORDS)
        has_interview = any(kw.lower() in q for kw in self.INTERVIEW_KEYWORDS)

        # Count matched specialized domains
        active_domains = sum([has_rec, has_eval, has_interview])

        # Multi-agent combined workflow
        if active_domains >= 2:
            tasks: List[str] = []
            if has_rec:
                tasks.append("recommendation")
            if has_eval:
                tasks.append("evaluation")
            if has_interview:
                tasks.append("interview")

            logger.info(
                "TaskRouter: Detected COMBINED task with agents %s for role '%s'",
                tasks,
                target_role,
            )
            return "combined", tasks, target_role

        # Single specialized intent workflows
        if has_interview:
            return "interview", ["interview"], target_role

        if has_eval:
            return "evaluation", ["evaluation"], target_role

        if has_rec:
            return "recommendation", ["recommendation"], target_role

        # Fallback heuristic checks
        if ("why" in q or "how" in q) and ("fit" in q or "suitable" in q or "role" in q):
            return "recommendation", ["recommendation"], target_role

        if explicit_role and any(w in q for w in ["gap", "missing", "evaluate", "readiness", "score", "இடைவெளி", "கமி"]):
            return "evaluation", ["evaluation"], target_role

        return "career_intelligence", ["general_rag"], target_role


task_router = TaskRouter()

