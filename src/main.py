import requests
import openai
import schedule
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv() # take environment variables from .env.
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

def get_updates():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url)
    return response.json()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response.json()

def generate_phrases():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "Generate 5 Greek phrases for B1 level with translation. One phrase - one line"
        }]
    )
    return response.choices[0].message.content

# Send phrases to all users
def send_phrases():
    phrases = generate_phrases()
    chats = set([update["message"]["chat"]["id"] for update in get_updates()["result"]])
    for chat_id in chats:
        send_message(
            chat_id, 
            "🇬🇷 <b>Here are your daily phrases from ChatGPT:</b>\n\n" + phrases
        )
    logging.info(f"Phrases sent to {len(chats)} chats")

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    # Schedule script to run once a day at a specific time
    schedule.every().day.at(os.getenv("SCHEDULE_TIME", "12:00")).do(send_phrases)

    logging.info("Bot started")
    while True:
        schedule.run_pending()
        time.sleep(1)
