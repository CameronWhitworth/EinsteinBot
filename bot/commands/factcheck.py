from discord import app_commands
import discord
from .base_command import BaseCommand
import google.generativeai as genai
from typing import List

class FactCheckCommand(BaseCommand):
    def __init__(self, client, model, prompt_manager):
        super().__init__(client)
        self.model = model
        self.prompt_manager = prompt_manager

    def register(self, tree: app_commands.CommandTree):
        @tree.command(
            name="factcheck",
            description="Fact check a statement or claim"
        )
        @app_commands.describe(
            statement="The statement or claim you want to fact check"
        )
        async def factcheck(interaction: discord.Interaction, statement: str):
            await interaction.response.defer()

            try:
                # Construct the prompt for fact-checking
                prompt = f"""Please fact check the following statement and provide a detailed analysis. 
                For each claim, indicate if it's:
                - True (with supporting evidence)
                - False (with correction)
                - Partially True/Misleading (with clarification)
                - Unverifiable (explain why)

                Statement to fact check: "{statement}"

                Please be thorough but concise in your analysis."""

                response = self.model.generate_content(prompt)
                
                # Split response into chunks if needed (Discord has a 2000 char limit)
                response_text = response.text
                chunks = self._split_response(response_text)
                
                for chunk in chunks:
                    await interaction.followup.send(chunk)

            except Exception as e:
                await interaction.followup.send(f"Error during fact-checking: {str(e)}", ephemeral=True)

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