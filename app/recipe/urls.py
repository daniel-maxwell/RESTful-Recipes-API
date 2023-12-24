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

# Register the ingredient viewset with the router
router.register('ingredients', views.IngredientViewSet)

# Register the tag viewset with the router
router.register('tags', views.TagViewSet)

# Define the app name
app_name = 'recipe'

# Define the URL patterns
urlpatterns = [
    path('', include(router.urls))
]
