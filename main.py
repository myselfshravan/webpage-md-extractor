"""Main entry point for web scraper to markdown converter"""

import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from extractor import MarkdownExtractor
from config import targets, OUTPUT_DIR, MAX_WORKERS


def main():
    """Main entry point - orchestrates concurrent URL processing"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Create output directory
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    logging.info(f"Output directory: {OUTPUT_DIR}")

    # Initialize extractor
    extractor = MarkdownExtractor()

    # Process URLs concurrently with ThreadPoolExecutor
    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_url = {
            executor.submit(extractor.extract_url, item["url"], item["title"]): item
            for item in targets
        }

        logging.info(f"Processing {len(targets)} URLs with {MAX_WORKERS} workers...")

        # Collect results as they complete
        for future in as_completed(future_to_url):
            item = future_to_url[future]
            try:
                success = future.result()
                results.append(success)
            except Exception as e:
                logging.error(f"Exception for {item['title']}: {e}")
                results.append(False)

    # Report results
    success_count = sum(1 for r in results if r is True)
    failure_count = len(results) - success_count

    print(f"\n{'='*50}")
    print(f"Processing complete!")
    print(f"Success: {success_count}/{len(results)}")
    print(f"Failed: {failure_count}/{len(results)}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
