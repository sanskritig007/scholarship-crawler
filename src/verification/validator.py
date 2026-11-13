"""
Verification & Status Validation Module
Assigns official status (ACTIVE, REVIEW_REQUIRED, EXPIRED) based on confidence score and deadline.
Enforces the >=95% verification rule from PDF Section 4.
"""
from typing import Dict, Any
from src.config import (
    VERIFIED_CONFIDENCE_THRESHOLD,
    STATUS_ACTIVE,
    STATUS_REVIEW_REQUIRED,
    STATUS_EXPIRED,
    STATUS_EXPIRING_SOON
)
from src.verification.scorer import calculate_confidence_score

def verify_and_score_scholarship(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriches a scholarship record with calculated confidence score,
    transparent reason breakdown, and determined lifecycle status.
    """
    score, breakdown, explanation = calculate_confidence_score(record)
    
    # Check if expired based on score breakdown
    is_expired = (breakdown.get("recency") == 0.0 and record.get("deadline", "Not specified") != "Not specified")
    
    if is_expired:
        status = STATUS_EXPIRED
    elif score >= VERIFIED_CONFIDENCE_THRESHOLD:
        status = STATUS_ACTIVE
    else:
        status = STATUS_REVIEW_REQUIRED

    # Return updated record with scoring metadata
    enriched = dict(record)
    enriched["confidence_score"] = score
    enriched["confidence_reason"] = {
        "score": score,
        "breakdown": breakdown,
        "explanation": explanation,
        "is_verified": score >= VERIFIED_CONFIDENCE_THRESHOLD
    }
    enriched["status"] = status
    return enriched

