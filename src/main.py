import requests
import openai
import schedule
import sqlite3
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")


def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    return response.json()


def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    response = requests.post(url, data=payload)
    return response.json()


def generate_phrases():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Generate 5 Greek phrases for B1 level with translation. One phrase - one line",
            }
        ],
    )
    return response.choices[0].message.content


def save_chats(conn, updates):
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER UNIQUE)"
    )
    chats_to_add = set()
    chats_to_remove = set()
    for update in updates:
        chat_id = update["message"]["chat"]["id"]
        message = update["message"].get("text", "")
        # If message is /start, add chat_id to set
        if message == "/start":
            chats_to_add.add(chat_id)
            if chat_id in chats_to_remove:
                chats_to_remove.remove(chat_id)
        # If message is /stop, remove chat_id from set
        elif message == "/stop":
            chats_to_remove.add(chat_id)
            if chat_id in chats_to_add:
                chats_to_add.remove(chat_id)
    # Add chats to database
    if len(chats_to_add) > 0:
        cursor.executemany(
            "INSERT OR IGNORE INTO chats (chat_id) VALUES (?)",
            [(chat_id,) for chat_id in chats_to_add],
        )
        logging.info(f"Added {cursor.rowcount} chats")
    # Remove chats from database
    if len(chats_to_remove) > 0:
        cursor.executemany(
            "DELETE FROM chats WHERE chat_id = ?",
            [(chat_id,) for chat_id in chats_to_remove],
        )
        logging.info(f"Removed {cursor.rowcount} chats")
    if len(chats_to_add) > 0 or len(chats_to_remove) > 0:
        conn.commit()


def get_chats(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM chats")
    return [chat_id[0] for chat_id in cursor.fetchall()]


# Send phrases to all users
def send_phrases():
    try:
        conn = sqlite3.connect(os.getenv("SQLITE_DB", "db.sqlite3"))
        save_chats(conn, get_updates()["result"])
        chats = get_chats(conn)
    finally:
        conn.close()

    phrases = generate_phrases()
    for chat_id in chats:
        send_message(
            chat_id, "🇬🇷 <b>Here are your daily phrases from ChatGPT:</b>\n\n" + phrases
        )
    logging.info(f"Phrases sent to {len(chats)} chats")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Schedule script to run once a day at a specific time
    schedule.every().day.at(os.getenv("SCHEDULE_TIME", "12:00")).do(send_phrases)

    logging.info("Bot started")
    while True:
        schedule.run_pending()
        time.sleep(1)
