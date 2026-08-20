"""
Database initialisation script.

Creates all tables and populates the bus_stops table from the cleaned CSV.
Includes retry logic so it can be run as a Docker one-shot service that
waits for PostgreSQL to become available before proceeding.

Usage:
    python backend/scripts/init_db.py
"""
import logging
import os
import sys
import time

import pandas as pd

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.models.domain import BusStop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)

_CSV_PATH = os.path.join(
    settings.DATA_DIR, "bus_stop_optimization_dataset_15000_cleaned.csv"
)
_BATCH_SIZE = 1_000
_MAX_RETRIES = 10
_RETRY_DELAY_S = 3


def wait_for_db() -> None:
    """Retry the DB connection until it succeeds or max retries are exceeded."""
    from sqlalchemy import text
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection established.")
            return
        except Exception as exc:
            logger.warning(
                "DB not ready (attempt %d/%d): %s — retrying in %ds…",
                attempt, _MAX_RETRIES, exc, _RETRY_DELAY_S,
            )
            time.sleep(_RETRY_DELAY_S)

    logger.critical("Could not connect to the database after %d attempts. Aborting.", _MAX_RETRIES)
    sys.exit(1)


def init_db() -> None:
    """Create tables and seed the bus_stops table from CSV if empty."""
    wait_for_db()

    logger.info("Creating database tables…")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(BusStop).first():
            logger.info("Database already populated — skipping seed.")
            return

        if not os.path.exists(_CSV_PATH):
            logger.error("CSV not found at '%s' — skipping data import.", _CSV_PATH)
            return

        logger.info("Loading CSV from %s", _CSV_PATH)
        df = pd.read_csv(_CSV_PATH)
        records = df.to_dict("records")
        total = len(records)
        logger.info("Inserting %d records in batches of %d…", total, _BATCH_SIZE)

        for i in range(0, total, _BATCH_SIZE):
            batch = records[i : i + _BATCH_SIZE]
            db.bulk_insert_mappings(BusStop, batch)
            db.commit()
            logger.info("Inserted %d / %d records.", min(i + _BATCH_SIZE, total), total)

        logger.info("Database initialisation complete.")
    except Exception as exc:
        db.rollback()
        logger.exception("Error during database initialisation: %s", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
