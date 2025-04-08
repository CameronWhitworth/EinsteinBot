class PromptManager:
    def __init__(self):
        self.base_personality = (
            "You are a Discord bot called Einstein. "
            "Keep responses concise, clear, and under 4000 characters. "
        )

    def wrap_question(self, prompt: str, context: str = "") -> str:
        """Wrap a question with the bot's personality."""
        if context:
            return (
                f"{self.base_personality}\n\n"
                f"Someone said: {context}\n"
                f"Question about this: {prompt}"
            )
        return f"{self.base_personality}\n\nQuestion: {prompt}"

    def wrap_summary(self, conversation: str, message_count: int) -> str:
        """Wrap a conversation for summarization."""
        return (
            f"{self.base_personality}\n\n"
            "Please provide a concise summary of the following conversation. "
            "Focus on the main topics, key points of discussion, and any conclusions reached. "
            "Keep your summary under 2000 characters.\n\n"
            f"Analyzing the last {message_count} messages:\n"
            f"Conversation:\n{conversation}"
        ) 