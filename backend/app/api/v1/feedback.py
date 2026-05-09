"""PhishGuard — Feedback API Endpoint.

POST /feedback/submit — analyst/user false-positive/negative reports.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import Feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    scan_event_id: str = Field(..., description="UUID of the scan event")
    feedback_type: str = Field(..., description="false_positive, false_negative, or correct")
    comment: str = Field(default="", max_length=1000)


@router.post("/submit")
async def submit_feedback(
    req: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback on a scan result."""
    feedback = Feedback(
        id=uuid.uuid4(),
        scan_event_id=uuid.UUID(req.scan_event_id),
        feedback_type=req.feedback_type,
        comment=req.comment,
        created_at=datetime.utcnow(),
    )

    db.add(feedback)
    await db.flush()

    return {
        "status": "submitted",
        "feedback_id": str(feedback.id),
        "message": "Thank you for your feedback. It will be used to improve our detection.",
    }
