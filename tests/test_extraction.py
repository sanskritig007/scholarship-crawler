"""
Unit tests for Phase 3: Extraction and Anti-Hallucination Grounding.
"""
import unittest
from src.extraction.grounding import find_evidence_snippet, ground_field
from src.extraction.extractor import ScholarshipExtractor

class TestExtractionAndGrounding(unittest.TestCase):

    def setUp(self):
        self.extractor = ScholarshipExtractor()

    def test_anti_hallucination_missing_field(self):
        """
        Critical Rule (PDF Section 5):
        If the official source does not mention an income limit:
        Income limit: Not specified (not 5 lakh).
        """
        sample_text = """
        The National Merit Scholarship provides financial support to undergraduate students.
        Applications close on 31 October 2026.
        Selected candidates receive Rs. 50,000 annually.
        """
        # Income limit is NOT mentioned in the text
        income_val, evidence_snippet = self.extractor.extract_income_limit(sample_text)
        self.assertEqual(income_val, "Not specified")
        self.assertIn("not specified", evidence_snippet.lower())

    def test_deadline_extraction_and_evidence_grounding(self):
        """
        Deadline must be traced back to exact source sentence evidence.
        """
        sample_text = """
        AICTE Pragati Scheme for Girls in Technical Education.
        Eligible female students must apply before 31 December 2026 at 11:59 PM.
        Scholarship amount is Rs. 50,000 per annum.
        """
        deadline, evidence = self.extractor.extract_deadline(sample_text)
        self.assertIn("31 December 2026", deadline)
        self.assertEqual(evidence, "Eligible female students must apply before 31 December 2026 at 11:59 PM.")

    def test_amount_extraction_and_grounding(self):
        """
        Monetary amount must be extracted with verbatim sentence proof.
        """
        sample_text = """
        Reliance Foundation Postgraduate Scholarship 2026.
        Selected scholars will receive a grant of up to Rs. 6,00,000 over the duration of degree.
        Closing date is 15 November 2026.
        """
        amount, evidence = self.extractor.extract_amount(sample_text)
        self.assertIn("6,00,000", amount)
        self.assertIn("grant of up to Rs. 6,00,000", evidence)

    def test_full_record_schema_conformance(self):
        """
        Verifies that extract_record builds the complete 18+ field schema with evidence map.
        """
        text = """
        HDFC Bank Parivartan's ECSS Programme 2026.
        Parental income must be less than Rs. 2.5 Lakh per annum.
        Applications close on 30 September 2026.
        Financial assistance of up to Rs. 75,000 provided.
        """
        record = self.extractor.extract_record(
            raw_text=text,
            page_title="HDFC Bank ECSS Scholarship Scheme",
            official_url="https://www.hdfcbank.com/parivartan/scholarships"
        )

        self.assertEqual(record["source_type"], "Corporate CSR")
        self.assertIn("HDFC", record["provider"])
        self.assertIn("30 September 2026", record["deadline"])
        self.assertIn("75,000", record["amount"])
        self.assertIn("2.5 Lakh", record["income_limit"])
        self.assertIn("deadline", record["evidence"])
        self.assertIn("income_limit", record["evidence"])

if __name__ == "__main__":
    unittest.main()

