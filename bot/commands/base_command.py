from discord import app_commands
import discord

class BaseCommand:
    def __init__(self, client):
        self.client = client
        
    def register(self, tree: app_commands.CommandTree):
        """Register the command with the command tree"""
        raise NotImplementedError("Subclasses must implement register()") 