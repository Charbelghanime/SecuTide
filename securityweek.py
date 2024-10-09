import time
import asyncio
import telegram
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
from main import DatabaseManager, TelegramBot

class ScraperBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.telegram_bot = TelegramBot()

    async def send_message_to_telegram_channel(self, message):
        """Send a message to the Telegram channel."""
        await self.telegram_bot.send_message(message)

    def scrape_latest_cybersecurity_news(self):
        """Scrape the latest cybersecurity news from SecurityWeek."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--no-sandbox")  
        chrome_options.add_argument("--disable-dev-shm-usage")  
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--remote-debugging-port=9222") 
        
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        except WebDriverException as wd_error:
            print(f"WebDriver Error: {wd_error}")
            return None

        url = "https://www.securityweek.com/"
        
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 15) 
            first_article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.zox-art-title a')))
            title = first_article_link.text
            link = first_article_link.get_attribute('href')
            first_article_link.click()
            time.sleep(3) 
            
            try:
                article_date = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'time'))).text
            except TimeoutException:
                article_date = "Date not available"
            
            return {
                "Title": title,
                "Link": link,
                "Date": article_date
            }

        except WebDriverException as wd_error:
            print(f"WebDriver Error: {wd_error}")
            return None
        except Exception as e:
            print(f"Error scraping the article: {e}")
            return None
        finally:
            driver.quit()

    async def process_article(self):
        """Scrape the article, check if it's sent, and send it if not."""
        article_info = self.scrape_latest_cybersecurity_news() 
        
        if article_info:
            message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: SecurityWeek"
            link = article_info['Link']
            
            if not self.db_manager.is_article_sent(link):  
                await self.send_message_to_telegram_channel(message)
                self.db_manager.mark_article_as_sent(link) 
            else:
                print("Article already sent.")

async def main():
    scraper_bot = ScraperBot()
    await scraper_bot.process_article()

if __name__ == "__main__":
    asyncio.run(main())
