from discord import app_commands
import discord
from .base_command import BaseCommand

class SummarizeCommand(BaseCommand):
    MAX_MESSAGES = 500  # Maximum number of messages that can be summarized
    DEFAULT_MESSAGES = 150  # Default number of messages if not specified

    def __init__(self, client, model, prompt_manager):
        super().__init__(client)
        self.model = model
        self.prompt_manager = prompt_manager

    async def _fetch_messages(self, channel, limit: int) -> list[str]:
        """Fetch and format messages from the channel."""
        messages = []
        async for message in channel.history(limit=limit):
            # Skip bot messages
            if message.author.bot:
                continue
            messages.append(f"{message.author.name}: {message.content}")
        
        # Reverse messages to get chronological order
        messages.reverse()
        return messages

    def _chunk_response(self, text: str, max_length: int = 2000) -> list[str]:
        """Split response into Discord-friendly chunks."""
        return [text[i:i+max_length] for i in range(0, len(text), max_length)]

    async def generate_summary(self, channel, message_limit: int = DEFAULT_MESSAGES) -> list[str]:
        """Generate a summary of the conversation in the channel."""
        # Ensure message limit is within bounds
        message_limit = min(max(1, message_limit), self.MAX_MESSAGES)
        
        # Fetch messages
        messages = await self._fetch_messages(channel, message_limit)
        
        if not messages:
            return ["No messages to summarize."]

        # Create conversation context
        conversation = "\n".join(messages)
        
        # Use prompt manager to wrap the conversation for summarization
        summary_prompt = self.prompt_manager.wrap_summary(conversation, len(messages))
        
        # Generate summary
        response = self.model.generate_content(summary_prompt)
        
        # Split into Discord-friendly chunks
        return self._chunk_response(response.text)

    def register(self, tree: app_commands.CommandTree):
        @tree.command(name="summarize", description="Get a summary of recent conversation")
        @app_commands.describe(
            messages=f"Number of messages to summarize (default: {self.DEFAULT_MESSAGES}, max: {self.MAX_MESSAGES})"
        )
        async def summarize_command(
            interaction: discord.Interaction,
            messages: app_commands.Range[int, 1, 500] = self.DEFAULT_MESSAGES
        ):
            await interaction.response.defer()
            try:
                replies = await self.generate_summary(interaction.channel, messages)
                # Send the message count as context
                await interaction.followup.send(f"📝 Summarizing the last {messages} messages:")
                for reply in replies:
                    await interaction.followup.send(reply)
            except Exception as e:
                await interaction.followup.send(f"Error: {str(e)}") 