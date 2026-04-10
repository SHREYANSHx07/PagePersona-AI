"""
cro_personalizer.py — Generates CRO-optimized personalized copy using Gemini.
Uses the new google-genai SDK.
"""
import json
import logging
from google import genai
from google.genai import types
from django.conf import settings
from .validator import validate_personalization
from .gemini_json import parse_json_from_model_text

logger = logging.getLogger(__name__)


def build_personalization_prompt(ad_analysis: dict, scraped_page: dict) -> str:
    return f"""
You are a world-class Conversion Rate Optimization (CRO) expert and copywriter.

Your task: Personalize an existing landing page to match the messaging, tone, and audience of a specific ad creative.

## AD CREATIVE ANALYSIS:
- Core Message: {ad_analysis.get('core_message', 'N/A')}
- Target Audience: {ad_analysis.get('target_audience', 'N/A')}
- Emotional Tone: {ad_analysis.get('emotional_tone', 'N/A')}
- CTA in Ad: {ad_analysis.get('cta_text', 'N/A')}
- Offer/Details: {ad_analysis.get('offer_details', 'N/A')}
- Key Benefits: {', '.join(ad_analysis.get('key_benefits', []))}
- Brand Personality: {ad_analysis.get('brand_personality', 'N/A')}
- Pain Point Addressed: {ad_analysis.get('pain_point_addressed', 'N/A')}
- Visual Style: {ad_analysis.get('visual_style', 'N/A')}

## CURRENT LANDING PAGE CONTENT:
- Current Headline: {scraped_page.get('headline', 'N/A')}
- Current Subheadline: {scraped_page.get('subheadline', 'N/A')}
- Current CTA: {scraped_page.get('cta_text', 'N/A')}
- Current Hero Text: {scraped_page.get('hero_text', 'N/A')}
- Meta Description: {scraped_page.get('meta_description', 'N/A')}
- Page Body Preview: {scraped_page.get('body_text', '')[:500]}

## YOUR TASK:
Generate personalized copy that:
1. Matches the MESSAGE SCENT from the ad (visitor sees consistent messaging)
2. Addresses the SAME PAIN POINT the ad promises to solve
3. Uses the SAME EMOTIONAL TONE as the ad
4. Has a CTA that follows through on the ad's promise
5. Adds social proof that reinforces the ad's credibility
6. Applies CRO best practices (clarity, urgency, specificity, value-first)

Return ONLY a valid JSON object (no markdown, no code blocks):

{{
  "new_headline": "Compelling headline that matches the ad's core promise (max 80 chars)",
  "new_subheadline": "Supporting headline that elaborates on the promise (max 150 chars)",
  "new_cta_text": "Action-oriented CTA button text (max 40 chars)",
  "new_hero_description": "Hero section description that speaks to the target audience's pain point (max 300 chars)",
  "new_social_proof": "A credibility statement or testimonial snippet (max 200 chars)",
  "reasoning": {{
    "headline": "Why this headline works better for message scent and CRO",
    "subheadline": "Why this subheadline improves comprehension",
    "cta": "Why this CTA improves conversion intent",
    "hero_description": "Why this description resonates with the ad audience",
    "social_proof": "Why this social proof builds trust for this specific audience"
  }}
}}

Be specific, persuasive, and ensure every word earns its place.
"""


def personalize_landing_page(ad_analysis: dict, scraped_page: dict) -> dict:
    """
    Generates personalized copy for a landing page based on ad analysis.
    """
    result = {
        "success": False,
        "new_headline": "",
        "new_subheadline": "",
        "new_cta_text": "",
        "new_hero_description": "",
        "new_social_proof": "",
        "reasoning": {},
        "validation_warnings": [],
        "error": None,
    }

    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key or api_key == 'your_gemini_api_key_here':
            result['error'] = "Gemini API key not configured."
            return result

        client = genai.Client(api_key=api_key)

        prompt = build_personalization_prompt(ad_analysis, scraped_page)

        model_id = settings.GEMINI_MODEL
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )

        raw_text = (response.text or "").strip()
        if not raw_text:
            result["error"] = "Empty response from Gemini. Check GEMINI_MODEL and API quota."
            return result

        parsed = parse_json_from_model_text(raw_text)

        # Validate output
        is_valid, cleaned, warnings = validate_personalization(parsed, scraped_page)

        result.update({
            "success": True,
            "new_headline": cleaned.get('new_headline', ''),
            "new_subheadline": cleaned.get('new_subheadline', ''),
            "new_cta_text": cleaned.get('new_cta_text', ''),
            "new_hero_description": cleaned.get('new_hero_description', ''),
            "new_social_proof": cleaned.get('new_social_proof', ''),
            "reasoning": cleaned.get('reasoning', {}),
            "validation_warnings": warnings,
        })

        logger.info(f"Personalization complete. Valid: {is_valid}. Warnings: {len(warnings)}")

    except json.JSONDecodeError as e:
        result['error'] = f"Failed to parse Gemini's personalization response: {str(e)}"
        logger.error(f"JSON parse error in cro_personalizer: {e}")
    except Exception as e:
        result['error'] = f"Error during personalization: {str(e)}"
        logger.error(f"Error in personalize_landing_page: {e}", exc_info=True)

    return result
