"""
page_scraper.py — Scrapes a landing page URL and extracts structured content.
"""
import requests
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}


def scrape_landing_page(url: str) -> dict:
    """
    Scrapes a landing page and returns structured content.

    Returns:
        {
            "success": bool,
            "url": str,
            "headline": str,
            "subheadline": str,
            "cta_text": str,
            "meta_description": str,
            "hero_text": str,
            "body_text": str,
            "full_html": str,
            "error": str | None
        }
    """
    result = {
        "success": False,
        "url": url,
        "headline": "",
        "subheadline": "",
        "cta_text": "",
        "meta_description": "",
        "hero_text": "",
        "body_text": "",
        "full_html": "",
        "error": None,
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style tags for text extraction
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        # --- Headline ---
        h1 = soup.find('h1')
        result['headline'] = _clean_text(h1.get_text()) if h1 else ""

        # --- Subheadline ---
        h2 = soup.find('h2')
        result['subheadline'] = _clean_text(h2.get_text()) if h2 else ""

        # --- Meta description ---
        meta = soup.find('meta', attrs={'name': 'description'}) or \
               soup.find('meta', attrs={'property': 'og:description'})
        if meta and meta.get('content'):
            result['meta_description'] = meta['content'].strip()

        # --- CTA buttons ---
        cta = _find_cta(soup)
        result['cta_text'] = cta

        # --- Hero section text ---
        hero_text = _find_hero_text(soup)
        result['hero_text'] = hero_text

        # --- Body text (first 2000 chars) ---
        body_text = soup.get_text(separator=' ', strip=True)
        result['body_text'] = ' '.join(body_text.split())[:2000]

        # --- Full HTML (original, unmodified) ---
        # Re-parse to get original with scripts intact
        result['full_html'] = html

        result['success'] = True
        logger.info(f"Successfully scraped {url}")

    except requests.exceptions.Timeout:
        result['error'] = "Request timed out. The page took too long to respond."
        logger.error(f"Timeout scraping {url}")
    except requests.exceptions.SSLError:
        result['error'] = "SSL certificate error. Cannot securely connect to the page."
        logger.error(f"SSL error scraping {url}")
    except requests.exceptions.ConnectionError:
        result['error'] = "Could not connect to the URL. Please check the URL is correct."
        logger.error(f"Connection error scraping {url}")
    except requests.exceptions.HTTPError as e:
        result['error'] = f"HTTP error {e.response.status_code}: {e.response.reason}"
        logger.error(f"HTTP error scraping {url}: {e}")
    except Exception as e:
        result['error'] = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error scraping {url}: {e}")

    return result


def _clean_text(text: str) -> str:
    """Clean up extracted text."""
    return ' '.join(text.split()).strip()


def _find_cta(soup: BeautifulSoup) -> str:
    """Find the primary CTA button text."""
    # Priority: buttons with common CTA words, then any button, then links
    cta_keywords = [
        'get started', 'start', 'try', 'sign up', 'signup', 'register',
        'buy', 'shop', 'order', 'book', 'schedule', 'request', 'download',
        'free', 'learn more', 'get', 'join', 'subscribe', 'contact', 'demo'
    ]

    # Check buttons first
    buttons = soup.find_all(['button', 'a'], class_=re.compile(r'btn|button|cta', re.I))
    for btn in buttons:
        text = _clean_text(btn.get_text())
        if text and len(text) < 60:
            return text

    # Check for buttons with CTA keywords
    all_buttons = soup.find_all('button')
    all_buttons += soup.find_all('a', href=True)

    for btn in all_buttons:
        text = _clean_text(btn.get_text())
        if text and any(kw in text.lower() for kw in cta_keywords):
            return text

    # Fallback: first button text
    first_btn = soup.find('button')
    if first_btn:
        return _clean_text(first_btn.get_text())

    return "Get Started"


def _find_hero_text(soup: BeautifulSoup) -> str:
    """Find the hero section description text."""
    # Look for hero/banner sections
    hero_selectors = [
        {'class': re.compile(r'hero|banner|jumbotron|intro|landing', re.I)},
        {'id': re.compile(r'hero|banner|home|intro', re.I)},
    ]

    for selector in hero_selectors:
        hero = soup.find(['section', 'div', 'header'], attrs=selector)
        if hero:
            # Get paragraph text within hero
            p = hero.find('p')
            if p:
                return _clean_text(p.get_text())

    # Fallback: first meaningful paragraph after h1
    h1 = soup.find('h1')
    if h1:
        # Look for next sibling paragraph
        for sibling in h1.find_next_siblings():
            if sibling.name == 'p':
                text = _clean_text(sibling.get_text())
                if len(text) > 20:
                    return text

    # Last resort: first paragraph with meaningful content
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = _clean_text(p.get_text())
        if len(text) > 30:
            return text[:300]

    return ""
