"""PhishGuard — Threat Intelligence Service.

Async parallel calls to VirusTotal v3, URLhaus, AbuseIPDB.
Graceful degradation if any service is down.
"""

import asyncio
from typing import Dict, Optional, Any
import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()


async def _query_virustotal(url: str, client: httpx.AsyncClient) -> Dict[str, Any]:
    """Query VirusTotal v3 API for URL analysis."""
    try:
        import base64
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        resp = await client.get(
            f"https://www.virustotal.com/api/v3/urls/{url_id}",
            headers={"x-apikey": settings.virustotal_api_key},
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            total = sum(stats.values()) if stats else 1
            return {
                "source": "virustotal",
                "available": True,
                "malicious_count": malicious,
                "total_engines": total,
                "score": malicious / max(total, 1),
                "raw": stats,
            }
        return {"source": "virustotal", "available": False, "reason": f"HTTP {resp.status_code}"}
    except Exception as e:
        logger.warning("virustotal_query_failed", error=str(e))
        return {"source": "virustotal", "available": False, "reason": str(e)}


async def _query_urlhaus(url: str, client: httpx.AsyncClient) -> Dict[str, Any]:
    """Query URLhaus API for URL lookup."""
    try:
        resp = await client.post(
            f"{settings.urlhaus_api_url}/url/",
            data={"url": url},
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            status_val = data.get("query_status", "no_results")
            return {
                "source": "urlhaus",
                "available": True,
                "is_malicious": status_val == "listed",
                "threat_type": data.get("threat", ""),
                "score": 1.0 if status_val == "listed" else 0.0,
            }
        return {"source": "urlhaus", "available": False, "reason": f"HTTP {resp.status_code}"}
    except Exception as e:
        logger.warning("urlhaus_query_failed", error=str(e))
        return {"source": "urlhaus", "available": False, "reason": str(e)}


async def _query_abuseipdb(ip: str, client: httpx.AsyncClient) -> Dict[str, Any]:
    """Query AbuseIPDB for IP reputation."""
    try:
        resp = await client.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={"ipAddress": ip, "maxAgeInDays": 90},
            headers={
                "Key": settings.abuseipdb_api_key,
                "Accept": "application/json",
            },
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            abuse_score = data.get("abuseConfidenceScore", 0) / 100.0
            return {
                "source": "abuseipdb",
                "available": True,
                "abuse_confidence": abuse_score,
                "total_reports": data.get("totalReports", 0),
                "score": abuse_score,
            }
        return {"source": "abuseipdb", "available": False, "reason": f"HTTP {resp.status_code}"}
    except Exception as e:
        logger.warning("abuseipdb_query_failed", error=str(e))
        return {"source": "abuseipdb", "available": False, "reason": str(e)}


async def query_threat_intel(url: str, ip: Optional[str] = None) -> Dict[str, Any]:
    """Run all CTI queries in parallel. Returns combined result."""
    async with httpx.AsyncClient() as client:
        tasks = [
            _query_virustotal(url, client),
            _query_urlhaus(url, client),
        ]
        if ip:
            tasks.append(_query_abuseipdb(ip, client))

        results = await asyncio.gather(*tasks, return_exceptions=True)

    processed = []
    total_score = 0.0
    available_count = 0

    for r in results:
        if isinstance(r, Exception):
            continue
        if isinstance(r, dict):
            processed.append(r)
            if r.get("available"):
                total_score += r.get("score", 0.0)
                available_count += 1

    cti_score = total_score / max(available_count, 1)

    return {
        "cti_score": cti_score,
        "sources": processed,
        "sources_available": available_count,
        "sources_total": len(tasks),
    }
