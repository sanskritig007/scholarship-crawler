"""
Confidence Scoring Engine
Calculates a deterministic 100-point confidence score based on actual evidence.
Strictly avoids arbitrary LLM guesses (PDF Section 4).
Provides transparent 'Why this score?' breakdown.
Uses standard library datetime parsing to run anywhere without external dependencies.
"""
import re
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from src.config import VERIFIED_CONFIDENCE_THRESHOLD

MONTHS_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

def parse_flexible_date(date_str: str) -> Optional[datetime]:
    """Parses date strings using standard library regex & datetime."""
    if not date_str or date_str == "Not specified":
        return None

    # Try "31 December 2026" or "15th Aug 2026"
    match = re.search(r'(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})', date_str)
    if match:
        day = int(match.group(1))
        month_name = match.group(2).lower()
        year = int(match.group(3))
        month = MONTHS_MAP.get(month_name)
        if month:
            try:
                return datetime(year, month, day)
            except ValueError:
                pass

    # Try DD/MM/YYYY or DD-MM-YYYY
    match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', date_str)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError:
            pass

    # Try YYYY-MM-DD
    match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_str)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError:
            pass

    return None

def calculate_confidence_score(record: Dict[str, Any]) -> Tuple[float, Dict[str, Any], str]:
    """
    Computes an evidence-based confidence score across 4 pillars:
    1. Source Authority (Max 30 pts)
    2. Evidence Grounding (Max 30 pts)
    3. Application Link Health (Max 20 pts)
    4. Temporal Recency & Active Status (Max 20 pts)

    Returns:
        (total_score: float, score_breakdown: dict, explanation: str)
    """
    breakdown = {}
    explanations = []

    # --- Pillar 1: Source Authority (0 - 30 pts) ---
    source_type = record.get("source_type", "")
    domain_score = float(record.get("domain_authority_score", 0.0))
    if domain_score > 0:
        authority_pts = min(domain_score, 30.0)
    else:
        if source_type == "Government":
            authority_pts = 30.0
        elif source_type in ["Corporate CSR", "University"]:
            authority_pts = 28.0
        elif source_type == "Foundation/Trust":
            authority_pts = 25.0
        else:
            authority_pts = 5.0

    breakdown["source_authority"] = round(authority_pts, 1)
    explanations.append(f"+{authority_pts} pts for authoritative primary domain ({source_type})")

    # --- Pillar 2: Evidence Grounding (0 - 30 pts) ---
    grounding_pts = 0.0
    evidence = record.get("evidence", {})
    if isinstance(evidence, str):
        try:
            import json
            evidence = json.loads(evidence)
        except Exception:
            evidence = {}

    # Deadline grounding (15 pts)
    deadline_val = record.get("deadline", "Not specified")
    deadline_ev = evidence.get("deadline", "")
    if deadline_val != "Not specified" and len(deadline_ev) > 10 and "no explicit" not in deadline_ev.lower():
        grounding_pts += 15.0
        explanations.append("+15 pts for verified deadline grounded in primary source text")
    elif deadline_val == "Not specified":
        grounding_pts += 5.0
        explanations.append("+5 pts for honest unstated deadline (anti-hallucination default)")

    # Amount grounding (15 pts)
    amount_val = record.get("amount", "Not specified")
    amount_ev = evidence.get("amount", "")
    if amount_val != "Not specified" and len(amount_ev) > 10 and "no financial" not in amount_ev.lower():
        grounding_pts += 15.0
        explanations.append("+15 pts for verified monetary benefit quote")
    elif amount_val == "Not specified":
        grounding_pts += 5.0
        explanations.append("+5 pts for honest unstated benefit (anti-hallucination default)")

    breakdown["evidence_grounding"] = round(grounding_pts, 1)

    # --- Pillar 3: Application Portal Link (0 - 20 pts) ---
    app_url = record.get("application_url", "").strip()
    official_url = record.get("official_source_url", "").strip()
    app_pts = 0.0

    if app_url and app_url.startswith("http"):
        if "apply" in app_url.lower() or "login" in app_url.lower() or "scheme" in app_url.lower() or app_url != official_url:
            app_pts = 20.0
            explanations.append("+20 pts for dedicated application/registration portal URL")
        else:
            app_pts = 16.0
            explanations.append("+16 pts for official scheme page URL")
    else:
        app_pts = 0.0
        explanations.append("+0 pts: Missing application portal link")

    breakdown["application_link"] = round(app_pts, 1)

    # --- Pillar 4: Temporal Recency & Active Status (0 - 20 pts) ---
    recency_pts = 0.0
    parsed_date = parse_flexible_date(deadline_val)

    if parsed_date:
        current_date = datetime.now()
        if parsed_date.date() >= current_date.date():
            recency_pts = 20.0
            explanations.append("+20 pts for active current/future application deadline")
        else:
            recency_pts = 0.0
            explanations.append("+0 pts: Deadline has passed (Stale/Expired)")
    elif deadline_val != "Not specified":
        if "2026" in deadline_val or "2027" in deadline_val:
            recency_pts = 18.5
            explanations.append("+18.5 pts for current cycle year mention")
        else:
            recency_pts = 10.0
            explanations.append("+10 pts for valid undated scheme announcement")
    else:
        recency_pts = 10.0
        explanations.append("+10 pts for rolling/ongoing open scheme")

    breakdown["recency"] = round(recency_pts, 1)

    total_score = min(100.0, max(0.0, authority_pts + grounding_pts + app_pts + recency_pts))
    total_score = round(total_score, 1)
    explanation_text = " | ".join(explanations)

    return total_score, breakdown, explanation_text
