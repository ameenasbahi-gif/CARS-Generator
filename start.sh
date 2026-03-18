#!/bin/bash
# MCAT CARS Practice — Start Script
# Run this once to install deps, then launches the backend.
# Frontend: just open index.html in your browser.

set -e
cd "$(dirname "$0")/backend"

echo "==> Installing Python dependencies..."
pip3 install -r requirements.txt

echo "==> Installing Playwright Chromium (needed for Jack Westin scraping)..."
python3 -m playwright install chromium

echo "==> Starting FastAPI server on http://localhost:8000"
echo "    Open index.html in your browser to use the app."
echo "    On first run, passages will be scraped automatically."
echo "    Check scrape progress: http://localhost:8000/scrape/status"
echo ""
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
