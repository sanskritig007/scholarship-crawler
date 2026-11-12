"""
Source Classification Engine
Analyzes URLs and domains to determine source type and authenticity level.
Differentiates between authoritative primary sources (Government, CSR, University)
and aggregator/unverified third-party sources.
"""
from urllib.parse import urlparse
from typing import Tuple, Dict, Any
from src.config import (
    SOURCE_GOVERNMENT,
    SOURCE_CORPORATE_CSR,
    SOURCE_UNIVERSITY,
    SOURCE_FOUNDATION,
)

# Known authentic domains mapping
VERIFIED_CSR_DOMAINS = {
    "reliancefoundation.org": "Reliance Foundation",
    "scholarships.reliancefoundation.org": "Reliance Foundation",
    "tatatrusts.org": "Tata Trusts",
    "infosys.org": "Infosys Foundation",
    "hdfcbank.com": "HDFC Bank Parivartan",
    "azimpremjifoundation.org": "Azim Premji Foundation",
    "adityabirlacsr.com": "Aditya Birla Group CSR",
    "loreal.com": "L'Oréal India",
    "onlinems.tatatrusts.org": "Tata Trusts",
}

VERIFIED_FOUNDATION_DOMAINS = {
    "vidyasaarathi.co.in": "Vidyasaarathi Portal",
    "sitaramjindalfoundation.org": "Sitaram Jindal Foundation",
    "kcfoundation.org": "KC Mahindra Education Trust",
    "inlaksfoundation.org": "Inlaks Shivdasani Foundation",
    "fairandlovelyfoundation.in": "Glow & Lovely Careers",
}

AGGREGATOR_DOMAINS = {
    "buddy4study.com",
    "scholarshipsads.com",
    "indcareer.com",
    "collegedunia.com",
    "shiksha.com",
    "careerindia.com",
    "sarkariresult.com",
}

def extract_domain(url: str) -> str:
    """Extracts lowercase clean hostname without 'www.' prefix."""
    try:
        netloc = urlparse(url).netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""

def classify_source(url: str) -> Dict[str, Any]:
    """
    Classifies a URL into a source category and computes domain authority score.

    Returns:
        {
            "source_type": str,
            "provider_guess": str,
            "is_official": bool,
            "domain_authority_score": float (0.0 to 30.0 for scoring rubric),
            "is_aggregator": bool
        }
    """
    domain = extract_domain(url)

    # 1. Government Domains (.gov.in, .nic.in, e.g., scholarships.gov.in, aicte-india.org)
    if domain.endswith(".gov.in") or domain.endswith(".nic.in") or domain in ["aicte-india.org", "ugc.ac.in"]:
        return {
            "source_type": SOURCE_GOVERNMENT,
            "provider_guess": "Government of India / State Department",
            "is_official": True,
            "domain_authority_score": 30.0,
            "is_aggregator": False,
            "domain": domain,
        }

    # 2. University / Academic Domains (.ac.in, .edu.in, .edu)
    if domain.endswith(".ac.in") or domain.endswith(".edu.in") or domain.endswith(".edu"):
        return {
            "source_type": SOURCE_UNIVERSITY,
            "provider_guess": "Academic Institution / University",
            "is_official": True,
            "domain_authority_score": 28.0,
            "is_aggregator": False,
            "domain": domain,
        }

    # 3. Verified Corporate CSR Portals
    for csr_domain, provider_name in VERIFIED_CSR_DOMAINS.items():
        if domain == csr_domain or domain.endswith("." + csr_domain):
            return {
                "source_type": SOURCE_CORPORATE_CSR,
                "provider_guess": provider_name,
                "is_official": True,
                "domain_authority_score": 28.0,
                "is_aggregator": False,
                "domain": domain,
            }

    # 4. Verified Trusts & Foundations
    for f_domain, provider_name in VERIFIED_FOUNDATION_DOMAINS.items():
        if domain == f_domain or domain.endswith("." + f_domain):
            return {
                "source_type": SOURCE_FOUNDATION,
                "provider_guess": provider_name,
                "is_official": True,
                "domain_authority_score": 25.0,
                "is_aggregator": False,
                "domain": domain,
            }

    # 5. Aggregators / Third-party Blogs (Not authoritative source per PDF section 2)
    for agg in AGGREGATOR_DOMAINS:
        if domain == agg or domain.endswith("." + agg):
            return {
                "source_type": "Aggregator",
                "provider_guess": "Third-Party Aggregator",
                "is_official": False,
                "domain_authority_score": 5.0,
                "is_aggregator": True,
                "domain": domain,
            }

    # 6. Unknown / Unclassified Domain
    return {
        "source_type": "Unknown",
        "provider_guess": "Unverified Provider",
        "is_official": False,
        "domain_authority_score": 10.0,
        "is_aggregator": False,
        "domain": domain,
    }

