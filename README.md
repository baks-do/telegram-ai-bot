# 🤖 Telegram AI Assistant with SQLite Memory & Gemini API

> **Language / Мова:** **English** | [Читати українською](README_UA.md)

A professional Telegram assistant built with `aiogram 3`, integrated with Google's Gemini AI, and powered by an SQLite database to store user notes and chat history persistent across sessions.

---

## ⚙️ Features

- 🧠 **Context-Aware AI Chat (Gemini API):** Stores conversation history per user in SQLite, allowing the bot to retain dialogue context even after service restarts.
- 📋 **Notes Manager:** Full CRUD note-taking functionality (`/note`, `/notes`, `/del`) bound to individual Telegram `user_id`s.
- ⚡ **Non-blocking Asynchronous Design:** Offloads blocking Gemini API calls using `asyncio.to_thread` to ensure high responsiveness.
- 🔒 **Environment Security:** API keys and sensitive tokens are safely isolated using `python-dotenv`.
- 🧹 **History Reset:** Easy context reset via `/clear` command for both database and in-memory chat sessions.

---

## 🛠 Tech Stack

* **Language:** Python 3.10+
* **Framework:** [aiogram 3.x](https://docs.aiogram.dev/)
* **AI Model:** [google-genai](https://pypi.org/project/google-genai/) (Gemini 2.5 / 1.5 Flash)
* **Database:** SQLite3
* **Security:** `python-dotenv`

---

## 📂 Project Structure

```text
piton/
├── bot3.py           # Main executable bot code
├── bot_memory.db     # SQLite local database (generated automatically)
├── .env              # Environment variables (ignored by Git)
├── .gitignore        # Git ignore rules
├── requirements.txt  # Project dependencies
├── README.md         # English documentation
└── README_UA.md      # Ukrainian documentation