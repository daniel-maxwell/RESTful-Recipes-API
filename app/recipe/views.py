"""
Views for the Recipe API
"""

from core.models import Recipe, Ingredient, Tag
from recipe import serializers

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)


@extend_schema_view(
    list=extend_schema(
        description="Get a list of recipes",
        parameters=[
            OpenApiParameter(
                name='ingredients',
                type=OpenApiTypes.STR,
                description='Comma-seperated list of ingredient IDs to filter by',
            ),
            OpenApiParameter(
                name='tags',
                type=OpenApiTypes.STR,
                description='Comma-seperated list of tag IDs to filter by',
            ),
        ],
    ),
)
class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for managing the Recipe model"""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return recipes for the authenticated user only"""
        # Get query parameters called 'ingredients' and 'tags'
        ingredients = self.request.query_params.get('ingredients')
        tags = self.request.query_params.get('tags')

        # Get a reference to the queryset
        qs = self.queryset

        # Filter the queryset based on the query parameters
        if ingredients:
            ingredientIds = self._list_str_to_list_int(ingredients)
            qs = qs.filter(ingredients__id__in=ingredientIds)
        if tags:
            tagIds = self._list_str_to_list_int(tags)
            qs = qs.filter(tags__id__in=tagIds)

        # Return the filtered queryset
        return qs.filter(
            user=self.request.user
        ).order_by('-id').distinct()


    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    def _list_str_to_list_int(self, query_params):
        """Cast a list of strings to a list of integers"""
        return [int(id) for id in query_params.split(',')]


@extend_schema_view(
    list=extend_schema(
        description="Get a list of ingredients",
        parameters=[
            OpenApiParameter(
                name='assigned_only',
                type=OpenApiTypes.INT, enum=[0, 1],
                description='Filter to only return assigned ingredients',
            ),
        ],
    ),
)
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        qs = self.queryset
        if assigned_only: qs = qs.filter(recipe__isnull=False)
        return qs.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        description="Get a list of tags",
        parameters=[
            OpenApiParameter(
                name='assigned_only',
                type=OpenApiTypes.INT, enum=[0, 1],
                description='Filter to only return assigned tags',
            ),
        ],
    ),
)
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        qs = self.queryset
        if assigned_only: qs = qs.filter(recipe__isnull=False)
        return qs.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)
