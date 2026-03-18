"""
Standalone scrape runner — called by GitHub Actions daily.
Scrapes Jack Westin + Khan Academy and saves to Supabase.
"""

import asyncio
import logging
from database import init_db, count_passages
from scrapers.jack_westin import JackWestinScraper
from scrapers.khan_academy import KhanAcademyScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("scrape_runner")


async def main():
    log.info("Initialising database...")
    init_db()

    before = count_passages()
    log.info(f"Passages before scrape: {before['total']}")

    log.info("Starting Jack Westin scraper...")
    jw = JackWestinScraper()
    jw_count = await jw.scrape()

    log.info("Starting Khan Academy scraper...")
    ka = KhanAcademyScraper()
    ka_count = await ka.scrape()

    after = count_passages()
    log.info(f"Scrape complete. Jack Westin: +{jw_count}  Khan Academy: +{ka_count}")
    log.info(f"Total passages now: {after['total']}")
    log.info(f"By category: {after['by_category']}")


if __name__ == "__main__":
    asyncio.run(main())
