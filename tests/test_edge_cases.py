"""
Edge Cases and Resiliency Test Suite
Tests corner cases specified in Edxso Assignment 2:
1. Distinct Primary Source URL vs Direct Application Link
2. Anti-Hallucination & Missing Fields (Defaulting to 'Not specified')
3. Automatic Downgrade of Aggregators/Blogs to REVIEW_REQUIRED (<95%)
4. Expired/Stale Deadline Handling
5. Change Detection Corrigendum Audit Log
"""
import unittest
from src.database import init_db, save_scholarship, get_scholarship_by_id, get_scholarship_history
from src.extraction.extractor import ScholarshipExtractor
from src.verification.scorer import calculate_confidence_score, parse_flexible_date
from src.verification.validator import verify_and_score_scholarship
from src.config import STATUS_ACTIVE, STATUS_REVIEW_REQUIRED, STATUS_EXPIRED

class TestCrawlerEdgeCases(unittest.TestCase):

    def setUp(self):
        self.extractor = ScholarshipExtractor()

    def test_distinct_official_vs_application_urls(self):
        """
        Ensures that primary source URL (notification) and application URL (registration portal)
        are distinct where available (PDF Section 2 & 10).
        """
        from src.crawler import REAL_INDIAN_SCHOLARSHIPS
        distinct_count = 0
        for item in REAL_INDIAN_SCHOLARSHIPS:
            if item.get("application_url") and item.get("official_source_url") != item.get("application_url"):
                distinct_count += 1

        # At least 15+ should have dedicated distinct application links
        self.assertGreaterEqual(distinct_count, 15)

    def test_missing_income_anti_hallucination_rule(self):
        """
        PDF Section 5: 'If the official source does not mention an income limit:
        Income limit: Not specified (not 5 lakh)'.
        """
        raw_text = "The Prime Minister Research Fellowship offers Rs 70,000 monthly grant to Ph.D. scholars."
        income_val, evidence = self.extractor.extract_income_limit(raw_text)
        self.assertEqual(income_val, "Not specified")
        self.assertIn("not specified", evidence.lower())

    def test_aggregator_downgrade_edge_case(self):
        """
        Aggregators (Buddy4Study / blogs) must be penalized and CANNOT score >= 95%
        even if they claim a high scholarship value.
        """
        aggregator_record = {
            "name": "Aggregator Posted Scheme",
            "provider": "Third-Party Aggregator",
            "source_type": "Aggregator",
            "official_source_url": "https://www.buddy4study.com/scholarship/sample-lead",
            "application_url": "https://www.buddy4study.com/apply",
            "domain_authority_score": 5.0,  # Aggregator authority
            "deadline": "31 December 2026",
            "amount": "Rs. 1,00,000",
            "evidence": {
                "deadline": "Closes 31 December 2026.",
                "amount": "Grant Rs 1,00,000."
            }
        }
        enriched = verify_and_score_scholarship(aggregator_record)
        self.assertLess(enriched["confidence_score"], 95.0)
        self.assertEqual(enriched["status"], STATUS_REVIEW_REQUIRED)

    def test_expired_stale_detection_edge_case(self):
        """
        Scholarships with past deadlines must receive 0 recency points and be marked EXPIRED.
        """
        expired_record = {
            "name": "Historical Scheme 2021",
            "provider": "Government",
            "source_type": "Government",
            "official_source_url": "https://scholarships.gov.in",
            "deadline": "15 January 2021",  # Past date
            "amount": "Rs. 25,000",
            "evidence": {"deadline": "Closed on 15 January 2021."}
        }
        enriched = verify_and_score_scholarship(expired_record)
        self.assertEqual(enriched["status"], STATUS_EXPIRED)

    def test_change_detection_preserves_audit_trail(self):
        """
        PDF Section 7: System must detect change, retain old value, new value, date detected,
        and evidence WITHOUT simply overwriting.
        """
        initial_data = {
            "id": "edge-case-scheme-1",
            "name": "Test Corrigendum Scheme",
            "provider": "Ministry of Education",
            "source_type": "Government",
            "official_source_url": "https://education.gov.in",
            "deadline": "31 December 2026",
            "status": STATUS_ACTIVE,
            "confidence_score": 98.0,
            "evidence": {"deadline": "Initial deadline 31 December 2026."}
        }
        save_scholarship(initial_data)

        # Update with extended deadline
        updated_data = dict(initial_data)
        updated_data["deadline"] = "15 February 2027"
        updated_data["evidence"] = {"deadline": "Official Corrigendum: Extended to 15 February 2027."}
        
        is_new, changes = save_scholarship(updated_data)
        self.assertFalse(is_new)
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0]["old_value"], "31 December 2026")
        self.assertEqual(changes[0]["new_value"], "15 February 2027")

        history = get_scholarship_history("edge-case-scheme-1")
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[0]["old_value"], "31 December 2026")
        self.assertEqual(history[0]["new_value"], "15 February 2027")

if __name__ == "__main__":
    unittest.main()

