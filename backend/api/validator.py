"""
validator.py — Validates and sanitizes Gemini's personalization output.
"""
import re
import logging

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    'new_headline',
    'new_subheadline',
    'new_cta_text',
    'new_hero_description',
    'reasoning',
]

MAX_LENGTHS = {
    'new_headline': 120,
    'new_subheadline': 200,
    'new_cta_text': 60,
    'new_hero_description': 500,
    'new_social_proof': 300,
}

# Patterns that indicate hallucinated or broken content
INVALID_PATTERNS = [
    r'<script',
    r'javascript:',
    r'{{.*?}}',  # Template variables leaked
    r'\[PLACEHOLDER\]',
    r'INSERT_',
    r'TODO:',
    r'FIXME:',
]


def validate_personalization(data: dict, original_page: dict) -> tuple[bool, dict, list]:
    """
    Validates Gemini's personalization output.

    Returns:
        (is_valid, cleaned_data, errors)

    - If a field is invalid, falls back to the original page value.
    - Never returns empty critical fields.
    """
    errors = []
    cleaned = {}

    for field in REQUIRED_FIELDS:
        if field == 'reasoning':
            # Reasoning is a dict, handle separately
            raw_reasoning = data.get('reasoning', {})
            if not isinstance(raw_reasoning, dict):
                raw_reasoning = {}
            cleaned['reasoning'] = raw_reasoning
            continue

        raw_value = data.get(field, '').strip()

        # Check for empty
        if not raw_value:
            errors.append(f"Field '{field}' is empty.")
            raw_value = _get_fallback(field, original_page)

        # Check for invalid patterns
        for pattern in INVALID_PATTERNS:
            if re.search(pattern, raw_value, re.IGNORECASE):
                errors.append(f"Field '{field}' contains invalid pattern: {pattern}")
                raw_value = _get_fallback(field, original_page)
                break

        # Enforce max length
        max_len = MAX_LENGTHS.get(field, 500)
        if len(raw_value) > max_len:
            raw_value = raw_value[:max_len].rsplit(' ', 1)[0] + '...'
            errors.append(f"Field '{field}' was truncated to {max_len} chars.")

        # Sanitize HTML tags from copy fields
        raw_value = _strip_html_tags(raw_value)

        cleaned[field] = raw_value

    # Handle optional social proof
    social_proof = data.get('new_social_proof', '').strip()
    if social_proof and len(social_proof) <= MAX_LENGTHS['new_social_proof']:
        cleaned['new_social_proof'] = _strip_html_tags(social_proof)
    else:
        cleaned['new_social_proof'] = ""

    is_valid = len(errors) == 0
    if errors:
        logger.warning(f"Validation issues (using fallbacks): {errors}")

    return is_valid, cleaned, errors


def _strip_html_tags(text: str) -> str:
    """Remove HTML tags from text, keeping content."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()


def _get_fallback(field: str, original_page: dict) -> str:
    """Returns the original page value as fallback for a field."""
    fallbacks = {
        'new_headline': original_page.get('headline', 'Welcome'),
        'new_subheadline': original_page.get('subheadline', ''),
        'new_cta_text': original_page.get('cta_text', 'Get Started'),
        'new_hero_description': original_page.get('hero_text', ''),
    }
    return fallbacks.get(field, '')
