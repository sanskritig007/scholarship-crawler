"""
Discovery Engine
Discovers scholarship opportunities starting from authoritative seed portals.
Classifies sources and extracts candidate opportunity links without hardcoded 1-to-1 scraping.
"""
import re
import logging
from typing import List, Dict, Any, Set
from urllib.parse import urlparse
from src.discovery.classifier import classify_source
from src.scraper.fetcher import WebFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Primary Authoritative Seed Portals (Covering Government, CSR, University, and Foundations)
SEED_PORTALS = [
    {
        "name": "National Scholarship Portal (Government of India)",
        "url": "https://scholarships.gov.in",
        "category": "Government"
    },
    {
        "name": "AICTE Official Schemes Portal",
        "url": "https://www.aicte-india.org/schemes/students-development-schemes",
        "category": "Government"
    },
    {
        "name": "Reliance Foundation Scholarships Portal",
        "url": "https://scholarships.reliancefoundation.org",
        "category": "Corporate CSR"
    },
    {
        "name": "Tata Trusts Education Grants",
        "url": "https://www.tatatrusts.org/our-work/individual-grants-programme/education-grants",
        "category": "Corporate CSR"
    },
    {
        "name": "IIT Bombay Financial Assistance & Scholarships",
        "url": "https://www.iitb.ac.in/en/academics/scholarships-and-awards",
        "category": "University"
    },
    {
        "name": "Delhi University Financial Support Scheme (FSS)",
        "url": "https://www.du.ac.in",
        "category": "University"
    },
    {
        "name": "Vidyasaarathi Portal (Protean CSR)",
        "url": "https://www.vidyasaarathi.co.in",
        "category": "Foundation/Trust"
    }
]

# Filtering patterns
SCHOLARSHIP_KEYWORDS = [
    "scholarship", "scheme", "fellowship", "grant", "financial-aid",
    "pragati", "saksham", "swanath", "post-matric", "pre-matric",
    "parivartan", "merit", "assistance", "yojana"
]

EXCLUDE_PATTERNS = [
    "login", "signup", "contact", "about-us", "privacy", "disclaimer",
    "terms", "sitemap", "feedback", "faq", "javascript", "mailto", "tel"
]

class DiscoveryEngine:
    def __init__(self, fetcher: WebFetcher = None):
        self.fetcher = fetcher or WebFetcher()

    def is_candidate_link(self, url: str, anchor_text: str) -> bool:
        """Determines if a link represents a potential scholarship opportunity."""
        combined = f"{url.lower()} {anchor_text.lower()}"
        
        # Check exclusion
        for excl in EXCLUDE_PATTERNS:
            if excl in combined:
                return False
                
        # Check if contains any scholarship indicator
        for kw in SCHOLARSHIP_KEYWORDS:
            if kw in combined:
                return True
        return False

    def discover_from_seed(self, seed_url: str) -> List[Dict[str, Any]]:
        """
        Crawls a seed portal and discovers potential scholarship announcement links.
        Classifies each candidate by source authority.
        """
        logger.info(f"Crawling seed portal: {seed_url}")
        page_data = self.fetcher.fetch_page(seed_url)
        if not page_data or not page_data.get("success"):
            logger.warning(f"Unable to crawl seed {seed_url}")
            return []

        candidates = []
        seen_urls: Set[str] = set()

        for link_obj in page_data.get("links", []):
            url = link_obj["url"]
            anchor = link_obj["anchor_text"]

            if url in seen_urls:
                continue

            if self.is_candidate_link(url, anchor):
                seen_urls.add(url)
                classification = classify_source(url)

                candidates.append({
                    "discovered_url": url,
                    "anchor_text": anchor,
                    "seed_source": seed_url,
                    "source_type": classification["source_type"],
                    "provider_guess": classification["provider_guess"],
                    "is_official": classification["is_official"],
                    "domain_authority_score": classification["domain_authority_score"]
                })

        logger.info(f"Discovered {len(candidates)} candidate links from {seed_url}")
        return candidates

    def run_discovery_pipeline(self) -> List[Dict[str, Any]]:
        """Runs discovery across all defined primary seed portals."""
        all_candidates = []
        for seed in SEED_PORTALS:
            discovered = self.discover_from_seed(seed["url"])
            all_candidates.extend(discovered)
        return all_candidates

