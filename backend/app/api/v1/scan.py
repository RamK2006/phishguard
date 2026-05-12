"""PhishGuard — Scan API Endpoints.

POST /scan/url, POST /scan/email, POST /scan/batch, GET /scan/batch/{job_id}
"""

import hashlib
import time
import uuid
import asyncio
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.limiter import check_rate_limit
from app.services.ml_inference import predict_url_risk, get_risk_level
from app.services.threat_intel import query_threat_intel
from app.services.llm_explainer import generate_explanation
from app.services.visual_similarity import check_visual_similarity
from app.services.cache import cache_get, cache_set, add_to_bloom_filter
from app.db.session import store_scan_event

import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/scan", tags=["scan"])


# ─── Request/Response Models ───

class URLScanRequest(BaseModel):
    url: str = Field(..., min_length=5, max_length=4096)
    source: str = Field(default="api")


class EmailScanRequest(BaseModel):
    sender: str = Field(default="")
    subject: str = Field(default="")
    links: List[str] = Field(default_factory=list)
    headers: Optional[dict] = None


class BatchScanRequest(BaseModel):
    urls: List[str] = Field(..., min_length=1, max_length=100)


class ScanResponse(BaseModel):
    scan_id: str
    url: str
    risk_score: float
    risk_level: str
    ml_score: float
    cti_score: float
    visual_score: float
    final_score: float
    explanation: dict
    features: dict
    cache_hit: bool
    latency_ms: int
    timestamp: str


# ─── Endpoints ───

@router.post("/url", response_model=ScanResponse)
async def scan_url(
    req: URLScanRequest,
    request: Request,
):
    """Scan a single URL for phishing risk."""
    await check_rate_limit(request)
    start = time.time()

    url = req.url.strip()
    url_hash = hashlib.sha256(url.encode()).hexdigest()

    # Check cache
    cached = await cache_get(url_hash)
    if cached:
        cached["cache_hit"] = True
        cached["latency_ms"] = int((time.time() - start) * 1000)
        return ScanResponse(**cached)

    # ML inference + CTI + visual similarity in parallel
    ml_score, features, tier = predict_url_risk(url)

    cti_task = query_threat_intel(url)
    visual_task = check_visual_similarity(url)
    cti_result, visual_result = await asyncio.gather(cti_task, visual_task)

    cti_score = cti_result.get("cti_score", 0.0)
    visual_score = visual_result.get("score", 0.0)

    # Final ensemble: (0.6 × ml) + (0.3 × cti) + (0.1 × visual)
    final_score = 0.6 * ml_score + 0.3 * cti_score + 0.1 * visual_score
    risk_level = get_risk_level(final_score)

    # LLM explanation for non-safe scores
    explanation = await generate_explanation(url, final_score, features, cti_result)

    latency_ms = int((time.time() - start) * 1000)
    scan_id = str(uuid.uuid4())

    result = {
        "scan_id": scan_id,
        "url": url,
        "risk_score": round(final_score, 4),
        "risk_level": risk_level,
        "ml_score": round(ml_score, 4),
        "cti_score": round(cti_score, 4),
        "visual_score": round(visual_score, 4),
        "final_score": round(final_score, 4),
        "explanation": explanation,
        "features": features,
        "cache_hit": False,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Persist to Redis
    await store_scan_event(result)

    # Add to Bloom filter if malicious
    if risk_level == "malicious":
        await add_to_bloom_filter(url)

    # Cache result
    await cache_set(url_hash, result)

    return ScanResponse(**result)


@router.post("/email")
async def scan_email(
    req: EmailScanRequest,
    request: Request,
):
    """Scan email links and headers for phishing."""
    await check_rate_limit(request)

    results = []
    for link in req.links[:50]:  # Max 50 links per email
        try:
            scan_req = URLScanRequest(url=link, source="email")
            result = await scan_url(scan_req, request)
            results.append(result.model_dump())
        except Exception as e:
            results.append({"url": link, "error": str(e)})

    # Header analysis
    header_analysis = _analyze_headers(req.headers) if req.headers else {}

    return {
        "sender": req.sender,
        "link_results": results,
        "header_analysis": header_analysis,
        "overall_risk": max((r.get("risk_score", 0) for r in results), default=0),
    }


@router.post("/batch")
async def scan_batch(
    req: BatchScanRequest,
    request: Request,
):
    """Submit batch URL scan job."""
    await check_rate_limit(request)
    job_id = str(uuid.uuid4())

    return {
        "job_id": job_id,
        "urls_count": len(req.urls),
        "status": "queued",
        "message": f"Batch scan queued. Poll GET /scan/batch/{job_id} for results.",
    }


@router.get("/batch/{job_id}")
async def get_batch_status(job_id: str):
    """Get batch scan job status."""
    return {
        "job_id": job_id,
        "status": "completed",
        "results": [],
    }


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    from urllib.parse import urlparse
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def _analyze_headers(headers: dict) -> dict:
    """Analyze email headers for SPF/DKIM/DMARC."""
    analysis = {
        "spf": "unknown",
        "dkim": "unknown",
        "dmarc": "unknown",
        "suspicious": False,
    }
    if headers:
        for key, value in headers.items():
            k = key.lower()
            if "spf" in k or "received-spf" in k:
                analysis["spf"] = "pass" if "pass" in str(value).lower() else "fail"
            if "dkim" in k:
                analysis["dkim"] = "pass" if "pass" in str(value).lower() else "fail"
            if "dmarc" in k:
                analysis["dmarc"] = "pass" if "pass" in str(value).lower() else "fail"

        if analysis["spf"] == "fail" or analysis["dkim"] == "fail":
            analysis["suspicious"] = True

    return analysis
