from discord import app_commands
import discord
from .base_command import BaseCommand

class AutoModCommand(BaseCommand):
    def __init__(self, client, automod):
        super().__init__(client)
        self.automod = automod
    
    def register(self, tree: app_commands.CommandTree):
        automod_ref = self.automod  # Store reference to avoid closure issues
        
        @tree.command(
            name="banword",
            description="Add a word to the auto-moderation ban list"
        )
        @app_commands.describe(word="The word to ban")
        async def banword_command(interaction: discord.Interaction, word: str):
            # Check if command is used in a guild
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            # Check if user is an administrator
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You need Administrator permissions to use this command.",
                    ephemeral=True
                )
                return
            
            if automod_ref.add_word(word):
                await interaction.response.send_message(
                    f"✅ Added '{word}' to the ban list.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"⚠️ '{word}' is already in the ban list or is invalid.",
                    ephemeral=True
                )
        
        @tree.command(
            name="unbanword",
            description="Remove a word from the auto-moderation ban list"
        )
        @app_commands.describe(word="The word to remove from ban list")
        async def unbanword_command(interaction: discord.Interaction, word: str):
            # Check if command is used in a guild
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            # Check if user is an administrator
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ You need Administrator permissions to use this command.",
                    ephemeral=True
                )
                return
            
            if automod_ref.remove_word(word):
                await interaction.response.send_message(
                    f"✅ Removed '{word}' from the ban list.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"⚠️ '{word}' is not in the ban list.",
                    ephemeral=True
                )
        
        @tree.command(
            name="listbanwords",
            description="List all words in the auto-moderation ban list"
        )
        async def listbanwords_command(interaction: discord.Interaction):
            # Check if command is used in a guild
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            # Check if user has manage_messages permission
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message(
                    "❌ You need the 'Manage Messages' permission to use this command.",
                    ephemeral=True
                )
                return
            words = automod_ref.get_all_words()
            if words:
                words_list = "\n".join(f"• {word}" for word in words)
                message = f"**Banned Words ({len(words)}):**\n{words_list}"
                # Discord has a 2000 character limit, so split if needed
                if len(message) > 2000:
                    chunks = []
                    current_chunk = f"**Banned Words ({len(words)} total):**\n"
                    for word in words:
                        word_line = f"• {word}\n"
                        if len(current_chunk) + len(word_line) > 1900:
                            chunks.append(current_chunk)
                            current_chunk = word_line
                        else:
                            current_chunk += word_line
                    if current_chunk:
                        chunks.append(current_chunk)
                    
                    await interaction.response.send_message(chunks[0], ephemeral=True)
                    for chunk in chunks[1:]:
                        await interaction.followup.send(chunk, ephemeral=True)
                else:
                    await interaction.response.send_message(message, ephemeral=True)
            else:
                await interaction.response.send_message(
                    "📝 The ban list is currently empty.",
                    ephemeral=True
                )

