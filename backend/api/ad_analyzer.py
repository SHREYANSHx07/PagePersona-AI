"""
ad_analyzer.py — Analyzes ad creative images with Gemini vision (model from settings.GEMINI_MODEL).
Uses the google-genai SDK.
"""
import io
import json
import logging
import requests as req_lib
from PIL import Image
from google import genai
from google.genai import types
from django.conf import settings

from .gemini_json import parse_json_from_model_text

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """
You are an expert marketing analyst and CRO specialist. Analyze this ad creative image in detail.

Return ONLY a valid JSON object with exactly these fields (no markdown, no code blocks, just raw JSON):

{
  "core_message": "The single most important message/promise this ad communicates",
  "target_audience": "Who this ad is targeting (demographics, psychographics, pain points)",
  "emotional_tone": "The emotional feeling this ad evokes (e.g., urgency, aspirational, trust, playful)",
  "cta_text": "The call-to-action text visible in the ad (or inferred if not visible)",
  "offer_details": "Any specific offer, discount, promotion, or value proposition mentioned",
  "key_benefits": ["benefit 1", "benefit 2", "benefit 3"],
  "color_palette": "Description of the dominant colors and their psychological effect",
  "visual_style": "The visual style of the ad (minimalist, bold, lifestyle, product-focused, etc.)",
  "brand_personality": "The brand personality communicated (professional, fun, luxury, approachable, etc.)",
  "pain_point_addressed": "The customer pain point or need this ad addresses"
}

Be specific and insightful. If the image doesn't contain text, infer from visual cues.
"""


def analyze_ad(image_data: bytes = None, image_url: str = None) -> dict:
    """
    Analyzes an ad creative image using Gemini Vision.

    Args:
        image_data: Raw image bytes (from file upload)
        image_url: URL of the image to analyze

    Returns:
        {
            "success": bool,
            "core_message": str,
            "target_audience": str,
            "emotional_tone": str,
            "cta_text": str,
            "offer_details": str,
            "key_benefits": list,
            "color_palette": str,
            "visual_style": str,
            "brand_personality": str,
            "pain_point_addressed": str,
            "error": str | None
        }
    """
    result = {
        "success": False,
        "core_message": "",
        "target_audience": "",
        "emotional_tone": "",
        "cta_text": "",
        "offer_details": "",
        "key_benefits": [],
        "color_palette": "",
        "visual_style": "",
        "brand_personality": "",
        "pain_point_addressed": "",
        "error": None,
    }

    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key == 'your_gemini_api_key_here':
            result['error'] = "Gemini API key not configured. Please set GEMINI_API_KEY in .env"
            return result

        # Initialize client with new SDK
        client = genai.Client(api_key=api_key)

        # Get image bytes
        if image_data:
            img_bytes = image_data
        elif image_url:
            img_bytes = _fetch_image_from_url(image_url)
            if not img_bytes:
                result['error'] = "Could not fetch image from the provided URL."
                return result
        else:
            result['error'] = "No image data or URL provided."
            return result

        # Process image with Pillow
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')

        output = io.BytesIO()
        img.save(output, format='PNG', optimize=True)
        processed_bytes = output.getvalue()

        # Build content parts for new SDK
        image_part = types.Part.from_bytes(
            data=processed_bytes,
            mime_type="image/png"
        )

        model_id = settings.GEMINI_MODEL
        response = client.models.generate_content(
            model=model_id,
            contents=[ANALYSIS_PROMPT, image_part],
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1024,
            )
        )

        raw_text = (response.text or "").strip()
        if not raw_text:
            result["error"] = "Empty response from Gemini. Try another image or set GEMINI_MODEL in .env."
            return result

        parsed = parse_json_from_model_text(raw_text)

        result.update({
            "success": True,
            "core_message": parsed.get("core_message", ""),
            "target_audience": parsed.get("target_audience", ""),
            "emotional_tone": parsed.get("emotional_tone", ""),
            "cta_text": parsed.get("cta_text", ""),
            "offer_details": parsed.get("offer_details", ""),
            "key_benefits": parsed.get("key_benefits", []),
            "color_palette": parsed.get("color_palette", ""),
            "visual_style": parsed.get("visual_style", ""),
            "brand_personality": parsed.get("brand_personality", ""),
            "pain_point_addressed": parsed.get("pain_point_addressed", ""),
        })

        logger.info("Ad analysis completed successfully")

    except json.JSONDecodeError as e:
        result['error'] = f"Failed to parse Gemini's response as JSON: {str(e)}"
        logger.error(f"JSON parse error in ad_analyzer: {e}")
    except Exception as e:
        result['error'] = f"Error analyzing ad: {str(e)}"
        logger.error(f"Error in analyze_ad: {e}", exc_info=True)

    return result


def _fetch_image_from_url(url: str) -> bytes | None:
    """Fetches image bytes from a URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = req_lib.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Error fetching image from URL {url}: {e}")
        return None
