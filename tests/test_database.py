"""
Unit tests for Database layer and change detection mechanism.
Supports both unittest and pytest.
"""
import unittest
import tempfile
from pathlib import Path
from src.database import (
    init_db,
    save_scholarship,
    get_all_scholarships,
    get_scholarship_by_id,
    get_scholarship_history,
    get_dashboard_metrics,
    log_crawl_run
)
from src.config import STATUS_ACTIVE, STATUS_REVIEW_REQUIRED, STATUS_EXPIRED

class TestDatabaseLayer(unittest.TestCase):
    def setUp(self):
        self.tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.test_db = Path(self.tf.name)
        init_db(self.test_db)

    def tearDown(self):
        if self.test_db.exists():
            self.test_db.unlink()

    def test_initial_scholarship_insertion(self):
        """Tests inserting a new scholarship into an empty database."""
        sample_data = {
            "id": "reliance-foundation-scholarship-2026",
            "name": "Reliance Foundation Undergraduate Scholarship",
            "provider": "Reliance Foundation",
            "source_type": "Corporate CSR",
            "official_source_url": "https://www.reliancefoundation.org/scholarships",
            "application_url": "https://scholarships.reliancefoundation.org/apply",
            "amount": "Up to ₹2,00,000 over degree duration",
            "deadline": "31 August 2026",
            "income_limit": "₹15,00,000 per annum",
            "education_level": "Undergraduate",
            "gender": "All",
            "category": "All",
            "status": STATUS_ACTIVE,
            "confidence_score": 98.4,
            "confidence_reason": {
                "official_domain": 30,
                "evidence_match": 30,
                "active_portal_url": 20,
                "current_year": 18.4
            },
            "evidence": {
                "deadline": "Applications close on 31 August 2026.",
                "amount": "Grant up to ₹2,00,000",
                "income_limit": "Annual household income less than 15 Lakh"
            }
        }

        is_new, changes = save_scholarship(sample_data, db_path=self.test_db)
        self.assertTrue(is_new)
        self.assertEqual(len(changes), 0)

        record = get_scholarship_by_id("reliance-foundation-scholarship-2026", db_path=self.test_db)
        self.assertIsNotNone(record)
        self.assertEqual(record["name"], "Reliance Foundation Undergraduate Scholarship")
        self.assertEqual(record["confidence_score"], 98.4)
        self.assertEqual(record["status"], STATUS_ACTIVE)
        self.assertIsInstance(record["evidence"], dict)
        self.assertEqual(record["evidence"]["deadline"], "Applications close on 31 August 2026.")

    def test_change_detection_and_audit_trail(self):
        """
        Tests the core requirement from Section 7 of PDF:
        Demonstrate that system detects changes (e.g. deadline changed from 31 August to 15 September)
        and retains old value, new value, date detected, and evidence without blindly overwriting.
        """
        # 1. Initial crawl (Run 1)
        run1_data = {
            "id": "nsp-post-matric-sc",
            "name": "Post Matric Scholarships Scheme for SC Students",
            "provider": "Ministry of Social Justice and Empowerment",
            "source_type": "Government",
            "official_source_url": "https://scholarships.gov.in",
            "application_url": "https://scholarships.gov.in/apply",
            "amount": "Full tuition fee plus maintenance allowance",
            "deadline": "31 August 2026",
            "income_limit": "₹2,50,000 per annum",
            "status": STATUS_ACTIVE,
            "confidence_score": 99.0,
            "evidence": {
                "deadline": "Portal closes for application submission on 31 August 2026."
            }
        }
        is_new, changes = save_scholarship(run1_data, db_path=self.test_db)
        self.assertTrue(is_new)

        # 2. Subsequent crawl (Run 2) with extended deadline
        run2_data = dict(run1_data)
        run2_data["deadline"] = "15 September 2026"
        run2_data["evidence"] = {
            "deadline": "Corrigendum: Application deadline extended to 15 September 2026."
        }

        is_new_run2, detected_changes = save_scholarship(run2_data, db_path=self.test_db)
        self.assertFalse(is_new_run2)
        self.assertEqual(len(detected_changes), 1)
        self.assertEqual(detected_changes[0]["field_name"], "deadline")
        self.assertEqual(detected_changes[0]["old_value"], "31 August 2026")
        self.assertEqual(detected_changes[0]["new_value"], "15 September 2026")

        # Verify history table retained the change audit trail
        history = get_scholarship_history("nsp-post-matric-sc", db_path=self.test_db)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["field_name"], "deadline")
        self.assertEqual(history[0]["old_value"], "31 August 2026")
        self.assertEqual(history[0]["new_value"], "15 September 2026")
        self.assertIn("Corrigendum: Application deadline extended to 15 September 2026.", history[0]["evidence"])

        # Verify updated record reflects current state
        updated_record = get_scholarship_by_id("nsp-post-matric-sc", db_path=self.test_db)
        self.assertEqual(updated_record["deadline"], "15 September 2026")

    def test_confidence_threshold_enforcement(self):
        """Tests that any scholarship with confidence < 95% is downgraded to REVIEW_REQUIRED."""
        unverified_data = {
            "id": "unverified-private-trust",
            "name": "General Merit Award",
            "provider": "Private Trust",
            "source_type": "Foundation/Trust",
            "official_source_url": "https://example-blog.org/scholarship",
            "status": STATUS_ACTIVE,  # Even if passed as active
            "confidence_score": 82.5,  # Below 95%
            "evidence": {}
        }
        save_scholarship(unverified_data, db_path=self.test_db)
        record = get_scholarship_by_id("unverified-private-trust", db_path=self.test_db)
        self.assertEqual(record["status"], STATUS_REVIEW_REQUIRED)

    def test_metrics_and_run_logging(self):
        """Tests aggregation of dashboard metrics and crawl run logging."""
        save_scholarship({
            "id": "s1",
            "name": "Scholarship 1",
            "provider": "Govt",
            "source_type": "Government",
            "official_source_url": "https://gov.in/s1",
            "status": STATUS_ACTIVE,
            "confidence_score": 96.0,
            "evidence": {}
        }, db_path=self.test_db)

        save_scholarship({
            "id": "s2",
            "name": "Scholarship 2",
            "provider": "Trust",
            "source_type": "Foundation/Trust",
            "official_source_url": "https://trust.org/s2",
            "status": STATUS_REVIEW_REQUIRED,
            "confidence_score": 80.0,
            "evidence": {}
        }, db_path=self.test_db)

        metrics = get_dashboard_metrics(db_path=self.test_db)
        self.assertEqual(metrics["total_discovered"], 2)
        self.assertEqual(metrics["verified"], 1)
        self.assertEqual(metrics["review_required"], 1)
        self.assertEqual(metrics["average_confidence"], 88.0)

        run_row_id = log_crawl_run(
            run_id="run_test_01",
            started_at="2026-11-12T10:00:00",
            completed_at="2026-11-12T10:05:00",
            total_discovered=2,
            total_verified=1,
            changes_detected=0,
            expired_detected=0,
            db_path=self.test_db
        )
        self.assertGreater(run_row_id, 0)

if __name__ == "__main__":
    unittest.main()

