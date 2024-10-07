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

    def scrape_cybernews_article(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set up the Chrome driver using WebDriverManager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        url = "https://cybernews.com/"

        try:
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            first_article = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cells__item a.link.heading')))

            driver.execute_script("arguments[0].scrollIntoView();", first_article)

            first_article.click()

            time.sleep(2)
            title = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'h1'))).text
            date = driver.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
            article_link = driver.current_url

            return {
                "Title": title,
                "Date": date,
                "Link": article_link
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
        article_info = self.scrape_cybernews_article()
        if article_info:
            message = f"Title: {article_info['Title']}\nLink: {article_info['Link']}\nDate: {article_info['Date']}\nSource: Cybernews"
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
