import requests
from bs4 import BeautifulSoup
import asyncio
import os
from main import DatabaseManager, TelegramBot 

db_manager = DatabaseManager()
telegram_bot = TelegramBot()

def scrape_latest_article():
    try:
        response = requests.get("https://thehackernews.com/")
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')

        article = soup.find('div', class_='body-post clear')
        if article:
            title = article.find('h2', class_='home-title').text
            link = article.find('a', class_='story-link')['href']
            date = article.find('span', class_='h-datetime').text.strip()  
            
            if date.startswith(""):
                date = date[1:].strip() 
            return title, link, date
        else:
            print("No article found.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

async def main():
    db_manager.create_table() 
    
    article_info = scrape_latest_article()
    if article_info:
        title, link, date = article_info
        
        if not db_manager.is_article_sent(link):
            message = f"Title: {title}\nLink: {link}\nDate: {date}"
            await telegram_bot.send_message(message)
            db_manager.mark_article_as_sent(link)
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
