import requests
from bs4 import BeautifulSoup
import asyncio
import os
from datetime import datetime
from main import DatabaseManager, TelegramBot 

class ScraperBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.telegram_bot = TelegramBot()

    async def send_message_to_telegram_channel(self, message):
        """Send a message to the Telegram channel."""
        await self.telegram_bot.send_message(message)

    def scrape_latest_article(self):
        """Scrapes the latest article from Cybersecurity News."""
        url = 'https://cybersecuritynews.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch the webpage: {e}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        news_section = soup.find('div', id='tdi_20')

        if not news_section:
            print("Could not find the 'Latest Cyber Security News' section.")
            return None

        latest_article = news_section.find('div', class_='td_module_10')

        if latest_article:
            title_tag = latest_article.find('a', class_='td-image-wrap')
            date_tag = latest_article.find('time')

            title = title_tag.get('title').strip() if title_tag else 'No title found'
            link = title_tag.get('href').strip() if title_tag else 'No link found'
            date_str = date_tag.get('datetime').strip() if date_tag and date_tag.has_attr('datetime') else 'No date found'

            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')
            except ValueError:
                date = 'Invalid date format'

            message = f"Title: {title}\nLink: {link}\nDate: {date}\nSource: CybersecurityNews"
            return {"message": message, "link": link}

        print("Could not find the latest article.")
        return None

    async def process_article(self):
        """Scrapes, checks, and sends the latest article."""
        article_info = self.scrape_latest_article()
        if article_info:
            link = article_info['link']
            if not self.db_manager.is_article_sent(link):
                await self.send_message_to_telegram_channel(article_info['message'])
                self.db_manager.mark_article_as_sent(link)
            else:
                print("Article already sent.")

async def main():
    scraper_bot = ScraperBot()
    await scraper_bot.process_article()

if __name__ == "__main__":
    asyncio.run(main())
