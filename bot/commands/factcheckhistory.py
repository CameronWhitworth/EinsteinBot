from discord import app_commands
import discord
from .base_command import BaseCommand
from typing import List

class FactCheckHistoryCommand(BaseCommand):
    MAX_MESSAGES = 500  # Maximum number of messages that can be analyzed
    DEFAULT_MESSAGES = 50  # Default number of messages if not specified

    def __init__(self, client, model, prompt_manager):
        super().__init__(client)
        self.model = model
        self.prompt_manager = prompt_manager

    async def _fetch_messages(self, channel, limit: int) -> List[str]:
        """Fetch recent messages from the channel."""
        messages = []
        async for message in channel.history(limit=limit):
            # Skip bot messages
            if message.author.bot:
                continue
            messages.append(f"{message.author.name}: {message.content}")
        
        # Reverse messages to get chronological order
        messages.reverse()
        return messages

    def _split_response(self, text: str, max_length: int = 1900) -> List[str]:
        """Split a response into chunks that fit within Discord's message limit."""
        if len(text) <= max_length:
            return [text]
            
        chunks = []
        current_chunk = ""
        
        for paragraph in text.split('\n\n'):
            if len(current_chunk) + len(paragraph) + 2 <= max_length:
                current_chunk += (paragraph + '\n\n')
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def register(self, tree: app_commands.CommandTree):
        @tree.command(
            name="factcheckhistory",
            description="Analyze recent conversation for factual accuracy"
        )
        @app_commands.describe(
            messages=f"Number of messages to analyze (default: {self.DEFAULT_MESSAGES}, max: {self.MAX_MESSAGES})"
        )
        async def factcheckhistory(
            interaction: discord.Interaction,
            messages: app_commands.Range[int, 1, 500] = self.DEFAULT_MESSAGES
        ):
            await interaction.response.defer()

            try:
                # Fetch messages
                message_list = await self._fetch_messages(interaction.channel, messages)
                
                if not message_list:
                    await interaction.followup.send("No messages found to analyze.")
                    return

                # Construct the prompt for fact-checking
                messages_text = "\n".join(message_list)
                prompt = f"""A user has requested to fact-check the recent conversation in a channel.
                Please analyze the following messages and provide a detailed fact-checking report.
                For each factual claim made, indicate if it's:
                - True (with supporting evidence)
                - False (with correction)
                - Partially True/Misleading (with clarification)
                - Unverifiable (explain why)

                Messages to analyze:
                {messages_text}

                Please provide a comprehensive analysis of the factual accuracy of these messages.
                Focus on verifiable claims and provide evidence where possible.
                Be thorough but concise in your analysis.
                Group similar claims together when possible to avoid repetition."""

                response = self.model.generate_content(prompt)
                
                # Split response into chunks if needed
                chunks = self._split_response(response.text)
                
                # Send initial message with context
                await interaction.followup.send(
                    f"🔍 Analyzing the last {len(message_list)} messages:\n"
                    f"*Note: This analysis is based on AI interpretation and may not be 100% accurate.*"
                )
                
                # Send the analysis chunks
                for chunk in chunks:
                    await interaction.followup.send(chunk)

            except Exception as e:
                await interaction.followup.send(f"Error during fact-checking: {str(e)}", ephemeral=True) 