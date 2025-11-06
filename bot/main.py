import discord
from discord import app_commands
import google.generativeai as genai
import os
from dotenv import load_dotenv
from commands import EinsteinCommand, SummarizeCommand, SyncCommand, FactCheckCommand, FactCheckHistoryCommand, HelpCommand
from commands.automod import AutoModCommand
from prompt_manager import PromptManager
from automod import AutoMod
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

# Initialize auto-moderation
automod = AutoMod()

class EinsteinBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.cooldowns = {}
        self.webhook_cache = {}  # Cache webhooks per channel
        
        # Initialize commands
        self.einstein_cmd = EinsteinCommand(self, model, prompt_manager)
        self.summarize_cmd = SummarizeCommand(self, model, prompt_manager)
        self.sync_cmd = SyncCommand(self)
        self.factcheck_cmd = FactCheckCommand(self, model, prompt_manager)
        self.factcheckhistory_cmd = FactCheckHistoryCommand(self, model, prompt_manager)
        self.help_cmd = HelpCommand(self)
        self.automod_cmd = AutoModCommand(self, automod)
        
        # Register commands
        self.einstein_cmd.register(self.tree)
        self.summarize_cmd.register(self.tree)
        self.sync_cmd.register(self.tree)
        self.factcheck_cmd.register(self.tree)
        self.factcheckhistory_cmd.register(self.tree)
        self.help_cmd.register(self.tree)
        self.automod_cmd.register(self.tree)

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

    async def get_reply_thread_context(self, message, max_messages=50, max_chars=2000):
        context_messages = []
        total_chars = 0
        current = message
        for _ in range(max_messages):
            if not current.reference or not current.reference.message_id:
                break
            parent = await current.channel.fetch_message(current.reference.message_id)
            content = parent.content
            author = parent.author.display_name if hasattr(parent.author, 'display_name') else parent.author.name
            if total_chars + len(content) > max_chars:
                break
            context_messages.append((author, content))
            total_chars += len(content)
            current = parent
        return list(reversed(context_messages))

client = EinsteinBot()

@client.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # Auto-moderation: Check for banned words
    # Skip checking DMs and private channels
    if isinstance(message.channel, (discord.TextChannel, discord.Thread)) and message.guild:
        # Check if bot has permission to manage messages
        if message.channel.permissions_for(message.guild.me).manage_messages:
            banned_words_found = automod.check_message(message.content)
            if banned_words_found:
                try:
                    # Delete the original message
                    await message.delete()
                    
                    # Send warning in red embed box
                    keywords_text = ", ".join(f"`{word}`" for word in banned_words_found)
                    warning_embed = discord.Embed(
                        title="⚠️ Message Flagged",
                        description=f"Message removed because it contained banned word(s): {keywords_text}.",
                        color=0xff6b6b  # Red warning color
                    )
                    await message.channel.send(embed=warning_embed)
                    
                    # Send filtered message using webhook to show user's avatar and name
                    filtered_content = automod.filter_message(message.content)
                    
                    # Get or create webhook for this channel
                    channel_id = message.channel.id
                    if channel_id not in client.webhook_cache:
                        # Try to find existing webhook first
                        webhooks = await message.channel.webhooks()
                        webhook = None
                        for wh in webhooks:
                            if wh.user == client.user:
                                webhook = wh
                                break
                        
                        # Create new webhook if none found
                        if not webhook:
                            webhook = await message.channel.create_webhook(name="AutoMod Filter")
                        
                        client.webhook_cache[channel_id] = webhook
                    else:
                        webhook = client.webhook_cache[channel_id]
                    
                    # Send message via webhook with user's avatar and name
                    await webhook.send(
                        content=filtered_content,
                        username=message.author.display_name,
                        avatar_url=message.author.display_avatar.url
                    )
                except discord.Forbidden:
                    # Bot doesn't have permission to delete messages
                    pass
                except Exception as e:
                    print(f"Error in auto-moderation: {e}")
                return  # Don't process the message further

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
            await message.reply(f"Please wait {remaining:.1f} seconds before using this command again.")
            return

        prompt = message.content.replace(f"<@{client.user.id}>", "").replace(f"<@!{client.user.id}>", "").strip()

        if not prompt:
            await message.reply("Please provide a question after mentioning me.")
            return

        try:
            await message.channel.typing()
            # Gather reply thread context as a list of (author, content)
            thread_context = await client.get_reply_thread_context(message, max_messages=50, max_chars=2000)
            replies = client.einstein_cmd.generate_response(prompt, thread_context)
            for reply in replies:
                await message.reply(reply)
        except Exception as e:
            await message.reply(f"Error: {str(e)}")

@client.event
async def on_guild_join(guild):
    # Find the first available text channel to send the welcome message
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(f"👋 Hello! I'm Einstein! I'm here to help with various tasks including:\n"
                             f"• Answering questions (just mention me)\n"
                             f"• Summarizing text\n"
                             f"• Fact checking\n"
                             f"• And more!\n\n"
                             f"Use `/help` to see all available commands!")
            break

client.run(DISCORD_TOKEN)
