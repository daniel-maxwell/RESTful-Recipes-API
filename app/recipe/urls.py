"""
URL mappings for the recipes API
"""
from recipe import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create a router
router = DefaultRouter()

# Register the recipe viewset with the router
router.register('recipes', views.RecipeViewSet)

# Define the app name
app_name = 'recipe'

# Define the URL patterns
urlpatterns = [
    path('', include(router.urls))
]
