"""Configuration for web scraper to markdown converter"""

from typing import TypedDict


class TargetUrl(TypedDict):
    """Type definition for target URL dictionary"""
    url: str
    title: str


# Target URLs to scrape
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

# Configuration constants
OUTPUT_DIR: str = "./output"
MAX_RETRIES: int = 3
PAGE_LOAD_TIMEOUT: int = 30  # seconds
MAX_WORKERS: int = 3  # concurrent browser instances
