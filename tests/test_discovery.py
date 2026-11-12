"""
Unit tests for Phase 2: Source Classification and Discovery Engine.
"""
import unittest
from src.discovery.classifier import classify_source
from src.discovery.finder import DiscoveryEngine
from src.config import SOURCE_GOVERNMENT, SOURCE_CORPORATE_CSR, SOURCE_UNIVERSITY

class TestDiscoveryAndClassification(unittest.TestCase):

    def test_government_domain_classification(self):
        """Official government portals must be recognized with maximum domain score."""
        res = classify_source("https://scholarships.gov.in/public/schemeGuidelines/101.pdf")
        self.assertEqual(res["source_type"], SOURCE_GOVERNMENT)
        self.assertTrue(res["is_official"])
        self.assertEqual(res["domain_authority_score"], 30.0)
        self.assertFalse(res["is_aggregator"])

        res2 = classify_source("https://www.aicte-india.org/schemes/students-development-schemes/pragati")
        self.assertEqual(res2["source_type"], SOURCE_GOVERNMENT)
        self.assertTrue(res2["is_official"])

    def test_corporate_csr_domain_classification(self):
        """Corporate CSR portals (Reliance, Tata Trusts, HDFC) must be correctly classified."""
        res = classify_source("https://scholarships.reliancefoundation.org/PG_Scholarship.aspx")
        self.assertEqual(res["source_type"], SOURCE_CORPORATE_CSR)
        self.assertTrue(res["is_official"])
        self.assertIn("Reliance", res["provider_guess"])
        self.assertGreaterEqual(res["domain_authority_score"], 25.0)

    def test_university_domain_classification(self):
        """University portals (.ac.in, .edu.in) must be classified as University."""
        res = classify_source("https://www.iitb.ac.in/en/academics/scholarships-and-awards")
        self.assertEqual(res["source_type"], SOURCE_UNIVERSITY)
        self.assertTrue(res["is_official"])
        self.assertGreaterEqual(res["domain_authority_score"], 25.0)

    def test_aggregator_downgrade(self):
        """Aggregators like Buddy4Study must not be treated as official sources (PDF Section 2)."""
        res = classify_source("https://www.buddy4study.com/scholarship/reliance-foundation-scholarship")
        self.assertEqual(res["source_type"], "Aggregator")
        self.assertFalse(res["is_official"])
        self.assertTrue(res["is_aggregator"])
        self.assertLess(res["domain_authority_score"], 10.0)

    def test_candidate_link_filtering(self):
        """Finder should pick up scholarship links and discard noise/login links."""
        engine = DiscoveryEngine()

        # Should match
        self.assertTrue(engine.is_candidate_link(
            "https://scholarships.gov.in/schemes/pragati-scholarship",
            "Pragati Scholarship Scheme for Girls"
        ))

        # Should exclude noise / auth links
        self.assertFalse(engine.is_candidate_link(
            "https://scholarships.gov.in/student-login",
            "Student Login"
        ))
        self.assertFalse(engine.is_candidate_link(
            "https://scholarships.gov.in/privacy-policy",
            "Privacy Policy & Terms"
        ))

if __name__ == "__main__":
    unittest.main()

