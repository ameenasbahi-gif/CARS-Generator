# MCAT CARS Passage Generator

## Project Overview

A website that generates authentic MCAT CARS (Critical Analysis and Reasoning Skills) passages by scraping real MCAT sample materials from verified internet sources.

## Goals

- Scrape authentic MCAT CARS passages from publicly available sources (official AAMC samples, prep company free previews, etc.)
- Present passages in a clean, exam-like interface
- Help students practice with real MCAT-style reading comprehension content

## Tech Stack

- **Frontend**: To be determined (likely React or plain HTML/CSS/JS)
- **Backend**: Python (FastAPI or Flask) for scraping and serving passages
- **Scraping**: Python with BeautifulSoup / Playwright for dynamic pages
- **Storage**: SQLite or PostgreSQL to cache scraped passages

## Key Features

1. **Passage Scraper** — Pulls CARS passages from authentic MCAT sources on the internet
2. **Passage Display** — Renders passages in a timed, exam-like reading interface
3. **Source Attribution** — Tracks and displays the origin of each passage
4. **Passage Variety** — Ensures diversity across humanities, social sciences, and natural sciences topics

## Source Targets

- AAMC official free sample materials
- Khan Academy MCAT passages (publicly accessible)
- Other verified MCAT prep sites with freely available sample passages

## Development Notes

- Respect `robots.txt` and rate-limit all scrapers
- Cache scraped content to avoid redundant requests
- Store passage metadata (source URL, date scraped, topic category)
- Passages should be de-duplicated before storage

## User Environment

**The user works exclusively on an iPad.**
- No local terminal, no local Python/Node server
- All backend services must be deployed to the cloud (not localhost)
- Frontend must be hosted (GitHub Pages, Netlify, etc.) — not opened as a local file
- Recommended deployment: **Railway** (backend) + **GitHub Pages** (frontend)
- For development/editing: user uses Claude Code via browser

## Branch

Active development branch: `claude/mcat-passage-generator-WgU62`
