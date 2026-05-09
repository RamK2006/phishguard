"""PhishGuard — Reports API Endpoints.

GET /reports/summary, GET /reports/scans, GET /reports/export/stix
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import ScanEvents, RiskLevel

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
async def get_summary(
    days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Get scan summary statistics."""
    since = datetime.utcnow() - timedelta(days=days)

    total = await db.scalar(
        select(func.count(ScanEvents.id)).where(ScanEvents.created_at >= since)
    )
    malicious = await db.scalar(
        select(func.count(ScanEvents.id)).where(
            and_(ScanEvents.created_at >= since, ScanEvents.risk_level == RiskLevel.MALICIOUS)
        )
    )
    suspicious = await db.scalar(
        select(func.count(ScanEvents.id)).where(
            and_(ScanEvents.created_at >= since, ScanEvents.risk_level == RiskLevel.SUSPICIOUS)
        )
    )
    safe = await db.scalar(
        select(func.count(ScanEvents.id)).where(
            and_(ScanEvents.created_at >= since, ScanEvents.risk_level == RiskLevel.SAFE)
        )
    )
    avg_latency = await db.scalar(
        select(func.avg(ScanEvents.latency_ms)).where(ScanEvents.created_at >= since)
    )

    return {
        "period_days": days,
        "total_scans": total or 0,
        "malicious": malicious or 0,
        "suspicious": suspicious or 0,
        "safe": safe or 0,
        "malicious_rate": round((malicious or 0) / max(total or 1, 1) * 100, 2),
        "avg_latency_ms": round(avg_latency or 0, 1),
    }


@router.get("/scans")
async def get_scans(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get paginated scan history."""
    query = select(ScanEvents).order_by(ScanEvents.created_at.desc())

    if risk_level:
        query = query.where(ScanEvents.risk_level == RiskLevel(risk_level))
    if search:
        query = query.where(ScanEvents.url.ilike(f"%{search}%"))

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    scans = result.scalars().all()

    count_query = select(func.count(ScanEvents.id))
    if risk_level:
        count_query = count_query.where(ScanEvents.risk_level == RiskLevel(risk_level))
    if search:
        count_query = count_query.where(ScanEvents.url.ilike(f"%{search}%"))
    total = await db.scalar(count_query)

    return {
        "scans": [
            {
                "id": str(s.id),
                "url": s.url,
                "domain": s.domain,
                "risk_score": s.risk_score,
                "risk_level": s.risk_level.value if s.risk_level else "safe",
                "source": s.source.value if s.source else "api",
                "latency_ms": s.latency_ms,
                "cache_hit": s.cache_hit,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "explanation": s.explanation,
            }
            for s in scans
        ],
        "total": total or 0,
        "page": page,
        "limit": limit,
        "pages": ((total or 0) + limit - 1) // limit,
    }


@router.get("/export/stix")
async def export_stix(
    days: int = Query(default=7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Export threat data as STIX 2.1 bundle."""
    since = datetime.utcnow() - timedelta(days=days)

    result = await db.execute(
        select(ScanEvents)
        .where(
            and_(
                ScanEvents.created_at >= since,
                ScanEvents.risk_level.in_([RiskLevel.MALICIOUS, RiskLevel.SUSPICIOUS]),
            )
        )
        .limit(1000)
    )
    scans = result.scalars().all()

    stix_objects = []
    for scan in scans:
        stix_objects.append({
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{scan.id}",
            "created": scan.created_at.isoformat() if scan.created_at else "",
            "name": f"Phishing URL: {scan.domain}",
            "pattern": f"[url:value = '{scan.url}']",
            "pattern_type": "stix",
            "valid_from": scan.created_at.isoformat() if scan.created_at else "",
            "labels": ["malicious-activity", "phishing"],
            "confidence": int((scan.risk_score or 0) * 100),
        })

    return {
        "type": "bundle",
        "id": "bundle--phishguard-export",
        "spec_version": "2.1",
        "objects": stix_objects,
    }
