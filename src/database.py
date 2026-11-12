"""
Database Layer (SQLite)
Manages the normalized schema, audit trails (change detection history), and run logs.
Designed to be inspectable, deterministic, and self-contained.
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from src.config import DB_PATH, STATUS_ACTIVE, STATUS_REVIEW_REQUIRED, VERIFIED_CONFIDENCE_THRESHOLD

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Creates a connection to SQLite database with row factory for dict-like access."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: Path = DB_PATH) -> None:
    """Initializes the SQLite database with the 3 core tables:
    1. scholarships (Latest state)
    2. scholarship_history (Audit log for change detection)
    3. crawl_runs (Execution logs)
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Main scholarships table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scholarships (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            provider TEXT NOT NULL,
            source_type TEXT NOT NULL,
            official_source_url TEXT NOT NULL,
            application_url TEXT,
            amount TEXT DEFAULT 'Not specified',
            deadline TEXT DEFAULT 'Not specified',
            eligibility_summary TEXT DEFAULT 'Not specified',
            income_limit TEXT DEFAULT 'Not specified',
            education_level TEXT DEFAULT 'Not specified',
            gender TEXT DEFAULT 'All',
            category TEXT DEFAULT 'All',
            documents_required TEXT DEFAULT 'Not specified',
            selection_process TEXT DEFAULT 'Not specified',
            renewal_requirements TEXT DEFAULT 'Not specified',
            status TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            confidence_reason TEXT NOT NULL,
            evidence TEXT NOT NULL,
            last_verified_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)

        # 2. History table for change detection (Retains old vs new values)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scholarship_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scholarship_id TEXT NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            detected_at TEXT NOT NULL,
            source_url TEXT,
            evidence TEXT,
            FOREIGN KEY (scholarship_id) REFERENCES scholarships (id) ON DELETE CASCADE
        );
        """)

        # 3. Crawler run execution logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawl_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL UNIQUE,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            total_discovered INTEGER DEFAULT 0,
            total_verified INTEGER DEFAULT 0,
            changes_detected INTEGER DEFAULT 0,
            expired_detected INTEGER DEFAULT 0,
            summary_notes TEXT
        );
        """)

        conn.commit()

def save_scholarship(data: Dict[str, Any], db_path: Path = DB_PATH) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Saves or updates a scholarship record.
    If the record already exists, checks for changes in monitored fields (e.g. deadline, amount, status).
    When a change is detected, records the delta into scholarship_history without overwriting blindly.

    Returns:
        (is_new_record: bool, detected_changes: list)
    """
    now_iso = datetime.utcnow().isoformat()
    record_id = data.get("id")
    if not record_id:
        raise ValueError("Scholarship record must have an 'id'.")

    # Serialize JSON fields if passed as dicts
    evidence_json = json.dumps(data.get("evidence", {})) if isinstance(data.get("evidence"), dict) else (data.get("evidence") or "{}")
    confidence_reason_json = json.dumps(data.get("confidence_reason", {})) if isinstance(data.get("confidence_reason"), dict) else (data.get("confidence_reason") or "{}")

    # Ensure status conforms to confidence threshold
    confidence = float(data.get("confidence_score", 0.0))
    provided_status = data.get("status", STATUS_ACTIVE)
    if confidence < VERIFIED_CONFIDENCE_THRESHOLD and provided_status == STATUS_ACTIVE:
        provided_status = STATUS_REVIEW_REQUIRED

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scholarships WHERE id = ?", (record_id,))
        existing = cursor.fetchone()

        if existing is None:
            # Insert brand new record
            cursor.execute("""
            INSERT INTO scholarships (
                id, name, provider, source_type, official_source_url, application_url,
                amount, deadline, eligibility_summary, income_limit, education_level,
                gender, category, documents_required, selection_process, renewal_requirements,
                status, confidence_score, confidence_reason, evidence, last_verified_at,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record_id,
                data.get("name", "Untitled Scholarship"),
                data.get("provider", "Not specified"),
                data.get("source_type", "Government"),
                data.get("official_source_url", ""),
                data.get("application_url", ""),
                data.get("amount", "Not specified"),
                data.get("deadline", "Not specified"),
                data.get("eligibility_summary", "Not specified"),
                data.get("income_limit", "Not specified"),
                data.get("education_level", "Not specified"),
                data.get("gender", "All"),
                data.get("category", "All"),
                data.get("documents_required", "Not specified"),
                data.get("selection_process", "Not specified"),
                data.get("renewal_requirements", "Not specified"),
                provided_status,
                confidence,
                confidence_reason_json,
                evidence_json,
                now_iso,
                now_iso,
                now_iso
            ))
            conn.commit()
            return True, []

        else:
            # Existing record: check for changes
            existing_dict = dict(existing)
            monitored_fields = ["deadline", "amount", "status", "application_url", "eligibility_summary"]
            detected_changes = []

            for field in monitored_fields:
                old_val = str(existing_dict.get(field, "") or "").strip()
                new_val = str(data.get(field, "") or "").strip()

                if new_val and old_val != new_val:
                    field_evidence = ""
                    if isinstance(data.get("evidence"), dict):
                        field_evidence = data.get("evidence", {}).get(field, "")
                    elif isinstance(data.get("evidence"), str):
                        try:
                            parsed = json.loads(data["evidence"])
                            field_evidence = parsed.get(field, "")
                        except Exception:
                            field_evidence = data.get("evidence", "")

                    change_record = {
                        "scholarship_id": record_id,
                        "field_name": field,
                        "old_value": old_val,
                        "new_value": new_val,
                        "detected_at": now_iso,
                        "source_url": data.get("official_source_url", existing_dict.get("official_source_url")),
                        "evidence": field_evidence or f"Updated value observed during crawl: {new_val}"
                    }
                    detected_changes.append(change_record)

                    # Log into history table
                    cursor.execute("""
                    INSERT INTO scholarship_history (
                        scholarship_id, field_name, old_value, new_value, detected_at, source_url, evidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        change_record["scholarship_id"],
                        change_record["field_name"],
                        change_record["old_value"],
                        change_record["new_value"],
                        change_record["detected_at"],
                        change_record["source_url"],
                        change_record["evidence"]
                    ))

            # Update the latest row in scholarships table
            cursor.execute("""
            UPDATE scholarships SET
                name = ?,
                provider = ?,
                source_type = ?,
                official_source_url = ?,
                application_url = ?,
                amount = ?,
                deadline = ?,
                eligibility_summary = ?,
                income_limit = ?,
                education_level = ?,
                gender = ?,
                category = ?,
                documents_required = ?,
                selection_process = ?,
                renewal_requirements = ?,
                status = ?,
                confidence_score = ?,
                confidence_reason = ?,
                evidence = ?,
                last_verified_at = ?,
                updated_at = ?
            WHERE id = ?
            """, (
                data.get("name", existing_dict["name"]),
                data.get("provider", existing_dict["provider"]),
                data.get("source_type", existing_dict["source_type"]),
                data.get("official_source_url", existing_dict["official_source_url"]),
                data.get("application_url", existing_dict["application_url"]),
                data.get("amount", existing_dict["amount"]),
                data.get("deadline", existing_dict["deadline"]),
                data.get("eligibility_summary", existing_dict["eligibility_summary"]),
                data.get("income_limit", existing_dict["income_limit"]),
                data.get("education_level", existing_dict["education_level"]),
                data.get("gender", existing_dict["gender"]),
                data.get("category", existing_dict["category"]),
                data.get("documents_required", existing_dict["documents_required"]),
                data.get("selection_process", existing_dict["selection_process"]),
                data.get("renewal_requirements", existing_dict["renewal_requirements"]),
                provided_status,
                confidence,
                confidence_reason_json,
                evidence_json,
                now_iso,
                now_iso,
                record_id
            ))

            conn.commit()
            return False, detected_changes

def get_all_scholarships(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Fetches all scholarships ordered by updated timestamp descending."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scholarships ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_scholarship_by_id(scholarship_id: str, db_path: Path = DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves a single scholarship with parsed JSON fields."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scholarships WHERE id = ?", (scholarship_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        try:
            res["evidence"] = json.loads(res.get("evidence") or "{}")
        except Exception:
            pass
        try:
            res["confidence_reason"] = json.loads(res.get("confidence_reason") or "{}")
        except Exception:
            pass
        return res

def get_scholarship_history(scholarship_id: str, db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves change logs for a specific scholarship."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM scholarship_history
        WHERE scholarship_id = ?
        ORDER BY detected_at DESC
        """, (scholarship_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def log_crawl_run(
    run_id: str,
    started_at: str,
    completed_at: str,
    total_discovered: int,
    total_verified: int,
    changes_detected: int,
    expired_detected: int,
    summary_notes: str = "",
    db_path: Path = DB_PATH
) -> int:
    """Logs a crawl run execution summary."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO crawl_runs (
            run_id, started_at, completed_at, total_discovered, total_verified,
            changes_detected, expired_detected, summary_notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, started_at, completed_at, total_discovered, total_verified,
            changes_detected, expired_detected, summary_notes
        ))
        conn.commit()
        return cursor.lastrowid

def get_dashboard_metrics(db_path: Path = DB_PATH) -> Dict[str, Any]:
    """Calculates all key metrics needed for the Streamlit dashboard."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM scholarships")
        total_discovered = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE confidence_score >= ?", (VERIFIED_CONFIDENCE_THRESHOLD,))
        verified_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE status = ?", (STATUS_REVIEW_REQUIRED,))
        review_required_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE status = ?", (STATUS_ACTIVE,))
        active_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scholarships WHERE status = 'EXPIRED'")
        expired_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence_score) FROM scholarships")
        avg_confidence = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT COUNT(*) FROM scholarship_history")
        total_changes = cursor.fetchone()[0]

        return {
            "total_discovered": total_discovered,
            "verified": verified_count,
            "review_required": review_required_count,
            "active": active_count,
            "expired": expired_count,
            "average_confidence": round(avg_confidence, 1),
            "total_changes_detected": total_changes
        }
