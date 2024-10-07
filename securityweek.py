import time
import asyncio
import telegram
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from main import DatabaseManager, TelegramBot 

db_manager = DatabaseManager()
telegram_bot = TelegramBot()

async def send_message_to_telegram_channel(message):
    await telegram_bot.send_message(message)

def scrape_latest_cybersecurity_news():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://www.securityweek.com/"
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        first_article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.zox-art-title a')))
        
        title = first_article_link.text
        link = first_article_link.get_attribute('href')
        
        first_article_link.click()

        time.sleep(2)
        
        try:
            article_date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'time'))).text
        except TimeoutException:
            article_date = "Date not available"
        
        return {
            "Title": title,
            "Link": link,
            "Date": article_date
        }

    except Exception as e:
        print(f"Error scraping the article: {e}")
        return None
    
    finally:
        driver.quit() 
async def main():
    db_manager.create_table() 
    article_info = scrape_latest_cybersecurity_news() 
    
    if article_info:
        message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: SecurityWeek"
        link = article_info['Link']
        
        if not db_manager.is_article_sent(link):  
            await send_message_to_telegram_channel(message)
            db_manager.mark_article_as_sent(link) 
        else:
            print("Article already sent.")

if __name__ == "__main__":
    asyncio.run(main())
