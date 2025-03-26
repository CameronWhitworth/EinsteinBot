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

# Helper function to keep responses Discord-safe
def generate_safe_response(prompt: str) -> list[str]:
    wrapped_prompt = (
        "You are a discord bot."
        "Please keep your response concise and under 4000 characters. "
        "Focus only on the essential details.\n\n" + prompt
    )
    response = model.generate_content(wrapped_prompt)
    text = response.text

    MAX_LEN = 2000
    chunks = [text[i:i+MAX_LEN] for i in range(0, len(text), MAX_LEN)]
    return chunks

class GeminiBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True  # Required to read message content
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = GeminiBot()

@client.tree.command(name="ai", description="Ask Gemini a question")
@app_commands.describe(prompt="Your question for the AI")
async def ai(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    try:
        replies = generate_safe_response(prompt)
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
            await message.channel.send("Please provide a prompt after mentioning me.")
            return

        try:
            await message.channel.typing()
            replies = generate_safe_response(prompt)
            for reply in replies:
                await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"Error: {str(e)}")

client.run(DISCORD_TOKEN)
