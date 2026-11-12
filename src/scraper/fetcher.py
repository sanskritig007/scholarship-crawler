"""
Web Scraping & Safe Fetcher Module
Resilient HTTP client using requests if installed, with standard library urllib fallback.
Parses HTML content, extracts text, anchors, and metadata safely.
"""
import re
import ssl
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse

try:
    import requests
    # pyrefly: ignore[missing-import]
    from bs4 import BeautifulSoup
    HAS_EXTERNAL_SCRAPING_LIBS = True
except ImportError:
    import urllib.request
    from html.parser import HTMLParser
    HAS_EXTERNAL_SCRAPING_LIBS = False

from src.config import DEFAULT_HEADERS, REQUEST_TIMEOUT_SECONDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleHTMLTextAndLinkExtractor:
    """Standard library HTML parser fallback when BeautifulSoup is not yet installed."""
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.links: List[Dict[str, str]] = []
        self.text_chunks: List[str] = []

    def feed(self, html_content: str):
        clean_html = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)

        for match in re.finditer(r'<a\s+(?:[^>]*?\s+)?href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', clean_html, flags=re.DOTALL | re.IGNORECASE):
            href, anchor = match.groups()
            anchor_clean = re.sub(r"<[^>]+>", " ", anchor).strip()
            if href and not href.startswith("javascript:") and not href.startswith("#"):
                full_url = urljoin(self.base_url, href.strip())
                self.links.append({
                    "url": full_url,
                    "anchor_text": anchor_clean
                })

        text_without_tags = re.sub(r"<[^>]+>", " ", clean_html)
        text_without_tags = re.sub(r"\s+", " ", text_without_tags).strip()
        self.text_chunks = [text_without_tags]

class WebFetcher:
    def __init__(self, timeout: int = REQUEST_TIMEOUT_SECONDS):
        self.timeout = timeout
        if HAS_EXTERNAL_SCRAPING_LIBS:
            self.session = requests.Session()
            self.session.headers.update(DEFAULT_HEADERS)
        else:
            self.session = None

    def fetch_page(self, url: str) -> Dict[str, Any]:
        """Fetches a URL and parses its HTML content."""
        if HAS_EXTERNAL_SCRAPING_LIBS:
            return self._fetch_with_requests(url)
        else:
            return self._fetch_with_urllib(url)

    def _fetch_with_requests(self, url: str) -> Dict[str, Any]:
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True, verify=False)
            if resp.status_code != 200:
                return {"url": url, "status_code": resp.status_code, "success": False, "title": "", "text": "", "links": [], "html": ""}

            soup = BeautifulSoup(resp.content, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "iframe"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            extracted_links = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                anchor_text = a_tag.get_text(strip=True)
                if not href or href.startswith("javascript:") or href.startswith("#"):
                    continue
                extracted_links.append({"url": urljoin(url, href), "anchor_text": anchor_text})

            content_blocks = [elem.get_text(strip=True) for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "td", "th"])]
            full_text = re.sub(r"[ \t]+", " ", "\n".join([t for t in content_blocks if len(t) > 3]))

            return {
                "url": resp.url,
                "status_code": 200,
                "success": True,
                "title": title,
                "text": full_text,
                "links": extracted_links,
                "html": resp.text
            }
        except Exception as e:
            return {"url": url, "status_code": 500, "success": False, "title": "", "text": "", "links": [], "error": str(e), "html": ""}

    def _fetch_with_urllib(self, url: str) -> Dict[str, Any]:
        try:
            req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                status_code = response.getcode()
                final_url = response.geturl()
                html_bytes = response.read()
                html_text = html_bytes.decode("utf-8", errors="replace")

                title_match = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else ""

                parser = SimpleHTMLTextAndLinkExtractor(final_url)
                parser.feed(html_text)

                return {
                    "url": final_url,
                    "status_code": status_code,
                    "success": True,
                    "title": title,
                    "text": parser.text_chunks[0] if parser.text_chunks else "",
                    "links": parser.links,
                    "html": html_text
                }
        except Exception as e:
            return {"url": url, "status_code": 500, "success": False, "title": "", "text": "", "links": [], "error": str(e), "html": ""}

    def verify_url_alive(self, url: str) -> bool:
        """Lightweight check to see if an application URL is reachable."""
        try:
            req = urllib.request.Request(url, headers=DEFAULT_HEADERS, method="HEAD")
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                return resp.getcode() in [200, 301, 302, 307, 308]
        except Exception:
            return False
