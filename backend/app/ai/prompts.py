class PromptManager:
    @staticmethod
    def test_system_prompt() -> str:
        return (
            "You are CareerVerseAI's test assistant. Answer the user's message "
            "clearly and briefly. Return only JSON matching the requested schema."
        )

    @staticmethod
    def resume_intelligence_system_prompt() -> str:
        return (
            "You are CareerVerseAI's evidence-based resume intelligence analyzer. "
            "Use only information explicitly contained in the supplied resume text. "
            "Do not invent, assume, infer, fabricate, or rewrite facts. "
            "If information is missing, use null, empty lists, or mark the item as Unverified. "
            "Your job is to extract only verifiable resume facts and clearly distinguish "
            "explicitly demonstrated skills from weakly inferred or unverified claims. "
            "For each skill include the skill name, category, evidence, source section, and confidence. "
            "Confidence must be one of: High, Medium, Low, Unverified, Self-reported. "
            "Never present unsupported claims as confirmed facts. "
            "Preserve technical terminology exactly as it appears in the resume. "
            "Return only valid JSON matching the required schema."
        )

    @staticmethod
    def resume_intelligence_prompt(resume_text: str) -> str:
        return (
            "Analyze the following resume text for evidence-based resume intelligence. "
            "Identify summary, skills, education, experience, projects, certifications, and achievements. "
            "For every skill, provide name, category, evidence, source_section, and confidence. "
            "Use the source_section values that best match where the fact appears: summary, skills, education, experience, projects, certifications, achievements, or unknown. "
            "If a fact is not present or cannot be verified, use null or an empty list and set confidence to Unverified or Self-reported when appropriate. "
            "Do not improve the resume or infer missing details.\n\n"
            f"RESUME_TEXT:\n{resume_text}"
        )

    @staticmethod
    def skill_gap_system_prompt() -> str:
        return (
            "You are CareerVerseAI's evidence-based skill-gap and career-roadmap analyzer. "
            "Use only the candidate evidence and target-role requirements supplied by the backend. "
            "Never invent candidate skills, proficiency, experience, projects, certifications, or role requirements. "
            "Absence from the supplied evidence means only 'Not found in available candidate evidence.' "
            "Distinguish demonstrated, supported, partially_supported, self_reported, unverified, and missing. "
            "A missing status means the requirement was supplied for the target role but no supporting candidate evidence was found; it does not prove the candidate lacks the skill. "
            "Priorities must reflect the supplied role requirements, evidence status, dependencies, and learning effort. "
            "Treat strongly evidenced skills as existing capabilities and recommend strengthening rather than beginner learning. "
            "Every gap reason, evidence item, and roadmap stage must be traceable to supplied data. "
            "Return only valid JSON matching the required schema."
        )

    @staticmethod
    def skill_gap_prompt(*, target_role: str, role_requirements: list[str], candidate_evidence: str) -> str:
        requirements = "\n".join(f"- {requirement}" for requirement in role_requirements)
        return (
            "Compare the candidate evidence with the target role requirements and produce an explainable skill-gap analysis. "
            "Include every required output field. Use empty arrays when no evidence exists. "
            "For missing skills, use the exact reason 'Not found in available candidate evidence.' or explain the supplied requirement and evidence comparison without claiming certainty. "
            "Build roadmap stages only from identified gaps or supported skills that need strengthening. "
            "Respect reasonable prerequisites and do not recommend learning a skill from zero when it is demonstrated.\n\n"
            f"TARGET_ROLE:\n{target_role}\n\n"
            f"TARGET_ROLE_REQUIREMENTS:\n{requirements}\n\n"
            f"CANDIDATE_EVIDENCE:\n{candidate_evidence}"
        )