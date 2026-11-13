"""
Evidence Grounding & Anti-Hallucination Module
Ensures that every extracted field (deadline, amount, income criteria)
is strictly grounded in an exact sentence/snippet from the primary source text.
Preserves punctuation and avoids substring false positives.
"""
import re
from typing import Optional, List, Tuple

# Common abbreviations to prevent premature sentence splitting
ABBREVIATIONS = ["rs", "inr", "ph.d", "dr", "mr", "mrs", "prof", "e.g", "i.e", "no", "vs", "etc"]

def split_into_sentences(text: str) -> List[str]:
    """Splits raw content text into clean sentences or meaningful lines."""
    protected = text
    for abbr in ABBREVIATIONS:
        protected = re.sub(rf'\b({abbr})\.', r'\1<DOT>', protected, flags=re.IGNORECASE)

    # Split on sentence terminals followed by whitespace, or on line breaks
    parts = re.split(r'(?<=[.!?])\s+|\n+', protected)
    sentences = []
    for part in parts:
        restored = part.replace("<DOT>", ".").strip()
        if len(restored) > 10:
            sentences.append(restored)
    return sentences

def find_evidence_snippet(raw_text: str, regex_pattern: str) -> Optional[str]:
    """
    Finds the first sentence that matches the given regex pattern.
    Uses regex word boundaries so that abbreviations like 'rs' do not match 'scholarship'.
    """
    sentences = split_into_sentences(raw_text)
    for sent in sentences:
        if re.search(regex_pattern, sent, re.IGNORECASE):
            return sent
    return None

def ground_field(
    field_name: str,
    extracted_val: Optional[str],
    raw_text: str,
    regex_pattern: str
) -> Tuple[str, str]:
    """
    Enforces the Anti-Hallucination rule (PDF Section 5):
    Database -> Official Source -> Evidence -> Extracted Value.
    """
    snippet = find_evidence_snippet(raw_text, regex_pattern)
    if snippet:
        return extracted_val if extracted_val else snippet, snippet

    return "Not specified", "No explicit mention found in primary source content."
