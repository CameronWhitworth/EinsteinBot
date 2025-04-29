import discord
from discord import app_commands
import google.generativeai as genai
import os
from dotenv import load_dotenv
from commands import EinsteinCommand, SummarizeCommand, SyncCommand, FactCheckCommand, HelpCommand
from prompt_manager import PromptManager
from discord.app_commands import Cooldown
from discord import app_commands
from typing import Optional
import datetime

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Initialize prompt manager
prompt_manager = PromptManager()

class EinsteinBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.cooldowns = {}
        
        # Initialize commands
        self.einstein_cmd = EinsteinCommand(self, model, prompt_manager)
        self.summarize_cmd = SummarizeCommand(self, model, prompt_manager)
        self.sync_cmd = SyncCommand(self)
        self.factcheck_cmd = FactCheckCommand(self, model, prompt_manager)
        self.help_cmd = HelpCommand(self)
        
        # Register commands
        self.einstein_cmd.register(self.tree)
        self.summarize_cmd.register(self.tree)
        self.sync_cmd.register(self.tree)
        self.factcheck_cmd.register(self.tree)
        self.help_cmd.register(self.tree)

    async def setup_hook(self):
        await self.tree.sync()

    def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int = 5) -> Optional[float]:
        """Check if a command is on cooldown for a user."""
        now = datetime.datetime.now().timestamp()
        key = f"{user_id}:{command}"
        
        if key in self.cooldowns:
            last_used = self.cooldowns[key]
            if now - last_used < cooldown_seconds:
                return cooldown_seconds - (now - last_used)
        
        self.cooldowns[key] = now
        return None

client = EinsteinBot()

@client.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if bot is mentioned
    if client.user.mentioned_in(message):
        # Ignore @everyone and similar commands
        if any(mention in message.content.lower() for mention in ['@everyone', '@here', '@role']):
            return

        # Check if the message contains any role mentions
        if message.role_mentions:
            return

        # Check cooldown
        remaining = client.check_cooldown(message.author.id, "mention", 5)
        if remaining:
            await message.channel.send(f"Please wait {remaining:.1f} seconds before using this command again.")
            return

        prompt = message.content.replace(f"<@{client.user.id}>", "").replace(f"<@!{client.user.id}>", "").strip()

        if not prompt:
            await message.channel.send("Please provide a question after mentioning me.")
            return

        try:
            await message.channel.typing()
            # Check if the message is a reply to another message
            context = ""
            if message.reference and message.reference.resolved:
                context = message.reference.resolved.content

            replies = client.einstein_cmd.generate_response(prompt, context)
            for reply in replies:
                await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"Error: {str(e)}")

client.run(DISCORD_TOKEN)
