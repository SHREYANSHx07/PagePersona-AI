"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def root(request):
    """Root URL — API-only backend; points callers to /api/."""
    return JsonResponse(
        {
            "service": "PagePersona / AI Landing Page Personalizer API",
            "health": "/api/health/",
            "endpoints": {
                "scrape_page": "POST /api/scrape-page/",
                "analyze_ad": "POST /api/analyze-ad/",
                "personalize": "POST /api/personalize/",
            },
            "ui": "Run the Vite frontend (e.g. http://localhost:5173) for the full app.",
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root),
    path("api/", include("api.urls")),
]
