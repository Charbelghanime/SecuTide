import sqlite3
import telegram
import os

class DatabaseManager:
    def __init__(self, db_name='sent_articles.db'):
        self.db_path = os.path.join(os.getcwd(), db_name)
        self.create_table()

    def create_connection(self):
        """Create a connection to the SQLite database."""
        return sqlite3.connect(self.db_path)

    def create_table(self):
        """Create the `sent_articles` table if it does not exist."""
        conn = self.create_connection()
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sent_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT UNIQUE NOT NULL
                )
            ''')
        conn.close()

    def is_article_sent(self, link):
        """Check if the article has already been sent."""
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM sent_articles WHERE link = ?', (link,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def mark_article_as_sent(self, link):
        """Mark an article as sent in the database."""
        conn = self.create_connection()
        with conn:
            conn.execute('INSERT INTO sent_articles (link) VALUES (?)', (link,))
        conn.close()


class TelegramBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.bot_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = telegram.Bot(token=self.bot_token)

    async def send_message(self, message):
        """Send a message to the Telegram channel."""
        await self.bot.send_message(chat_id=self.bot_chat_id, text=message)
