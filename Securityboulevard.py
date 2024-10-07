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

    def scrape_security_boulevard_article(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        url = "https://securityboulevard.com/security-creators-network/"

        try:
            driver.get(url)

            wait = WebDriverWait(driver, 15)
            first_article_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.pt-cv-title a.panel-title')))
            
            title = first_article_link.text.split("\n")[0]
            link = first_article_link.get_attribute('href')

            article_date_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.entry-date time')))
            date = article_date_element.get_attribute('datetime')

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
            driver.quit()  # Ensure the browser is closed

    async def process_article(self):
        article_info = self.scrape_security_boulevard_article()
        if article_info:
            message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: Security Boulevard"
            link = article_info['Link']

            if not self.db_manager.is_article_sent(link):
                await self.telegram_bot.send_message(message)
                self.db_manager.mark_article_as_sent(link)
            else:
                print("Article already sent.")

async def main():
    scraper_bot = ScraperBot()
    await scraper_bot.process_article()

if __name__ == "__main__":
    asyncio.run(main())
