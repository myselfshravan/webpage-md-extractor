Role: You are a Senior Python Backend Engineer. Task: Implement a robust web-scraper-to-markdown module within an existing uv project. Project Name: webpage-md-extractor Context: I have initialized a project using uv. I need a script that takes a dictionary of URLs and Titles, extracts the main content from those pages, converts it to clean Markdown, and saves the files locally.

Functional Requirements:

Input: A strict data structure (List of Dictionaries) containing url and title.

Example: [{ "url": "https://...", "title": "catalog_schema" }]

Processing:

Fetch the HTML content (must handle dynamic JS-heavy sites like Facebook/Meta docs).

Clean the DOM (remove navbars, footers, ads).

Convert the relevant HTML body to Markdown.

Output:

Create an output/ directory if it doesn't exist.

Save files as ./output/{title}.md.

Engineering Standards (Strict Adherence):

KISS: Use a simple, linear flow: Load Config -> Fetch -> Parse -> Save. No over-abstraction.

DRY: Create a single Extractor class or module. Do not duplicate scraping logic.

Modern Python: Use asyncio to process multiple URLs concurrently. Use Type Hints (typing) for everything.

Dependencies: Use uv add compatible libraries. Prefer Playwright (for rendering JS) + Markdownify (for conversion) over older Selenium scripts.

Error Handling: If a URL fails, log the error and continue to the next (do not crash). Implement a simple retry mechanism (max 3 retries).

Deliverables:

The uv add commands to install necessary dependencies.

A single Python file main.py (or extractor.py) containing the logic.

A config.py or separate section defining the dictionary of URLs.

Instructions on how to run it.

Input Data (for testing): Use this dictionary for the initial run:

Python
targets = [
    {"url": "https://www.facebook.com/business/help/890714097648074?id=725943027795860", "title": "fb_feed_specs"},
    {"url": "https://www.facebook.com/business/help/1898524300466211?id=725943027795860", "title": "fb_feed_troubleshooting"}
]