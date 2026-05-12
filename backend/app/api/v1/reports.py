"""PhishGuard — Reports API Endpoints.

GET /reports/summary, GET /reports/scans, GET /reports/export/stix
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from app.db.session import get_recent_scans, get_summary_stats

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
async def get_summary(
    days: int = Query(default=7, ge=1, le=90),
):
    """Get scan summary statistics."""
    return await get_summary_stats(days)


@router.get("/scans")
async def get_scans(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    risk_level: Optional[str] = None,
    search: Optional[str] = None,
):
    """Get paginated scan history."""
    result = await get_recent_scans(page, limit)

    # Client-side filtering (Redis doesn't support SQL WHERE)
    if risk_level or search:
        filtered = []
        for scan in result.get("scans", []):
            if risk_level and scan.get("risk_level") != risk_level:
                continue
            if search and search.lower() not in scan.get("url", "").lower():
                continue
            filtered.append(scan)
        result["scans"] = filtered
        result["total"] = len(filtered)

    return result


@router.get("/export/stix")
async def export_stix(
    days: int = Query(default=7, ge=1, le=90),
):
    """Export threat data as STIX 2.1 bundle."""
    result = await get_recent_scans(1, 1000)
    scans = result.get("scans", [])

    stix_objects = []
    for scan in scans:
        risk = scan.get("risk_level", "safe")
        if risk in ["malicious", "suspicious"]:
            stix_objects.append({
                "type": "indicator",
                "spec_version": "2.1",
                "id": f"indicator--{scan.get('scan_id', '')}",
                "created": scan.get("timestamp", ""),
                "name": f"Phishing URL: {scan.get('url', '')}",
                "pattern": f"[url:value = '{scan.get('url', '')}']",
                "pattern_type": "stix",
                "valid_from": scan.get("timestamp", ""),
                "labels": ["malicious-activity", "phishing"],
                "confidence": int((scan.get("risk_score", 0)) * 100),
            })

    return {
        "type": "bundle",
        "id": "bundle--phishguard-export",
        "spec_version": "2.1",
        "objects": stix_objects,
    }
