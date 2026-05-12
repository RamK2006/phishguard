"""PhishGuard — Data Models (Pydantic).

Lightweight Pydantic models replacing SQLAlchemy ORM.
Data is stored as JSON in Upstash Redis.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import enum


class RiskLevel(str, enum.Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class ScanSource(str, enum.Enum):
    EXTENSION = "extension"
    API = "api"
    DASHBOARD = "dashboard"
    BATCH = "batch"


class ScanEvent(BaseModel):
    """Scan event data model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    domain: str = ""
    risk_score: float = 0.0
    risk_level: str = "safe"
    ml_score: float = 0.0
    cti_score: float = 0.0
    visual_score: float = 0.0
    final_score: float = 0.0
    features: Dict[str, float] = Field(default_factory=dict)
    explanation: Dict[str, Any] = Field(default_factory=dict)
    source: str = "api"
    scan_type: str = "url"
    latency_ms: int = 0
    cache_hit: bool = False
    ip_address: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class FeedbackItem(BaseModel):
    """Feedback data model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scan_event_id: str
    feedback_type: str
    comment: str = ""
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
