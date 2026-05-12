"""PhishGuard — FastAPI Application Factory.

Central app with lifespan, CORS, and logging.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import structlog

from app.core.config import settings
from app.api.v1 import scan, reports, feedback, health
from app.services.ml_inference import load_model
from app.core.limiter import close_redis

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # ─── Startup ───
    logger.info("phishguard_starting", host=settings.backend_host, port=settings.backend_port)

    # Load ML model (optional — falls back to heuristic)
    load_model()

    logger.info("phishguard_started")
    yield

    # ─── Shutdown ───
    await close_redis()
    logger.info("phishguard_stopped")


app = FastAPI(
    title="PhishGuard API",
    description="AI-Powered Phishing Detection & Real-Time Browser Protection",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request Logging Middleware ───
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = int((time.time() - start) * 1000)

    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=latency,
    )

    return response


# ─── Exception Handler ───
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ─── Register Routers ───
app.include_router(scan.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(health.router)
