"""
Views for the Recipe API
"""

from core.models import Recipe, Ingredient, Tag
from recipe import serializers

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for managing the Recipe model"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return recipes for the authenticated user only"""
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-id')  # Order by id (most recent first)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)


class IngredientViewSet(viewsets.GenericViewSet,
                        mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin):
    """Viewset for managing the Ingredient model"""
    serializer_class = serializers.IngredientSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        """Return ingredients for the authenticated user only"""
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')  # Order by name in descending order

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.GenericViewSet,
                 mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin):
    """Viewset for managing the Tag model"""
    serializer_class = serializers.TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()

    def get_queryset(self):
        """Return tags for the authenticated user only"""
        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')  # Order by name in descending order

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)
