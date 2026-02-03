"""Web scraper that extracts content and converts to Markdown using Selenium"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Optional

import aiofiles
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import OUTPUT_DIR, MAX_RETRIES, PAGE_LOAD_TIMEOUT


class MarkdownExtractor:
    """Web scraper that extracts content and converts to Markdown using Selenium"""

    def __init__(self):
        """Initialize Chrome options for headless mode"""
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    def extract_url(self, url: str, title: str) -> bool:
        """
        Extract URL content and save as markdown with retry logic

        Args:
            url: The URL to scrape
            title: The filename (without extension) for the output

        Returns:
            True on success, False on failure
        """
        for attempt in range(MAX_RETRIES):
            try:
                # 1. Fetch HTML with Selenium
                html = self._fetch_html(url)
                if not html:
                    raise ValueError("Failed to fetch HTML")

                # 2. Clean HTML
                cleaned = self._clean_html(html)

                # 3. Convert to Markdown
                markdown = self._convert_to_markdown(cleaned)

                # 4. Save to file (run async in event loop)
                asyncio.run(self._save_markdown(title, markdown))

                logging.info(f"✓ Successfully processed: {title}")
                return True

            except Exception as e:
                logging.error(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {title}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                else:
                    logging.error(f"✗ All retries exhausted for {title}")
                    return False

    def _fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch rendered HTML using Selenium WebDriver

        Args:
            url: The URL to fetch

        Returns:
            Rendered HTML string or None on failure
        """
        driver = None
        try:
            # Setup Chrome with webdriver-manager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

            # Navigate to URL
            logging.info(f"Fetching: {url}")
            driver.get(url)

            # Wait for JavaScript to render (document.readyState === 'complete')
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Additional wait for dynamic content
            time.sleep(2)

            # Get fully rendered HTML
            html = driver.page_source
            logging.debug(f"Fetched {len(html)} bytes from {url}")
            return html

        except Exception as e:
            logging.error(f"Failed to fetch {url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()  # Always close browser

    def _clean_html(self, html: str) -> str:
        """
        Clean unwanted elements from HTML

        Args:
            html: Raw HTML string

        Returns:
            Cleaned HTML string
        """
        soup = BeautifulSoup(html, "lxml")

        # Remove unwanted elements (navigation, ads, scripts, etc.)
        unwanted_selectors = [
            "nav", "footer", "header", "aside",
            "script", "style", "iframe", "noscript",
            ".ad", ".advertisement", "#ads",
            "[role='navigation']", "[role='banner']",
            "[role='complementary']", "[aria-label='Advertisement']"
        ]

        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()

        # Extract main content area
        main_content = (
            soup.find("main") or
            soup.find("article") or
            soup.find("div", class_="content") or
            soup.find("div", id="content") or
            soup.find("div", role="main")
        )

        # Fallback to body if no main content area found
        result = str(main_content) if main_content else str(soup.body or soup)
        logging.debug(f"Cleaned HTML: {len(result)} bytes")
        return result

    def _convert_to_markdown(self, html: str) -> str:
        """
        Convert cleaned HTML to Markdown

        Args:
            html: Cleaned HTML string

        Returns:
            Markdown string
        """
        markdown = md(
            html,
            heading_style="ATX",  # Use # for headings
            bullets="-",          # Use - for list items
            strip=["a"],         # Strip link attributes for cleaner output
        )

        # Clean up excessive whitespace
        lines = [line.rstrip() for line in markdown.split('\n')]
        cleaned = '\n'.join(lines).strip()

        logging.debug(f"Converted to markdown: {len(cleaned)} chars")
        return cleaned

    async def _save_markdown(self, title: str, content: str) -> None:
        """
        Save markdown content to file

        Args:
            title: Filename (without extension)
            content: Markdown content to save
        """
        output_path = Path(OUTPUT_DIR) / f"{title}.md"
        async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
            await f.write(content)
        logging.info(f"Saved: {output_path}")
