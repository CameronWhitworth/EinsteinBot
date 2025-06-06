# 🤖 EinsteinBot - Your AI-Powered Discord Bot

Welcome to EinsteinBot! This bot harnesses the power of Google's Generative AI to bring intelligent conversations and helpful interactions to your Discord server.

> 🎯 **Looking to use EinsteinBot in your server?**  
> Check out the [user guide](TEMP_CHANGE_LATER) for instructions on adding and using the hosted version of EinsteinBot!

This documentation is for developers who want to build and host their own instance of EinsteinBot or contribute to its development.

## ✨ Features

- 🧠 Powered by Google's Generative AI
- ❓ Ask questions and get intelligent responses
- 📝 Summarize any past conversations with ease
- ✅ Fact-check information and comments to ensure accuracy
- 💬 Natural conversation capabilities
- 🎯 Easy to set up and use
- 🛠️ Customizable prompt management

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- A Discord Bot Token
- Google AI API credentials

### Installation

1. Cone this repository:
```bash
git clone https://github.com/CameronWhitworth/EinsteinBot.git
cd EinsteinBot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables by creating a `.env` file:
```env
DISCORD_TOKEN=your_discord_token_here
GOOGLE_API_KEY=your_google_api_key_here
```

4. Run the bot:
```bash
python bot/main.py
```

## 🏗️ Project Structure

```
EinsteinBot/
├── bot/
│   ├── commands/      # Discord bot commands
│   ├── main.py        # Main bot implementation
│   └── prompt_manager.py  # AI prompt management
├── requirements.txt    # Project dependencies
└── .env               # Environment variables
```

## 🛠️ Dependencies

- `discord.py` - The core Discord API wrapper
- `google-generativeai` - Google's Generative AI interface
- `python-dotenv` - Environment variable management

## Contributing

Feel free to fork this repository and submit pull requests! Always open to improvements and new features.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Powered by Google's Generative AI

---
