from rest_framework import serializers

from foods.models import Recipe


class RecipeShortReadSerializer(serializers.ModelSerializer):
    """Сериализатор короткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
