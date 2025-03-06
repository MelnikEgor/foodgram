import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from .mixins import UserameNotMeMixin
from foods.models import Ingredient, IngredientRecipe, Recipe, Tag


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Сериализатор обработки изображений."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserWriteSerializer(serializers.ModelSerializer, UserameNotMeMixin):
    """Сериализатор регистрации пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения пользователей."""

    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.subscriber.filter(user=user).exists()
        return False


class RecipeShortReadSerializer(serializers.ModelSerializer):
    """Сериализатор короткого представления рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок пользователя."""

    # recipes = RecipeShortReadSerializer(read_only=True, many=True)
    # recipes_count = serializers.SerializerMethodField(
    #     'get_recipes_count',
    #     read_only=True,
    # )
    recipes = serializers.SerializerMethodField(
        # 'get_recipes_count',
        # read_only=True,
        # many=True
    )
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass
        serializer = RecipeShortReadSerializer(
            recipes,
            read_only=True,
            many=True
        )
        return serializer.data

    # def get_recipes_count(self, obj):
    #     return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.subscriber.filter(user=user).exists()
        return False


class PasswordSerializer(serializers.ModelSerializer):
    """Сериализатор смены пароля."""

    new_password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'blank': 'Новый пароль не может быть пустым.',
        },
        # source='*'
    )
    current_password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'blank': 'Текущий пароль не может быть пустым.',
        },
        # source='*'
    )

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def validate(self, attrs):
        current_password = attrs['current_password']
        if not self.instance.check_password(current_password):
            raise serializers.ValidationError(
                {
                    'current_password': 'Текущий пароль не такой.'
                }
            )
        if attrs['new_password'] == current_password:
            raise serializers.ValidationError(
                {
                    'new_password': 'Новый пароль похож на старый.'
                }
            )
        return attrs


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара пользователя."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = (
            'avatar',
        )


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

    def validate(self, data):
        errors = {}
        amount = data.get('amount', None)
        ingredient = data.get('ingredient', None)
        if amount is None:
            errors['amount'] = 'Обязательное поле.'
        elif amount < 1:
            errors['amount'] = 'Количество ингредиентов должно быть меньше 1.'
        if ingredient is None:
            errors['id'] = 'Обязательное поле.'
        if errors:
            raise serializers.ValidationError(errors)
        return data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    author = UserReadSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        write_only=True,
        allow_empty=False
    )
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

    def validate(self, data):
        errors = {}
        ingredients = data.get('ingredientrecipe_set', None)
        if ingredients is None:
            errors['ingredients'] = 'Обязательное поле.'
        else:
            ingredient_ids = [
                ingredient['ingredient'].id for ingredient in ingredients
            ]
            if len(ingredient_ids) != len(set(ingredient_ids)):
                errors['ingredients'] = (
                    'Нельзя добавить один ингредиент несколько раз.'
                )

        tags = data.get('tags', None)
        if tags is None:
            errors['tags'] = 'Обязательное поле.'
        elif len(tags) != len(set(tags)):
            errors['tags'] = 'Нельзя добавить один тег несколько раз'

        name = data.get('name', None)
        if name is None:
            errors['name'] = 'Обязательное поле.'

        text = data.get('text', None)
        if text is None:
            errors['text'] = 'Обязательное поле.'

        cooking_time = data.get('cooking_time', None)
        if cooking_time is None:
            errors['cooking_time'] = 'Обязательное поле.'

        if errors:
            raise serializers.ValidationError(errors)
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        return representation

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.shopping_cart.filter(user=user).exists()
        return False

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_obj = ingredient.pop('ingredient')
            amount = ingredient.pop('amount')
            IngredientRecipe.objects.create(
                amount=amount,
                recipe=recipe,
                ingredient=ingredient_obj
            )
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredientrecipe_set', None)
        tags = validated_data.pop('tags', None)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.ingredientrecipe_set.all().delete()
            for ingredient in ingredients:
                IngredientRecipe.objects.create(
                    recipe=instance,
                    ingredient=ingredient['ingredient'],
                    amount=ingredient['amount']
                )

        instance.save()
        return instance
