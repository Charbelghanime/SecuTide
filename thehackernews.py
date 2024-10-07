import requests
from bs4 import BeautifulSoup
import asyncio
import telegram
import os
from test import init_database, send_message_to_telegram_channel, is_article_sent, mark_article_as_sent

# Get bot token and chat ID from environment variables
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')  # Use environment variable for the bot token
bot_chat_id = os.getenv('TELEGRAM_CHAT_ID')  # Use environment variable for the chat ID

bot = telegram.Bot(token=bot_token)

def scrape_latest_article():
    try:
        response = requests.get("https://thehackernews.com/")
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the latest article
        article = soup.find('div', class_='body-post clear')
        if article:
            title = article.find('h2', class_='home-title').text
            link = article.find('a', class_='story-link')['href']
            date = article.find('span', class_='h-datetime').text.strip()  
            
            if date.startswith(""):
                date = date[1:].strip()  # Remove the special character

            return title, link, date
        else:
            print("No article found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

async def main():
    init_database()
    
    article_info = scrape_latest_article()
    if article_info:
        title, link, date = article_info
        
        # Check if the article has already been sent
        if not is_article_sent(link):
            message = f"Title: {title}\nLink: {link}\nDate: {date}"
            # Send the message to the Telegram channel
            await send_message_to_telegram_channel(message)
            # Mark the article as sent
            mark_article_as_sent(link)
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
