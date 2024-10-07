import requests
from bs4 import BeautifulSoup
import telegram
from datetime import datetime
import asyncio
import os
from main import create_table, is_article_sent, mark_article_as_sent

# Telegram bot configuration from environment variables
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')  # Use environment variable for the bot token
bot_chat_id = os.getenv('TELEGRAM_CHAT_ID')  # Use environment variable for the chat ID

bot = telegram.Bot(token=bot_token)

async def send_message_to_telegram_channel(message):
    await bot.send_message(chat_id=bot_chat_id, text=message)

async def scrape_latest_article():
    url = 'https://cybersecuritynews.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the webpage: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    news_section = soup.find('div', id='tdi_20')

    if news_section is None:
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
        return message

    else:
        print("Could not find the latest article.")
        return None

async def main():
    create_table()  # Ensure the database is ready
    
    latest_article_message = await scrape_latest_article()
    if latest_article_message:
        link = latest_article_message.split('\n')[1].split(': ')[1]
        
        if not is_article_sent(link):  # Check if the article has already been sent
            await send_message_to_telegram_channel(latest_article_message)  # Send message to Telegram
            mark_article_as_sent(link)  # Mark the article as sent in the database
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
