# Web Scraper to Markdown - Implementation Plan (Selenium)

## Overview
Modular web scraper that extracts content from URLs (including JS-heavy sites like Facebook) and converts them to clean Markdown files using **Selenium WebDriver** for browser automation.

## Key Changes from Original Plan
- **Browser Automation**: Using Selenium WebDriver instead of Playwright
- **Driver Management**: Using webdriver-manager for automatic ChromeDriver installation
- **Concurrency**: Using ThreadPoolExecutor instead of pure asyncio (Selenium is synchronous)
- **Dependencies**: selenium + webdriver-manager instead of playwright

## Project Structure

```
webpage-md-extractor/
├── config.py           # Target URLs and configuration constants
├── extractor.py        # MarkdownExtractor class with Selenium
├── main.py             # Orchestration with ThreadPoolExecutor
├── output/             # Generated markdown files (auto-created)
├── .gitignore          # Exclude output/, logs
└── CLAUDE.md          # This implementation plan
```

## Dependencies

### Installed Packages
```bash
# Already installed via uv
- selenium==4.40.0          # WebDriver for browser automation
- webdriver-manager==4.0.2  # Automatic ChromeDriver management
- beautifulsoup4==4.14.3    # DOM cleaning
- lxml==6.0.2              # HTML parsing
- markdownify==1.2.2       # HTML to Markdown conversion
- aiofiles==25.1.0         # Async file I/O
```

### Why Selenium?
- Industry standard with massive community support
- Handles JavaScript-heavy sites (Facebook, Meta docs)
- Webdriver-manager handles driver installation automatically
- Compatible with existing Python ecosystem

## Implementation Details

### 1. config.py
**Purpose:** Configuration data (no logic)

```python
from typing import TypedDict

class TargetUrl(TypedDict):
    url: str
    title: str

targets: list[TargetUrl] = [
    {
        "url": "https://www.facebook.com/business/help/890714097648074?id=725943027795860",
        "title": "fb_feed_specs"
    },
    {
        "url": "https://www.facebook.com/business/help/1898524300466211?id=725943027795860",
        "title": "fb_feed_troubleshooting"
    }
]

OUTPUT_DIR: str = "./output"
MAX_RETRIES: int = 3
PAGE_LOAD_TIMEOUT: int = 30  # seconds
MAX_WORKERS: int = 3  # concurrent browser instances
```

### 2. extractor.py (Selenium Implementation)
**Purpose:** Single MarkdownExtractor class with all scraping logic

#### Class Structure
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import aiofiles
import logging
from pathlib import Path
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

    def extract_url(self, url: str, title: str) -> bool:
        """
        Extract URL content and save as markdown
        Returns True on success, False on failure
        """
        pass  # Implementation below

    def _fetch_html(self, url: str) -> str | None:
        """Fetch rendered HTML using Selenium"""
        pass

    def _clean_html(self, html: str) -> str:
        """Clean HTML DOM (remove nav, footer, ads)"""
        pass

    def _convert_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown"""
        pass

    async def _save_markdown(self, title: str, content: str) -> None:
        """Save markdown to file"""
        pass
```

#### Key Implementation Points

**_fetch_html (Selenium WebDriver):**
```python
def _fetch_html(self, url: str) -> str | None:
    """Fetch HTML with Selenium WebDriver"""
    driver = None
    try:
        # Setup Chrome with webdriver-manager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=self.chrome_options)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

        # Navigate and wait for page load
        driver.get(url)

        # Wait for JavaScript to render
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Get fully rendered HTML
        html = driver.page_source
        return html

    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None
    finally:
        if driver:
            driver.quit()  # Always close browser
```

**_clean_html (BeautifulSoup):**
```python
def _clean_html(self, html: str) -> str:
    """Clean unwanted elements from HTML"""
    soup = BeautifulSoup(html, "lxml")

    # Remove navigation, ads, scripts, etc.
    unwanted_selectors = [
        "nav", "footer", "header", "aside",
        "script", "style", "iframe",
        ".ad", ".advertisement", "#ads",
        "[role='navigation']", "[role='banner']"
    ]

    for selector in unwanted_selectors:
        for element in soup.select(selector):
            element.decompose()

    # Extract main content
    main_content = (
        soup.find("main") or
        soup.find("article") or
        soup.find("div", class_="content") or
        soup.find("div", id="content")
    )

    return str(main_content) if main_content else str(soup.body or soup)
```

**_convert_to_markdown (Markdownify):**
```python
def _convert_to_markdown(self, html: str) -> str:
    """Convert cleaned HTML to Markdown"""
    markdown = md(
        html,
        heading_style="ATX",  # Use # for headings
        bullets="-",          # Use - for lists
        strip=["a"],         # Strip link attributes
    )
    return markdown.strip()
```

**_save_markdown (async aiofiles):**
```python
async def _save_markdown(self, title: str, content: str) -> None:
    """Save markdown to output directory"""
    output_path = Path(OUTPUT_DIR) / f"{title}.md"
    async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
        await f.write(content)
    logging.info(f"Saved: {output_path}")
```

**extract_url with Retry Logic:**
```python
def extract_url(self, url: str, title: str) -> bool:
    """
    Main extraction method with retry logic
    Returns True on success, False on failure
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
            import asyncio
            asyncio.run(self._save_markdown(title, markdown))

            logging.info(f"✓ Successfully processed: {title}")
            return True

        except Exception as e:
            logging.error(f"Attempt {attempt + 1}/{MAX_RETRIES} failed for {title}: {e}")
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logging.error(f"✗ All retries exhausted for {title}")
                return False
```

### 3. main.py (ThreadPoolExecutor Concurrency)
**Purpose:** Orchestration with concurrent processing

```python
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from extractor import MarkdownExtractor
from config import targets, OUTPUT_DIR, MAX_WORKERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    """Main entry point"""
    # 1. Setup
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    extractor = MarkdownExtractor()

    # 2. Process URLs concurrently with ThreadPoolExecutor
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(extractor.extract_url, item["url"], item["title"]): item
            for item in targets
        }

        # Collect results as they complete
        for future in as_completed(future_to_url):
            item = future_to_url[future]
            try:
                success = future.result()
                results.append(success)
            except Exception as e:
                logging.error(f"Exception for {item['title']}: {e}")
                results.append(False)

    # 3. Report results
    success_count = sum(1 for r in results if r is True)
    failure_count = len(results) - success_count

    print(f"\n{'='*50}")
    print(f"Processing complete!")
    print(f"Success: {success_count}/{len(results)}")
    print(f"Failed: {failure_count}/{len(results)}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
```

**Why ThreadPoolExecutor?**
- Selenium is synchronous (no native async support)
- ThreadPoolExecutor allows concurrent browser instances
- Simpler than mixing asyncio with synchronous code
- Each thread runs independent Selenium driver

### 4. .gitignore Updates
Add these lines:
```
# Output directory
output/

# Logs
*.log

# Selenium/Chrome cache
.wdm/
```

## Error Handling Strategy

### Layer 1: Network/Selenium Errors
- **Location**: `_fetch_html`
- **Handles**: Timeouts, connection errors, WebDriver exceptions
- **Action**: Log error, return None
- **Propagates to**: Retry logic in `extract_url`

### Layer 2: Parsing Errors
- **Location**: `_clean_html`, `_convert_to_markdown`
- **Handles**: Malformed HTML, encoding issues
- **Action**: Best-effort fallback, log warning
- **Result**: Return partial result rather than fail

### Layer 3: File I/O Errors
- **Location**: `_save_markdown`
- **Handles**: Permission errors, disk full
- **Action**: Raise exception to trigger retry

### Layer 4: Retry Logic
- **Location**: `extract_url` method
- **Strategy**: Exponential backoff (1s, 2s, 4s)
- **Max attempts**: 3 (configurable via MAX_RETRIES)
- **Final failure**: Log error, return False

### Layer 5: Orchestration
- **Location**: `main` function
- **Strategy**: ThreadPoolExecutor with exception handling
- **Result**: Each URL processed independently
- **Reporting**: Success/failure summary

## Verification Steps

### 1. Test Imports
```bash
uv run python -c "from selenium import webdriver; print('Selenium OK')"
uv run python -c "from webdriver_manager.chrome import ChromeDriverManager; print('WebDriver Manager OK')"
```

### 2. Run Scraper
```bash
uv run python main.py
```

### 3. Validate Output
```bash
# Check output files
ls -lh output/

# View content
cat output/fb_feed_specs.md | head -30
cat output/fb_feed_troubleshooting.md | head -30
```

### 4. Validation Checklist
- [ ] `output/` directory contains 2 files
- [ ] Files: `fb_feed_specs.md`, `fb_feed_troubleshooting.md`
- [ ] Markdown formatting correct (headings, lists, links)
- [ ] No navigation/footer content
- [ ] No JavaScript code in output
- [ ] Main content preserved
- [ ] Console shows "Success: 2/2"

### 5. Test Error Handling
Add invalid URL to config.py and verify:
- 3 retry attempts logged
- Script continues to other URLs
- Summary shows 1 failure

### 6. Test Concurrency
Add 5+ URLs to config.py and verify concurrent processing.

## Running the Project

```bash
# Navigate to project
cd /Users/shravan/webpage-md-extractor

# Run the scraper
uv run python main.py

# View output
ls output/
cat output/fb_feed_specs.md
```

## Key Differences: Selenium vs Playwright

| Aspect | Selenium | Playwright |
|--------|----------|------------|
| **Async Support** | No (synchronous) | Yes (native async/await) |
| **Concurrency** | ThreadPoolExecutor | asyncio.gather() |
| **Driver Setup** | webdriver-manager | Built-in browser binaries |
| **API Style** | Traditional OOP | Modern async context |
| **Browser Management** | driver.quit() | async with browser |
| **Maturity** | Very mature (15+ years) | Newer (2020+) |
| **Performance** | Good | Better (less overhead) |

## Expected Output

### Console
```
2026-02-01 14:30:15 - INFO - Saved: output/fb_feed_specs.md
2026-02-01 14:30:15 - INFO - ✓ Successfully processed: fb_feed_specs
2026-02-01 14:30:18 - INFO - Saved: output/fb_feed_troubleshooting.md
2026-02-01 14:30:18 - INFO - ✓ Successfully processed: fb_feed_troubleshooting

==================================================
Processing complete!
Success: 2/2
Failed: 0/2
==================================================
```

### Files
```
output/
├── fb_feed_specs.md           # ~50-200 KB
└── fb_feed_troubleshooting.md # ~50-200 KB
```

## Design Principles

✓ **KISS (Keep It Simple)**
- Linear flow: Load → Fetch → Parse → Save
- 3 simple files: config, extractor, main
- No over-abstraction

✓ **DRY (Don't Repeat Yourself)**
- Single MarkdownExtractor class
- No duplicate scraping logic
- Reusable for any URL list

✓ **Modern Python**
- Type hints everywhere (TypedDict, | None syntax)
- ThreadPoolExecutor for concurrency
- Context managers where applicable (async with for files)

✓ **Error Resilience**
- Retry with exponential backoff
- Graceful failure (continue on error)
- Independent URL processing

## Next Steps

1. ✅ Dependencies installed (selenium, webdriver-manager, etc.)
2. ⏳ Create config.py
3. ⏳ Create extractor.py with Selenium
4. ⏳ Update main.py with ThreadPoolExecutor
5. ⏳ Update .gitignore
6. ⏳ Run and verify output

## Critical Files to Implement

1. **[config.py](config.py)** - Target URLs and configuration
2. **[extractor.py](extractor.py)** - MarkdownExtractor with Selenium WebDriver
3. **[main.py](main.py)** - ThreadPoolExecutor orchestration
4. **[.gitignore](.gitignore)** - Exclude output/, logs, .wdm/
