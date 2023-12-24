"""
Serializers for recipe APIs
"""
from rest_framework import serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model"""

    class Meta:
        model = Tag
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the Recipe model"""

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags',
        )
        read_only_fields = ('id',)

    # Override the create method to handle recipe tags
    def create(self, validated_data):
        '''Create a recipe, handle tag retrieval or creation'''
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags_data, recipe)
        return recipe

    # Override the update method to handle recipe tags
    def update(self, instance, validated_data):
        '''Update a recipe, handle tag retrieval or creation'''
        tags_data = validated_data.pop('tags', None)
        if tags_data is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags_data, instance)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)
        instance.save()
        return instance

    # Helper method either gets or creates tags if they don't exist
    def _get_or_create_tags(self, tags_data, recipe):
        '''Get or create tags for a recipe'''
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
