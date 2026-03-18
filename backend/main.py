"""
MCAT CARS Practice — FastAPI Backend
--------------------------------------
Endpoints:
  GET  /passages              List all passages (filter by category)
  GET  /passages/random       Get a random passage (with full questions)
  GET  /passages/{id}         Get a specific passage by ID
  GET  /passages/count        Count passages by category
  POST /scrape                Trigger a background scrape from all sources
  GET  /scrape/status         Check scrape status
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, get_passages, get_passage_by_id, get_random_passage, count_passages
from scrapers.jack_westin import JackWestinScraper
from scrapers.khan_academy import KhanAcademyScraper

logging.basicConfig(level=logging.INFO, format="%(name)s | %(levelname)s | %(message)s")
log = logging.getLogger("main")

# Track scrape state
scrape_state = {"running": False, "last_result": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup: init DB, auto-scrape if empty."""
    init_db()
    counts = count_passages()
    if counts["total"] == 0:
        log.info("Database empty — triggering initial scrape in background")
        asyncio.create_task(run_all_scrapers())
    else:
        log.info(f"Database has {counts['total']} passages — skipping scrape")
    yield


app = FastAPI(
    title="MCAT CARS API",
    description="Passage bank scraped from Jack Westin and Khan Academy",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten for production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/passages")
def list_passages(
    category: str = Query("all", description="all | humanities | social | natural"),
    limit: int = Query(50, ge=1, le=200),
):
    """List all passages (summaries only, no question text)."""
    rows = get_passages(category, limit)
    category_label_map = {
        "humanities": "Humanities",
        "social": "Social Sciences",
        "natural": "Natural Sciences",
    }
    for r in rows:
        r["category_label"] = category_label_map.get(r["category"], r["category"].title())
    return {"passages": rows, "total": len(rows)}


@app.get("/passages/random")
def random_passage(
    category: str = Query("all", description="all | humanities | social | natural"),
):
    """Return a full random passage with questions."""
    p = get_random_passage(category)
    if not p:
        raise HTTPException(
            status_code=404,
            detail=f"No passages found for category '{category}'. Try POST /scrape first."
        )
    return _format_passage(p)


@app.get("/passages/count")
def passage_count():
    """Return passage counts by category."""
    return count_passages()


@app.get("/passages/{passage_id}")
def single_passage(passage_id: int):
    """Return a single passage with all questions."""
    p = get_passage_by_id(passage_id)
    if not p:
        raise HTTPException(status_code=404, detail="Passage not found")
    return _format_passage(p)


@app.post("/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks):
    """Manually trigger a scrape from all sources."""
    if scrape_state["running"]:
        return {"message": "Scrape already in progress"}
    background_tasks.add_task(run_all_scrapers)
    return {"message": "Scrape started. Check GET /scrape/status for progress."}


@app.get("/scrape/status")
def scrape_status():
    """Check whether a scrape is in progress."""
    counts = count_passages()
    return {
        "running": scrape_state["running"],
        "last_result": scrape_state["last_result"],
        "passages_in_db": counts,
    }


# ── Helpers ──────────────────────────────────────────────────────────────────

def _format_passage(p: dict) -> dict:
    """Add category_label to a passage dict."""
    label_map = {
        "humanities": "Humanities",
        "social":     "Social Sciences",
        "natural":    "Natural Sciences",
    }
    p["category_label"] = label_map.get(p["category"], p["category"].title())
    return p


async def run_all_scrapers():
    """Run Jack Westin and Khan Academy scrapers concurrently."""
    scrape_state["running"] = True
    log.info("Starting scrapers: Jack Westin + Khan Academy")
    try:
        jw = JackWestinScraper()
        ka = KhanAcademyScraper()
        jw_count, ka_count = await asyncio.gather(
            jw.scrape(),
            ka.scrape(),
            return_exceptions=True,
        )
        scrape_state["last_result"] = {
            "jack_westin": jw_count if isinstance(jw_count, int) else str(jw_count),
            "khan_academy": ka_count if isinstance(ka_count, int) else str(ka_count),
        }
        log.info(f"Scrape finished: JW={jw_count} KA={ka_count}")
    except Exception as e:
        log.error(f"Scraper error: {e}")
        scrape_state["last_result"] = {"error": str(e)}
    finally:
        scrape_state["running"] = False
