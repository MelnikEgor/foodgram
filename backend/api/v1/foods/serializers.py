from django.contrib.auth import get_user_model
from rest_framework import serializers

from .utils import add_ingredients
from api.v1.fields import Base64ImageField
from api.v1.users.serializers import UserReadSerializer
from api.v1.utils import check_field
from foods.models import Ingredient, IngredientRecipe, Recipe, Tag


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов для рецепта."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов для рецепта."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientFromRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в составе рецепта"""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиентов должно быть меньше 1.'
            )
        return value

    def validate(self, data):
        errors = {}
        error_message = 'Обязательное поле.'
        amount = data.get('amount', None)
        ingredient = data.get('ingredient', None)

        if amount is None:
            errors['amount'] = error_message
        if ingredient is None:
            errors['id'] = error_message

        if errors:
            raise serializers.ValidationError(errors)
        return data


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    author = UserReadSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientFromRecipeSerializer(
        many=True,
        source='ingredientrecipe_set',
        allow_empty=False
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        obj = obj.favorites.all()
        return check_field(self, obj)

    def get_is_in_shopping_cart(self, obj):
        obj = obj.shopping_carts.all()
        return check_field(self, obj)


class RecipeWriteSerializer(RecipeReadSerializer):
    """Сериализатор рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        allow_empty=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Нельзя добавить один тег несколько раз.'
            )
        return value

    def validate_ingredients(self, value):
        ingredient_ids = [
            ingredient['ingredient'].id for ingredient in value
        ]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Нельзя добавить один ингредиент несколько раз.'
            )
        return value

    def validate(self, data):
        errors = {}
        error_message = 'Обязательное поле.'
        ingredients = data.get('ingredientrecipe_set', None)
        tags = data.get('tags', None)
        name = data.get('name', None)
        text = data.get('text', None)
        cooking_time = data.get('cooking_time', None)

        if ingredients is None:
            errors['ingredients'] = error_message
        if tags is None:
            errors['tags'] = error_message
        if name is None:
            errors['name'] = error_message
        if text is None:
            errors['text'] = error_message
        if cooking_time is None:
            errors['cooking_time'] = error_message

        if errors:
            raise serializers.ValidationError(errors)
        return data

    def to_representation(self, instance):
        return RecipeReadSerializer(
            data=instance, context=self.context
        ).to_representation(instance)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientrecipe_set', None)
        tags = validated_data.pop('tags', None)
        super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredientrecipe_set.all().delete()
        add_ingredients(instance, ingredients)
        instance.save()
        return instance
