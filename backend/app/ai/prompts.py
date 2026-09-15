class PromptManager:
    @staticmethod
    def test_system_prompt() -> str:
        return (
            "You are CareerVerseAI's test assistant. Answer the user's message "
            "clearly and briefly. Return only JSON matching the requested schema."
        )