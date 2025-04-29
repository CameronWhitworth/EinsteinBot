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

**How to Use EinsteinBot:**
1. Direct Mention: Type `@EinsteinBot` followed by your question
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

**Important Notes:**
• I only respond to direct mentions at the start of messages
• I ignore @everyone, @here, and role mentions
• Slash commands are always available
• Responses may be split into multiple messages if they're long

**Need More Help?**
Just ask me directly! For example:
`@EinsteinBot how do I use the factcheck command?`

Happy learning! 🎓"""

            await interaction.response.send_message(help_message, ephemeral=True) 