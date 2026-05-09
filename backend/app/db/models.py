"""PhishGuard — SQLAlchemy Async ORM Models.

Tables: users, scan_events, feedback, threat_reports, brand_database.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text,
    ForeignKey, JSON, Index, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class RiskLevel(str, enum.Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"


class ScanSource(str, enum.Enum):
    EXTENSION = "extension"
    API = "api"
    DASHBOARD = "dashboard"
    BATCH = "batch"


class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    role = Column(String(50), default="analyst")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scan_events = relationship("ScanEvents", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")


class ScanEvents(Base):
    __tablename__ = "scan_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False)
    domain = Column(String(255), nullable=True)
    risk_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(SAEnum(RiskLevel), nullable=False, default=RiskLevel.SAFE)
    ml_score = Column(Float, nullable=True)
    cti_score = Column(Float, nullable=True)
    visual_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)

    # Feature data
    features = Column(JSONB, nullable=True)

    # Threat intelligence results
    virustotal_result = Column(JSONB, nullable=True)
    urlhaus_result = Column(JSONB, nullable=True)
    abuseipdb_result = Column(JSONB, nullable=True)

    # LLM explanation
    explanation = Column(JSONB, nullable=True)

    # Source and metadata
    source = Column(SAEnum(ScanSource), default=ScanSource.API)
    scan_type = Column(String(20), default="url")  # url, email, batch
    latency_ms = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False)
    ip_address = Column(String(45), nullable=True)
    country_code = Column(String(2), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relations
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("Users", back_populates="scan_events")

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index("ix_scan_events_risk_level", "risk_level"),
        Index("ix_scan_events_domain", "domain"),
        Index("ix_scan_events_created_at_desc", created_at.desc()),
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_event_id = Column(UUID(as_uuid=True), ForeignKey("scan_events.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    feedback_type = Column(String(20), nullable=False)  # false_positive, false_negative, correct
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("Users", back_populates="feedback")
    scan_event = relationship("ScanEvents")


class ThreatReports(Base):
    __tablename__ = "threat_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="medium")
    ioc_type = Column(String(50), nullable=True)  # url, domain, ip, hash
    ioc_value = Column(Text, nullable=True)
    stix_bundle = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BrandDatabase(Base):
    __tablename__ = "brand_database"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_name = Column(String(255), nullable=False, unique=True)
    legitimate_domains = Column(JSONB, nullable=False, default=list)
    logo_hash = Column(String(64), nullable=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
