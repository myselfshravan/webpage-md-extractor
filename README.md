# Web Scraper to Markdown

A modular Python web scraper that extracts content from URLs (including JavaScript-heavy sites) and converts them to clean Markdown files using Selenium WebDriver.

## Features

- **Selenium WebDriver** - Handles JavaScript-heavy sites like Facebook, Meta docs
- **Automatic Driver Management** - webdriver-manager installs ChromeDriver automatically
- **Concurrent Processing** - ThreadPoolExecutor for parallel URL processing
- **Retry Logic** - 3 attempts with exponential backoff (1s, 2s, 4s)
- **Error Resilience** - Continues processing even if URLs fail
- **Clean Extraction** - Removes navigation, footers, ads, scripts
- **Quality Markdown** - Proper formatting with headings, lists, links

## Installation

Dependencies are already installed. If you need to reinstall:

```bash
uv add selenium webdriver-manager beautifulsoup4 lxml markdownify aiofiles
```

## Quick Start

### 1. Configure URLs

Edit [config.py](config.py) to add your target URLs:

```python
targets: list[TargetUrl] = [
    {
        "url": "https://example.com/page1",
        "title": "my_page"
    },
    {
        "url": "https://example.com/page2",
        "title": "another_page"
    }
]
```

### 2. Run the Scraper

```bash
uv run python main.py
```

### 3. View Output

```bash
# List generated files
ls output/

# View content
cat output/my_page.md
```

## Configuration Options

Edit [config.py](config.py) to customize:

```python
OUTPUT_DIR: str = "./output"        # Output directory
MAX_RETRIES: int = 3                # Retry attempts per URL
PAGE_LOAD_TIMEOUT: int = 30         # Page load timeout (seconds)
MAX_WORKERS: int = 3                # Concurrent browser instances
```

## Output

Generated markdown files are saved to `./output/{title}.md` with:
- Clean formatting (ATX headings, bullet lists)
- No navigation/footer content
- No ads or scripts
- Preserved main content and links

## Example

**Input:**
```python
targets = [
    {
        "url": "https://www.facebook.com/business/help/890714097648074",
        "title": "fb_feed_specs"
    }
]
```

**Run:**
```bash
uv run python main.py
```

**Output:**
```
output/
└── fb_feed_specs.md
```

## Troubleshooting

**ChromeDriver Issues:**
- ChromeDriver is downloaded automatically by webdriver-manager
- Cached in `~/.wdm/drivers/`
- Delete cache if issues occur: `rm -rf ~/.wdm/`

**Facebook Rate Limiting:**
- Some URLs may fail due to rate limiting
- The retry mechanism will attempt 3 times
- Script continues processing other URLs

## Project Structure

```
webpage-md-extractor/
├── config.py          # Configuration and target URLs
├── extractor.py       # MarkdownExtractor class (Selenium)
├── main.py            # Entry point with ThreadPoolExecutor
├── output/            # Generated markdown files
├── CLAUDE.md          # Detailed implementation plan
└── README.md          # This file
```

## Documentation

See [CLAUDE.md](CLAUDE.md) for complete implementation details including:
- Architecture decisions
- Error handling strategy
- Implementation approach
- Selenium vs Playwright comparison