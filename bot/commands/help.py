from discord import app_commands
import discord
from .base_command import BaseCommand

class HelpCommand(BaseCommand):
    def register(self, tree: app_commands.CommandTree):
        @tree.command(
            name="help",
            description="Get detailed information about EinsteinBot's commands and features"
        )
        async def help_command(interaction: discord.Interaction):
            help_message = """🤖 **EinsteinBot Help Guide** 🤖

**Key Features:**
• 🧠 Powered by Google's Generative AI
• 💬 Natural conversation capabilities
• 📝 Context-aware responses (works with message replies)
• ⏱️ 5-second cooldown between mentions
• ✅ Fact-checking capabilities
• 📊 Conversation summarization
• 🔍 Conversation analysis

**How to Use EinsteinBot:**
1. Direct Mention: Type `@EinsteinAI` followed by your question
2. Slash Commands: Use `/` followed by the command name

**Available Commands:**

📚 **/einstein [question]**
Ask EinsteinBot any question and get an AI-powered response.
• Example: `/einstein What is the theory of relativity?`
• Works with direct mentions too: `@EinsteinBot explain quantum physics`

📝 **/summarize [number]**
Get a summary of recent conversation in the channel.
• Default: 150 messages
• Maximum: 500 messages
• Example: `/summarize 200`

✅ **/factcheck [statement]**
Fact-check any statement or claim.
• Provides detailed analysis
• Indicates if claims are true, false, or unverifiable
• Example: `/factcheck The Earth is flat`

🔍 **/factcheckhistory [number]**
Analyze recent conversation for factual accuracy.
• Reviews the last 50 messages by default
• Can analyze up to 500 messages
• Provides a detailed analysis of factual claims
• Example: `/factcheckhistory 100`

**Important Notes:**
• I respond to direct mentions if used anywhere in the message
• I ignore @everyone, @here, and role mentions
• Slash commands are always available
• Responses may be split into multiple messages if they're long

⚠️ **Important Warning:** 
While I aim to provide accurate information, I'm an AI and can sometimes make mistakes.
I currently do not have access to the internet, so I cannot access the latest information.
Always verify critical information from reliable sources.

Happy learning! 🎓"""

            await interaction.response.send_message(help_message, ephemeral=True) 