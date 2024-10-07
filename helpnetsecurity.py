import time
import asyncio
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from main import DatabaseManager, TelegramBot  

class ScraperBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.telegram_bot = TelegramBot()

    async def send_message_to_telegram_channel(self, message):
        """Send a message to the Telegram channel."""
        await self.telegram_bot.send_message(message)

    def scrape_first_article(self):
        """Scrape the first article from HelpNetSecurity."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

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

    async def process_article(self):
        """Scrape the article, check if it's sent, and send it if not."""
        article_info = self.scrape_first_article()
        
        if article_info:
            message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: HelpNetSecurity"
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
