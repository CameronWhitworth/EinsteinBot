import discord
from discord import app_commands
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def generate_safe_response(prompt: str, context: str = "") -> list[str]:
    # Create a personality wrapper for Einstein
    base_prompt = (
        "You are a Discord bot called Einstein"
        "Keep responses concise, and under 4000 characters. "
    )
    
    # If there's context from a replied message, include it
    if context:
        wrapped_prompt = (
            f"{base_prompt}\n\n"
            f"Someone said: {context}\n"
            f"Question about this: {prompt}"
        )
    else:
        wrapped_prompt = f"{base_prompt}\n\nQuestion: {prompt}"

    response = model.generate_content(wrapped_prompt)
    text = response.text

    MAX_LEN = 2000
    chunks = [text[i:i+MAX_LEN] for i in range(0, len(text), MAX_LEN)]
    return chunks

class EinsteinBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = EinsteinBot()

# Add owner-only sync command
@client.tree.command(name='sync', description='Syncs the command tree (Owner only)')
async def sync(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message('Only the server owner can use this command!', ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    try:
        await client.tree.sync()
        await interaction.followup.send('Commands synced successfully!', ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f'Failed to sync commands: {str(e)}', ephemeral=True)

@client.tree.command(name="einstein", description="Ask Einstein a question")
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

        replies = generate_safe_response(prompt, context)
        for reply in replies:
            await interaction.followup.send(reply)
    except Exception as e:
        await interaction.followup.send(f"Error: {str(e)}")

@client.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if bot is mentioned
    if client.user.mentioned_in(message):
        prompt = message.content.replace(f"<@{client.user.id}>", "").strip()

        if not prompt:
            await message.channel.send("Please provide a question after mentioning me.")
            return

        try:
            await message.channel.typing()
            # Check if the message is a reply to another message
            context = ""
            if message.reference and message.reference.resolved:
                context = message.reference.resolved.content

            replies = generate_safe_response(prompt, context)
            for reply in replies:
                await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"Error: {str(e)}")

client.run(DISCORD_TOKEN)
