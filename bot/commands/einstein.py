from discord import app_commands
import discord
from .base_command import BaseCommand

class EinsteinCommand(BaseCommand):
    def __init__(self, client, model, prompt_manager):
        super().__init__(client)
        self.model = model
        self.prompt_manager = prompt_manager

    def generate_response(self, prompt: str, context: str = "") -> list[str]:
        # Use prompt manager to wrap the question
        wrapped_prompt = self.prompt_manager.wrap_question(prompt, context)
        
        response = self.model.generate_content(wrapped_prompt)
        text = response.text

        MAX_LEN = 2000
        return [text[i:i+MAX_LEN] for i in range(0, len(text), MAX_LEN)]

    def register(self, tree: app_commands.CommandTree):
        @tree.command(name="einstein", description="Ask Einstein a question")
        @app_commands.describe(prompt="Your question for Einstein")
        async def einstein_command(interaction: discord.Interaction, prompt: str):
            await interaction.response.defer()
            try:
                # Check if the command is used in reply to a message
                context = ""
                if interaction.message and interaction.message.reference:
                    referenced_msg = await interaction.channel.fetch_message(interaction.message.reference.message_id)
                    if referenced_msg:
                        context = referenced_msg.content

                replies = self.generate_response(prompt, context)
                for reply in replies:
                    await interaction.followup.send(reply)
            except Exception as e:
                await interaction.followup.send(f"Error: {str(e)}") 