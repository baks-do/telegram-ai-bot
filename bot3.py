import asyncio
import sqlite3
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from google import genai
from google.genai import types as genai_types

# Примусове кодування UTF-8 для консолі Windows
sys.stdout.reconfigure(encoding='utf-8')

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

user_chats = {}

# --- Робота з базою даних SQLite ---

def init_db():
    """Створення таблиць для нотаток та історії чатів"""
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    
    # Таблиця нотаток
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL
        )
    """)
    
    # Таблиця історії чатів Gemini
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

# --- Функції нотаток ---

def add_note(user_id: int, text: str) -> int:
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (user_id, text) VALUES (?, ?)", (user_id, text))
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id

def get_user_notes(user_id: int):
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, text FROM notes WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_user_note(user_id: int, note_id: int) -> bool:
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

# --- Функції збереження та завантаження історії чату ---

def save_chat_message(user_id: int, role: str, text: str):
    """Збереження одного повідомлення в БД"""
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)", 
        (user_id, role, text)
    )
    conn.commit()
    conn.close()

def load_chat_history(user_id: int):
    """Отримання історії повідомлень та форматування її для Gemini SDK"""
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, message FROM chat_history WHERE user_id = ? ORDER BY id ASC", 
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    history = []
    for role, message in rows:
        history.append(
            genai_types.Content(
                role=role,
                parts=[genai_types.Part.from_text(text=message)]
            )
        )
    return history

def clear_user_chat_history(user_id: int):
    """Видалення історії чату з БД"""
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# --- Команди бота ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "Привіт! Я твій розумний асистент із вічною пам'яттю у SQLite. 🤖📝\n\n"
        "• **/note <текст>** — зберегти текст як нотатку.\n"
        "• **/notes** — переглянути свої нотатки.\n"
        "• **/del <ID>** — видалити нотатку за номером.\n"
        "• **/clear** — повністю очистити історію діалогу (і з БД також).\n"
        "• **Будь-який текст** — спілкування з Gemini!"
    )

@dp.message(Command("note"))
async def add_note_cmd(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Напиши текст нотатки після команди. Наприклад:\n`/note Купити каву`", parse_mode="Markdown")
        return

    user_id = message.from_user.id
    note_text = args[1]
    note_id = add_note(user_id, note_text)
    
    await message.answer(f"✅ Нотатку №{note_id} збережено в БД!")

@dp.message(Command("notes"))
async def show_notes_cmd(message: types.Message):
    user_id = message.from_user.id
    notes = get_user_notes(user_id)
    
    if not notes:
        await message.answer("📭 У тебе немає збережених нотаток.")
        return

    text = "📋 **Твої нотатки:**\n\n"
    for note_id, note_text in notes:
        text += f"[{note_id}] {note_text}\n"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("del"))
async def delete_note_cmd(message: types.Message):
    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await message.answer("⚠️ Вкажи номер нотатки. Наприклад: `/del 1`", parse_mode="Markdown")
        return

    user_id = message.from_user.id
    note_id = int(args[1])
    
    if delete_user_note(user_id, note_id):
        await message.answer(f"🗑 Нотатку №{note_id} видалено!")
    else:
        await message.answer(f"❌ Нотатку №{note_id} не знайдено.")

@dp.message(Command("clear"))
async def clear_history_cmd(message: types.Message):
    user_id = message.from_user.id
    
    # Видаляємо з оперативної пам'яті
    if user_id in user_chats:
        del user_chats[user_id]
        
    # Видаляємо з бази даних
    clear_user_chat_history(user_id)
    await message.answer("🧹 Історію діалогу успішно очищено з бази даних!")

@dp.message()
async def ai_chat_handler(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    user_id = message.from_user.id

    # Якщо сесії немає в оперативній пам'яті, відновлюємо її з SQLite
    if user_id not in user_chats:
        saved_history = load_chat_history(user_id)
        user_chats[user_id] = ai_client.chats.create(
            model="gemini-3.6-flash",
            history=saved_history
        )

    try:
        response = await asyncio.to_thread(
            user_chats[user_id].send_message,
            message.text
        )
        
        # Зберігаємо нове повідомлення користувача та відповідь ШІ у БД
        save_chat_message(user_id, "user", message.text)
        save_chat_message(user_id, "model", response.text)

        await message.answer(response.text)
    except Exception as e:
        await message.answer(f"❌ Помилка при зверненні до ШІ: {e}")

async def main():
    init_db()  # Створення/перевірка таблиць у БД
    print("Бот запущений! Історія чатів тепер зберігається у SQLite.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())