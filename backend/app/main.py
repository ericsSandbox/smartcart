from fastapi import FastAPI
import time
import logging
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware

# import routers
from app.routers import health, household, lists, pantry, members, recipes, pricing, circulars, gateway
from app.services.circular_loader import init_circular_loader

logger = logging.getLogger(__name__)

app = FastAPI(title="SmartCart API (dev)")

# CORS - must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://ericsSandbox.github.io",
        "https://ericsSandbox.github.io/smartcart",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Wait for the database to be ready, then create tables (development convenience).

    This avoids import-time attempts to connect to Postgres before the container
    has finished initializing (common with docker-compose)."""
    max_tries = 30
    for i in range(max_tries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database reachable")
            # create DB tables after DB is reachable
            Base.metadata.create_all(bind=engine)
            
            # Load circular items on startup
            logger.info("Loading circular items from PDFs...")
            db = next(get_db())
            try:
                results = init_circular_loader(db)
                if results["loaded"]:
                    logger.info(f"✓ Circular loader: {results['total_items']} items loaded")
                if results["failed"]:
                    logger.warning(f"⚠ Circular loader: {len(results['failed'])} retailers failed")
            except Exception as e:
                logger.warning(f"Circular loader failed (not critical): {e}")
            finally:
                db.close()
            
            return
        except OperationalError as e:
            # Could be connection refused or DNS resolution issue; retry
            logger.info(f"DB not ready (attempt {i+1}/{max_tries}): {e}")
            time.sleep(1)
        except Exception as e:
            # Catch-all to avoid crashing the entire app on startup in dev
            logger.warning(f"Unexpected error while waiting for DB: {e}")
            time.sleep(1)

    # If we get here the DB never became reachable. Log and continue without
    # creating tables. In production you may want to fail fast instead.
    logger.error("Database did not become reachable after retries; starting without DB initialization.")
    # do not raise; app will start but DB-related endpoints will fail until DB is available
    return


app.include_router(health.router)
app.include_router(gateway.router)
app.include_router(household.router)
app.include_router(lists.router)
app.include_router(pantry.router)
app.include_router(members.router)
app.include_router(recipes.router)
app.include_router(pricing.router)
app.include_router(circulars.router)


@app.get("/")
async def root():
    return {"message": "SmartCart backend running"}
