"""
Lifecycle and Change Detection Engine
Monitors scholarships over subsequent crawl runs to detect changes in deadlines,
amounts, eligibility, and detects expired/stale opportunities.
"""
from datetime import datetime
from typing import Dict, Any, List, Tuple
from src.database import save_scholarship, get_scholarship_by_id, get_scholarship_history
from src.config import STATUS_EXPIRED, STATUS_ACTIVE, STATUS_REVIEW_REQUIRED

class ChangeDetector:
    def __init__(self):
        pass

    def process_crawl_result(self, record: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Saves or updates a scholarship and records audit history if changes are observed.
        Returns (is_new, changes_list).
        """
        return save_scholarship(record)

    def mark_expired_if_past_deadline(self, scholarship_id: str, deadline_str: str) -> bool:
        """Explicitly sets a scholarship to EXPIRED if deadline passed."""
        record = get_scholarship_by_id(scholarship_id)
        if not record:
            return False
            
        updated = dict(record)
        updated["status"] = STATUS_EXPIRED
        updated["evidence"] = dict(record.get("evidence", {}))
        updated["evidence"]["deadline"] = f"Marked EXPIRED: Application window closed ({deadline_str})."
        
        is_new, changes = save_scholarship(updated)
        return len(changes) > 0

