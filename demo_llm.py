"""
Live Interactive Proof: LLM Extraction & AI Hallucination Guardrail Demo
Run this script using:
    python3 demo_llm.py
"""
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.extraction.llm_extractor import LLMScholarshipExtractor, LLM_SYSTEM_PROMPT
from src.verification.scorer import calculate_confidence_score

def print_banner(text):
    print("\n" + "=" * 75)
    print(f"  {text}")
    print("=" * 75)

def main():
    print_banner("🤖 LLM EXTRACTION & ANTI-HALLUCINATION GUARDRAIL DEMO")
    print("Demonstrating how an LLM parses messy unstructured circulars,")
    print("extracts schema entities, and is audited against hallucination.\n")

    # Sample messy unstructured text from a real government scheme notice
    sample_raw_notice = """
    OFFICE MEMORANDUM - ALL INDIA COUNCIL FOR TECHNICAL EDUCATION
    Ref No: AICTE/SD/PRAGATI/2026-27

    Subject: Implementation of AICTE Pragati Scholarship Scheme for Girl Students.

    It is hereby notified that applications are invited for the academic session 2026-2027.
    Under this scheme, 10,000 girl students admitted to AICTE approved technical institutions
    in degree and diploma level courses are eligible to receive a financial grant of Rs. 50,000 per annum
    towards college fees, books, equipment and hostel maintenance.
    All eligible female students must submit their complete documentation on the portal on or before 31 December 2026.
    Parental income certificate is required, and annual family income must be less than Rs. 8 Lakh per annum.
    Disbursement will be handled strictly via Direct Benefit Transfer (DBT).
    """

    print("📥 1. UNSTRUCTURED INPUT NOTICE (Messy Government Circular):")
    print("-" * 75)
    print(sample_raw_notice.strip())
    print("-" * 75)

    print("\n🧠 2. EXECUTING LLM WITH STRICT ANTI-HALLUCINATION PROMPT...")
    extractor = LLMScholarshipExtractor()
    extracted_json = extractor.generate_extraction(sample_raw_notice, "https://www.aicte-india.org/pragati")

    print("\n📋 3. LLM STRUCTURED OUTPUT (Machine-Readable JSON):")
    print(json.dumps(extracted_json, indent=2))

    print_banner("🛡️ 4. AI GUARDRAIL AUDIT (Proof Against Hallucination)")
    is_safe, audit = extractor.verify_llm_hallucination(sample_raw_notice, extracted_json)
    for field, status in audit.items():
        print(f"   ► Field [{field}]: {status}")

    print(f"\n   Overall AI Hallucination Check: {'✅ PASSED (100% Grounded in Primary Source)' if is_safe else '❌ FAILED'}")

    # Compute Evidence Confidence Score
    test_record = dict(extracted_json)
    test_record["source_type"] = "Government"
    test_record["official_source_url"] = "https://www.aicte-india.org/pragati"
    test_record["application_url"] = "https://scholarships.gov.in"
    test_record["domain_authority_score"] = 30.0

    score, breakdown, explanation = calculate_confidence_score(test_record)

    print_banner("📊 5. DETERMINISTIC CONFIDENCE SCORE (PDF Section 4)")
    print(f"   Calculated Confidence Score: {score}%")
    print(f"   Status Determination:        {'✅ VERIFIED' if score >= 95.0 else '⚠️ REVIEW REQUIRED'}")
    print(f"   Rubric Breakdown:")
    for k, v in breakdown.items():
        print(f"     • {k.replace('_', ' ').title()}: {v} pts")
    print(f"\n   Explanation: {explanation}\n")

if __name__ == "__main__":
    main()

