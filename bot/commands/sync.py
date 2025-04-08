from discord import app_commands
import discord
from .base_command import BaseCommand

class SyncCommand(BaseCommand):
    def register(self, tree: app_commands.CommandTree):
        @tree.command(name='sync', description='Syncs the command tree (Owner only)')
        async def sync(interaction: discord.Interaction):
            if interaction.user.id != interaction.guild.owner_id:
                await interaction.response.send_message('Only the server owner can use this command!', ephemeral=True)
                return
            
            await interaction.response.defer(ephemeral=True)
            try:
                await self.client.tree.sync()
                await interaction.followup.send('Commands synced successfully!', ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f'Failed to sync commands: {str(e)}', ephemeral=True) 