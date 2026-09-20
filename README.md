# AI-Powered Discord Bot

A multifunctional Discord bot built with Python (`discord.py`), featuring comprehensive server moderation, advanced audit logging, and intelligent conversational capabilities powered by a local AI model via Ollama. 

This project is designed to be fully self-hosted, ensuring privacy and zero API costs by utilizing local LLMs for AI interactions.

## 🚀 Features

### 🤖 Local AI Integration
* **Smart Responses:** Ask questions and interact with the bot using the `!ask` command.
* **Zero API Costs:** Powered by [Ollama](https://ollama.com/) running locally (using Llama 3 / 3.1).
* **Asynchronous Handling:** Built with `aiohttp` to ensure the bot remains responsive while the AI generates answers.

### 🛡️ Moderation & Utility
* **Moderation Commands:** Keep the server clean with `!clear`, `!kick`, and `!ban`.
* **Server Info:** Retrieve real-time server statistics and latency with `!serverinfo` and `!ping`.
* **Custom Help Menu:** A structured, embedded `!help` command that categorizes available tools.

### 📋 Advanced Audit Logging
* **Message Tracking:** Logs deleted and edited messages to a hidden channel.
* **Member Activity:** Tracks when users join or leave the server, including custom welcome banners.
* **Profile Updates:** Monitors and logs changes to user roles and server nicknames.

## 🛠️ Technologies Used
* **Language:** Python 3.x
* **Libraries:** `discord.py`, `aiohttp`, `python-dotenv`
* **AI Backend:** Ollama (Local LLM inference)

## ⚙️ Prerequisites

Before you begin, ensure you have met the following requirements:
1. Python 3.8 or higher installed.
2. A Discord Bot Token (created via the [Discord Developer Portal](https://discord.com/developers/applications)).
3. [Ollama](https://ollama.com/) installed and running locally.
4. An Ollama model pulled locally (e.g., `ollama run llama3.1`).

## 📥 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AndreasKanell/Discord-Bot.git
   cd Discord-Bot
   ```

2. **Install the required dependencies:**
   ```bash
   pip install discord.py aiohttp python-dotenv
   ```

3. **Configure the environment variables:**
   * Create a `.env` file in the root directory.
   * Add your Discord bot token:
     ```env
     DISCORD_TOKEN=your_bot_token_here
     ```

4. **Run the bot:**
   ```bash
   python main.py
   ```