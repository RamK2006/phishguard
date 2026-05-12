"""PhishGuard — Feedback API Endpoint.

POST /feedback/submit — analyst/user false-positive/negative reports.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.db.session import store_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    scan_event_id: str = Field(..., description="UUID of the scan event")
    feedback_type: str = Field(..., description="false_positive, false_negative, or correct")
    comment: str = Field(default="", max_length=1000)


@router.post("/submit")
async def submit_feedback(req: FeedbackRequest):
    """Submit feedback on a scan result."""
    feedback_id = str(uuid.uuid4())

    await store_feedback({
        "feedback_id": feedback_id,
        "scan_event_id": req.scan_event_id,
        "feedback_type": req.feedback_type,
        "comment": req.comment,
        "created_at": datetime.utcnow().isoformat(),
    })

    return {
        "status": "submitted",
        "feedback_id": feedback_id,
        "message": "Thank you for your feedback. It will be used to improve our detection.",
    }
