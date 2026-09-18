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