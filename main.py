import sqlite3
import telegram
import asyncio
import os  

# Telegram bot credentials 
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')  # Token set as an environment variable
bot_chat_id = os.getenv('TELEGRAM_CHAT_ID')  # Chat ID set as an environment variable

bot = telegram.Bot(token=bot_token)

def create_connection():
    conn = sqlite3.connect('sent_articles.db')
    return conn

def create_table():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sent_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link TEXT UNIQUE NOT NULL
            )
        ''')
    conn.close()

# Check if the article has already been sent
def is_article_sent(link):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM sent_articles WHERE link = ?', (link,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Mark an article as sent
def mark_article_as_sent(link):
    conn = create_connection()
    with conn:
        conn.execute('INSERT INTO sent_articles (link) VALUES (?)', (link,))
    conn.close()

async def send_message_to_telegram_channel(message):
    await bot.send_message(chat_id=bot_chat_id, text=message)

def init_database():
    create_table()
