"""
Unit tests for Phase 4: Verification and Confidence Scoring Engine.
"""
import unittest
from src.verification.scorer import calculate_confidence_score
from src.verification.validator import verify_and_score_scholarship
from src.config import STATUS_ACTIVE, STATUS_REVIEW_REQUIRED, STATUS_EXPIRED

class TestVerificationAndScoring(unittest.TestCase):

    def test_high_confidence_verified_scholarship(self):
        """
        An official Government scholarship with grounded evidence and active link
        must score >= 95% and be marked ACTIVE (Verified).
        """
        record = {
            "name": "NSP Post Matric Scholarship for SC",
            "provider": "Ministry of Social Justice and Empowerment",
            "source_type": "Government",
            "official_source_url": "https://scholarships.gov.in",
            "application_url": "https://scholarships.gov.in/applyNow",
            "domain_authority_score": 30.0,
            "deadline": "31 December 2026",
            "amount": "Rs. 50,000 per annum",
            "evidence": {
                "deadline": "Eligible candidates must apply before 31 December 2026.",
                "amount": "Selected scholars will receive Rs. 50,000 per annum."
            }
        }
        enriched = verify_and_score_scholarship(record)
        self.assertGreaterEqual(enriched["confidence_score"], 95.0)
        self.assertEqual(enriched["status"], STATUS_ACTIVE)
        self.assertIn("breakdown", enriched["confidence_reason"])
        self.assertEqual(enriched["confidence_reason"]["breakdown"]["source_authority"], 30.0)

    def test_aggregator_downgraded_to_review_required(self):
        """
        Third-party / aggregator sources (PDF Section 2) must not score >= 95%
        and must be assigned STATUS_REVIEW_REQUIRED.
        """
        record = {
            "name": "Private Merit Award",
            "provider": "Unverified Trust",
            "source_type": "Aggregator",
            "official_source_url": "https://www.buddy4study.com/scholarship/sample",
            "application_url": "https://www.buddy4study.com/apply",
            "domain_authority_score": 5.0,  # Aggregator penalized score
            "deadline": "31 December 2026",
            "amount": "Rs. 20,000",
            "evidence": {
                "deadline": "Apply before 31 December 2026.",
                "amount": "Scholarship is Rs. 20,000."
            }
        }
        enriched = verify_and_score_scholarship(record)
        self.assertLess(enriched["confidence_score"], 95.0)
        self.assertEqual(enriched["status"], STATUS_REVIEW_REQUIRED)

    def test_expired_scholarship_detection(self):
        """
        A scholarship with a past deadline must be categorized as EXPIRED.
        """
        record = {
            "name": "Legacy Fellowship 2020",
            "provider": "Government Department",
            "source_type": "Government",
            "official_source_url": "https://scholarships.gov.in",
            "application_url": "https://scholarships.gov.in/apply",
            "domain_authority_score": 30.0,
            "deadline": "15 January 2020",  # Far in the past
            "amount": "Rs. 30,000",
            "evidence": {
                "deadline": "Deadline was 15 January 2020.",
                "amount": "Amount Rs. 30,000."
            }
        }
        enriched = verify_and_score_scholarship(record)
        self.assertEqual(enriched["status"], STATUS_EXPIRED)
        self.assertEqual(enriched["confidence_reason"]["breakdown"]["recency"], 0.0)

    def test_why_this_score_transparency(self):
        """
        PDF Section 10 Requirement: 'Why this score?' must provide clear, explainable factors.
        """
        record = {
            "name": "Reliance Foundation Undergraduate Scholarship",
            "provider": "Reliance Foundation",
            "source_type": "Corporate CSR",
            "official_source_url": "https://scholarships.reliancefoundation.org",
            "application_url": "https://scholarships.reliancefoundation.org/apply",
            "domain_authority_score": 28.0,
            "deadline": "31 October 2026",
            "amount": "Rs. 2,00,000",
            "evidence": {
                "deadline": "Applications close on 31 October 2026.",
                "amount": "Grant up to Rs. 2,00,000 over duration of degree."
            }
        }
        score, breakdown, explanation = calculate_confidence_score(record)
        self.assertIn("source_authority", breakdown)
        self.assertIn("evidence_grounding", breakdown)
        self.assertIn("application_link", breakdown)
        self.assertIn("recency", breakdown)
        self.assertTrue(len(explanation) > 20)

if __name__ == "__main__":
    unittest.main()

