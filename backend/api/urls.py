"""
api/urls.py — URL routing for the API app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('scrape-page/', views.scrape_page, name='scrape_page'),
    path('analyze-ad/', views.analyze_ad_creative, name='analyze_ad'),
    path('personalize/', views.personalize, name='personalize'),
]
