"""
Serializers for recipe APIs
"""
from rest_framework import serializers
from core.models import Recipe, Ingredient, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model"""

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for the Ingredient model"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe model"""

    ingredients = IngredientSerializer(many=True, required=False)
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'ingredients',
            'tags',
        )
        read_only_fields = ('id',)

    # Override the create method to handle ingredients and tags
    def create(self, validated_data):
        '''Create a recipe, handle tag retrieval or creation'''
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_ingredients(ingredients_data, recipe)
        self._get_or_create_tags(tags_data, recipe)
        return recipe

    # Override the update method to handle ingedients and tags
    def update(self, instance, validated_data):
        '''Update a recipe, handle tag retrieval or creation'''

        # Remove ingredients and tags from validated data
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)

        # If ingredients / tags information was provided,
        # clear the existing ingredients and tags
        # and get or create the new ingredients / tags
        if ingredients_data is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients_data, instance)

        if tags_data is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags_data, instance)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()
        return instance

    def _get_or_create_ingredients(self, ingredients_data, recipe):
        '''Either gets or creates ingredients if they don't exist'''
        for ingredient_data in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                user=self.context['request'].user,
                name=ingredient_data['name']
            )
            recipe.ingredients.add(ingredient)

    #
    def _get_or_create_tags(self, tags_data, recipe):
        '''Either gets or creates tags if they don't exist'''
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                user=self.context['request'].user,
                name=tag_data['name']
            )
            recipe.tags.add(tag)


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the RecipeDetail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + (
            'description',
        )

        read_only_fields = ('id',)
