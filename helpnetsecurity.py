import time
import asyncio
import telegram
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from main import create_table, is_article_sent, mark_article_as_sent 

# Telegram bot configuration from environment variables
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')  # Use environment variable for the bot token
bot_chat_id = os.getenv('TELEGRAM_CHAT_ID')  # Use environment variable for the chat ID
bot = telegram.Bot(token=bot_token)

async def send_message_to_telegram_channel(message):
    await bot.send_message(chat_id=bot_chat_id, text=message)

def scrape_first_article():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://www.helpnetsecurity.com/"
    
    try:
        driver.get(url)        
        wait = WebDriverWait(driver, 10)
        
        first_article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card-body a.d-block')))
        title = first_article_link.get_attribute('title')
        link = first_article_link.get_attribute('href')

        article_date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.card-body time')))
        date = article_date.text 
        
        return {
            "Title": title,
            "Link": link,
            "Date": date
        }

    except TimeoutException:
        print("Timeout waiting for page elements.")
        return None

    except Exception as e:
        print(f"Error scraping the article: {e}")
        return None
    
    finally:
        driver.quit()

async def main():
    create_table() 
    article_info = scrape_first_article() 
    
    if article_info:
        message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: HelpNetSecurity"
        link = article_info['Link']
        
        if not is_article_sent(link): 
            await send_message_to_telegram_channel(message) 
            mark_article_as_sent(link)
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
