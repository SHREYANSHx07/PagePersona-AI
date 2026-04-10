"""
views.py — Django REST API views for the AI Landing Page Personalizer.

Endpoints:
  POST /api/scrape-page/
  POST /api/analyze-ad/
  POST /api/personalize/
  GET  /api/health/
"""
import logging
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

from .page_scraper import scrape_landing_page
from .ad_analyzer import analyze_ad
from .cro_personalizer import personalize_landing_page
from .html_injector import inject_personalization

logger = logging.getLogger(__name__)


@api_view(['GET'])
def health_check(request):
    """Health check endpoint."""
    return Response({"status": "ok", "message": "AI Landing Page Personalizer API is running."})


@api_view(['POST'])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def scrape_page(request):
    """
    Scrapes a landing page and returns structured content.

    Body: { "url": "https://example.com" }
    """
    url = request.data.get('url', '').strip()

    if not url:
        return Response(
            {"error": "URL is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    logger.info(f"Scraping page: {url}")
    result = scrape_landing_page(url)

    if not result['success']:
        return Response(
            {"error": result.get('error', 'Failed to scrape page.'), "partial": result},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def analyze_ad_creative(request):
    """
    Analyzes an ad creative image using Gemini Vision.

    Body (multipart): image file in 'image' field
    Body (JSON): { "image_url": "https://..." }
    """
    image_file = request.FILES.get('image')
    image_url = request.data.get('image_url', '').strip()

    if not image_file and not image_url:
        return Response(
            {"error": "Either an image file or image_url is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    image_data = None
    if image_file:
        image_data = image_file.read()
        logger.info(f"Analyzing uploaded image: {image_file.name} ({len(image_data)} bytes)")
    else:
        logger.info(f"Analyzing image from URL: {image_url}")

    result = analyze_ad(image_data=image_data, image_url=image_url or None)

    if not result['success']:
        return Response(
            {"error": result.get('error', 'Failed to analyze ad.')},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def personalize(request):
    """
    Full orchestration endpoint: takes ad image + landing page URL,
    returns personalized HTML + change log.

    Body (multipart):
        - image: (file, optional)
        - image_url: string (optional)
        - landing_page_url: string (required)
    """
    landing_page_url = request.data.get('landing_page_url', '').strip()
    image_file = request.FILES.get('image')
    image_url = request.data.get('image_url', '').strip()

    if not landing_page_url:
        return Response(
            {"error": "landing_page_url is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not image_file and not image_url:
        return Response(
            {"error": "Either an image file or image_url is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not landing_page_url.startswith(('http://', 'https://')):
        landing_page_url = 'https://' + landing_page_url

    # --- Step 1: Scrape landing page ---
    logger.info(f"[Personalize] Step 1: Scraping {landing_page_url}")
    scraped = scrape_landing_page(landing_page_url)

    if not scraped['success']:
        return Response(
            {
                "error": f"Could not scrape the landing page: {scraped.get('error', 'Unknown error')}",
                "step": "scraping"
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # --- Step 2: Analyze ad creative ---
    logger.info("[Personalize] Step 2: Analyzing ad creative")
    image_data = image_file.read() if image_file else None
    ad_analysis = analyze_ad(image_data=image_data, image_url=image_url or None)

    if not ad_analysis['success']:
        return Response(
            {
                "error": f"Could not analyze the ad: {ad_analysis.get('error', 'Unknown error')}",
                "step": "ad_analysis"
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # --- Step 3: Generate personalization ---
    logger.info("[Personalize] Step 3: Generating personalized copy")
    personalization = personalize_landing_page(ad_analysis, scraped)

    if not personalization['success']:
        return Response(
            {
                "error": f"Could not personalize: {personalization.get('error', 'Unknown error')}",
                "step": "personalization"
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    # --- Step 4: Inject into HTML ---
    logger.info("[Personalize] Step 4: Injecting changes into HTML")
    personalized_html, change_log = inject_personalization(
        scraped['full_html'],
        personalization
    )

    response_data = {
        "success": True,
        "landing_page_url": landing_page_url,
        "personalized_html": personalized_html,
        "original_html": scraped['full_html'],
        "change_log": change_log,
        "ad_analysis": ad_analysis,
        "page_data": {
            "headline": scraped.get('headline', ''),
            "subheadline": scraped.get('subheadline', ''),
            "cta_text": scraped.get('cta_text', ''),
            "hero_text": scraped.get('hero_text', ''),
        },
        "personalization": {
            "new_headline": personalization.get('new_headline', ''),
            "new_subheadline": personalization.get('new_subheadline', ''),
            "new_cta_text": personalization.get('new_cta_text', ''),
            "new_hero_description": personalization.get('new_hero_description', ''),
            "new_social_proof": personalization.get('new_social_proof', ''),
            "reasoning": personalization.get('reasoning', {}),
        },
        "validation_warnings": personalization.get('validation_warnings', []),
        "changes_count": len(change_log),
    }

    logger.info(f"[Personalize] Done. {len(change_log)} changes applied.")
    return Response(response_data, status=status.HTTP_200_OK)
