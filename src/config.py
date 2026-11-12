"""
System Configuration & Constants
Defines thresholds, paths, allowed statuses, and source classifications.
"""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "scholarships.db"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Verification & Scoring Thresholds (per PDF requirements)
# A scholarship is only labelled VERIFIED if confidence is 95% or above.
VERIFIED_CONFIDENCE_THRESHOLD = 95.0

# Allowed Statuses (per Section 8 & 9 of Assignment PDF)
STATUS_ACTIVE = "ACTIVE"
STATUS_EXPIRING_SOON = "EXPIRING_SOON"
STATUS_EXPIRED = "EXPIRED"
STATUS_REVIEW_REQUIRED = "REVIEW_REQUIRED"
STATUS_NO_LONGER_VERIFIABLE = "NO_LONGER_VERIFIABLE"

VALID_STATUSES = [
    STATUS_ACTIVE,
    STATUS_EXPIRING_SOON,
    STATUS_EXPIRED,
    STATUS_REVIEW_REQUIRED,
    STATUS_NO_LONGER_VERIFIABLE,
]

# Source Classifications
SOURCE_GOVERNMENT = "Government"
SOURCE_CORPORATE_CSR = "Corporate CSR"
SOURCE_UNIVERSITY = "University"
SOURCE_FOUNDATION = "Foundation/Trust"

VALID_SOURCE_TYPES = [
    SOURCE_GOVERNMENT,
    SOURCE_CORPORATE_CSR,
    SOURCE_UNIVERSITY,
    SOURCE_FOUNDATION,
]

# HTTP Crawl Settings (Free & Responsible Crawling)
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
}

REQUEST_TIMEOUT_SECONDS = 15

