import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.endpoints import router
from app.core.config import settings
from app.core.database import check_db_connection
from app.services.ml_service import validate_models

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate ML models at startup so misconfiguration fails fast."""
    logger.info(
        "Starting %s v%s (env=%s)", settings.PROJECT_NAME, settings.VERSION, settings.APP_ENV
    )
    try:
        validate_models()
        logger.info("ML models loaded and validated successfully.")
    except Exception as exc:
        logger.critical("STARTUP FAILED — could not load ML models: %s", exc)
        raise
    yield
    logger.info("Shutting down %s.", settings.PROJECT_NAME)


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "AI-powered bus stop suitability analysis, location optimization, "
        "and infrastructure recommendation API."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Router ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")
# Also mount without prefix for backward compatibility with existing frontend
app.include_router(router)



# ── Health endpoint ───────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Returns the operational status of the API, including DB and ML model
    availability. Returns HTTP 200 when fully healthy, HTTP 503 otherwise.
    """
    db_ok = check_db_connection()
    try:
        validate_models()
        models_ok = True
    except Exception:
        models_ok = False

    status = "healthy" if (db_ok and models_ok) else "degraded"
    payload = {
        "status": status,
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "components": {
            "database": "ok" if db_ok else "unavailable",
            "ml_models": "ok" if models_ok else "unavailable",
        },
    }

    if status == "degraded":
        return JSONResponse(status_code=503, content=payload)
    return payload
