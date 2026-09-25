# 🤖 Discord AI & Multi-Tool Bot

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2.svg)](https://discordpy.readthedocs.io/)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20(Llama%203.1)-black.svg)](https://ollama.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A powerful, self-hosted Discord bot written in Python using **`discord.py`**. The bot integrates a **local AI conversational assistant** powered by **Ollama (`llama3.1`)**, an automated **server audit logging system**, interactive **moderation & utility tools**, live **weather updates**, and an interactive **tech trivia game** with Discord UI buttons.

---

## 🌟 Key Highlights

- **🧠 Local AI Conversational System:** Mention the bot (`@Bot`) to chat with a local LLM running zero-cost inference via Ollama. Features sliding-window memory, typing status, and automatic message chunking.
- **🛡️ Server Moderation:** Built-in commands for clearing messages, kicking, and banning members with Discord permission checks.
- **📋 Automated Audit Logging:** Real-time event tracking for deleted messages, edited messages, member joins (with custom welcome DMs and auto-role assignment), member departures, nickname changes, and role updates.
- **🌤️ Live Weather Forecasts:** Real-time global weather conditions powered by the OpenWeatherMap API with temperature, feels-like, humidity, and condition icons.
- **🎮 Interactive Trivia Quiz:** Dynamic Computer Science quizzes powered by the OpenTDB API, featuring interactive Discord UI buttons (`discord.ui.View`) with a 15-second countdown timer.

---

## 🤖 Deep Dive: AI Interaction System

The bot features a custom, privacy-focused conversational AI layer integrated directly into the Discord message pipeline via `on_message`:

```
User Message (@Bot) 
       │
       ▼
Strip @Mention & Retrieve User History (Dict)
       │
       ▼
Append Query + Maintain Sliding Window (MAX_HISTORY = 10)
       │
       ▼
Trigger Typing Indicator (`async with channel.typing()`)
       │
       ▼
Async HTTP POST (`aiohttp`) ──► Local Ollama API (`/api/chat`) [llama3.1]
       │
       ▼
Receive Response & Append to User History
       │
       ▼
`send_long_message()` ──► Split chunks (<1900 chars) ──► Discord Reply
```

### 1. Mention-Based Triggers (`@Bot`)
Instead of rigid command prefixes, users can mention the bot anywhere in a message (e.g., `@Bot how do binary search trees work?`). The bot strips the mention tag `<@bot.user.id>` and forwards the clean prompt to the AI.

### 2. Conversational Memory & Sliding Window
- **Per-User Memory (`user_histories`):** Conversation state is tracked per Discord user ID, allowing multi-turn conversations where the AI remembers previous questions and context.
- **System Persona:** Each user session begins with a system prompt:
  > *"You are a helpful, conversational AI assistant on a Discord server. Give clear and practical answers."*
- **Context Limit Management (`MAX_HISTORY = 10`):** To avoid memory exhaustion and stay within LLM context windows, history is automatically trimmed. The system prompt at index 0 is preserved while keeping the latest 10 messages:
  ```python
  if len(user_histories[user_id]) > MAX_HISTORY + 1:
      user_histories[user_id] = [user_histories[user_id][0]] + user_histories[user_id][-MAX_HISTORY:]
  ```

### 3. Non-Blocking Async Inference
Calls to Ollama's `/api/chat` endpoint are made asynchronously using `aiohttp.ClientSession()`. This ensures the bot's event loop is never blocked, allowing other users and commands to function smoothly while the model generates text.

### 4. Smart Message Chunking (`send_long_message`)
Discord limits standard messages to **2,000 characters**. AI models frequently generate long, detailed explanations that would otherwise trigger API errors:
- The custom helper `send_long_message` splits responses into safe 1,900-character segments.
- The first segment replies directly to the user's prompt (`reference_message.reply`), and subsequent segments follow sequentially in the channel.

### 5. Command Fallthrough Guarantee
Because overriding `on_message` intercepts all incoming chat, `await bot.process_commands(message)` is explicitly invoked at the end of the handler, ensuring standard commands (`!weather`, `!quiz`, `!help`, etc.) continue to execute seamlessly.

---

## 📂 Code Structure & `main.py` Walkthrough

The bot logic is encapsulated in `main.py`, structured into clean, modular blocks:

| Section | Lines in `main.py` | Description |
| :--- | :--- | :--- |
| **Setup & Config** | `1 – 24` | Loads `.env` token, initializes `intents` (`message_content`, `members`), configures logging to `discord.log`, and sets up command prefix `!`. |
| **Welcome System** | `29 – 57` | `on_member_join` sends a private welcome DM, posts an embed banner to the welcome channel, and auto-assigns the `"Member"` role. |
| **Audit Logging** | `58 – 161` | Event handlers (`on_message_delete`, `on_message_edit`, `on_member_remove`, `on_member_update`) logging deletions, edits, leaves, nickname changes, and role updates to designated channels. |
| **Basic Commands** | `162 – 198` | Utility commands: `!hello`, `!add_role`, `!remove_role`, `!dm`, and `!reply`. |
| **Moderation** | `199 – 218` | Server management: `!clear` (bulk purge), `!kick`, and `!ban` protected by Discord permissions (`manage_messages`, `kick_members`, `ban_members`). |
| **Server Diagnostics** | `219 – 244` | `!ping` (WebSocket latency in ms) and `!serverinfo` (embed displaying owner, member count, creation date, server avatar). |
| **AI Interaction** | `245 – 315` | `send_long_message()` helper and `on_message` event handler for local Ollama chat, conversation memory, typing status, and command pass-through. |
| **Weather Integration** | `316 – 357` | `!weather <city>` fetches real-time data from OpenWeatherMap API via `aiohttp` and formats it into a rich embed. |
| **Interactive Trivia** | `358 – 462` | `TriviaView` UI class (`discord.ui.View`) and `!quiz` command fetching CS questions from OpenTDB API with button interactions and a 15-second timeout. |
| **Help System** | `463 – 517` | `!help` custom embed organizing all available bot commands into categorized fields. |
| **Error Handling** | `519 – 534` | `on_command_error` catching `MissingRequiredArgument`, `BadArgument`, and `MissingPermissions` with friendly user messages. |

---

## 📜 Commands Reference

### 🤖 AI System
| Trigger | Usage | Description |
| :--- | :--- | :--- |
| `@Bot <question>` | `@Bot explain quantum computing simply` | Chats with the local Ollama LLM (`llama3.1`) with conversation context memory. |

### 🛡️ Moderation Commands
> Requires appropriate administrator / moderator permissions.

| Command | Arguments | Permissions Required | Description |
| :--- | :--- | :--- | :--- |
| `!clear` | `<amount>` | `Manage Messages` | Bulk deletes the specified number of messages. |
| `!kick` | `<@member> [reason]` | `Kick Members` | Kicks a member from the server with an optional reason. |
| `!ban` | `<@member> [reason]` | `Ban Members` | Bans a member from the server with an optional reason. |

### ℹ️ General & Utility Commands
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `!ping` | None | Displays bot WebSocket latency in milliseconds. |
| `!serverinfo` | None | Displays server statistics (owner, member count, creation date, icon). |
| `!hello` | None | Sends a friendly greeting mentioning the user. |
| `!reply` | `<message>` | Echoes back your text as a direct message reply. |
| `!dm` | `<message>` | Sends the specified message to your direct messages. |
| `!add_role` | None | Assigns the `test-role` role to the command author. |
| `!remove_role` | None | Removes the `test-role` role from the command author. |
| `!help` | None | Displays the formatted help menu with all commands. |

### 🌤️ Weather & 🧠 Entertainment
| Command | Arguments | Description |
| :--- | :--- | :--- |
| `!weather` | `<city>` | Fetches live weather conditions, temperature, humidity, and icons for the given city. |
| `!quiz` | None | Starts a 15-second multiple-choice tech trivia question with interactive buttons **A**, **B**, **C**, **D**. |

---

## ⚙️ Prerequisites

1. **Python 3.8+** installed on your system.
2. **Discord Developer Account:**
   - Create an application and bot token via the [Discord Developer Portal](https://discord.com/developers/applications).
   - Enable **Privileged Gateway Intents**:
     - ✅ **Message Content Intent** (required for `on_message` and command processing)
     - ✅ **Server Members Intent** (required for `on_member_join`, role assignment, audit logs)
3. **Ollama:**
   - Install [Ollama](https://ollama.com/) (available for Windows, macOS, Linux).
   - Pull the default model:
     ```bash
     ollama run llama3.1
     ```
   - Ensure the Ollama local daemon is running on default port `11434`.

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AndreasKanell/Discord-Bot.git
cd Discord-Bot
```

### 2. Create and Activate a Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

> **Note:** If `aiohttp` is not in your `requirements.txt`, install it manually:
> ```bash
> pip install discord.py python-dotenv aiohttp
> ```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### 5. (Optional) Configure Audit Log Channels
In `main.py`, update the channel IDs to match your Discord server's channel IDs:
- **Welcome Channel:** Line 34 (`welcome_channel = bot.get_channel(...)`)
- **Deleted Messages:** Line 65 (`log_channel = bot.get_channel(...)`)
- **Edited Messages:** Line 86 (`log_channel = bot.get_channel(...)`)
- **Member Leave:** Line 106 (`log_channel = bot.get_channel(...)`)
- **Member Update:** Line 124 (`log_channel = bot.get_channel(...)`)

### 6. Start Ollama & Run the Bot
Ensure your Ollama service is active:
```bash
ollama serve
```

Run the bot:
```bash
python main.py
```

When successfully connected, you will see:
```text
<Bot_Name> is online !
```

---

## 📁 Project Structure

```text
discord-bot/
├── .env                  # Environment secrets (Bot token)
├── .gitignore            # Git ignore file (excludes .env, venv, logs)
├── discord.log           # Discord debug log generated on runtime
├── main.py               # Main bot implementation (AI, events, commands)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🛡️ License

This project is licensed under the [MIT License](LICENSE). You are free to modify, distribute, and self-host this bot.