from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from backend.constants import (
    INGREDIENT_NAME_MAX_LENGTH,
    MEASUREMENT_UNIT_MAX_LENGTH,
    NAME_LENGTH,
    RECIPE_NAME_MAX_LENGTH,
    TAG_NAME_MAX_LENGTH,
    TAG_SLUG_MAX_LENGTH
)


User = get_user_model()


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название тега',
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'Слаг',
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:NAME_LENGTH]


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(
        'Название ингридиента',
        max_length=INGREDIENT_NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['measurement_unit', 'name'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return self.name[:NAME_LENGTH]


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(
        'Название рецепта',
        max_length=RECIPE_NAME_MAX_LENGTH
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                1,
                'Время приготовления не может быть меньше 1 минуты.'
            ),
        ]
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/images/'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)
        default_related_name = 'recipes'

    def __str__(self):
        return self.name[:NAME_LENGTH]


class URLRecipe(models.Model):
    """Модель ссылки."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    full_url = models.CharField('Полный URL.', max_length=128)
    short_url = models.CharField('Короткий URL.', max_length=128)

    class Meta:
        verbose_name = 'ссылка'
        verbose_name_plural = 'Ссылки'

    def __str__(self):
        return self.recipe[:NAME_LENGTH]


class IngredientRecipe(models.Model):
    """Связная модель ингредиентов в рецепте."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                1,
                'Количество ингредиентов не может быть меньше 1.'
            ),
        ]
    )

    class Meta:
        verbose_name = 'ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_for_recipe'
            )
        ]

    def __str__(self):
        return f'{self.recipe}'


class RecipesIn(models.Model):
    """Модель карты покупок."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Favorite(RecipesIn):
    """Модель избранных рецептов."""

    class Meta:
        verbose_name = 'избраное'
        verbose_name_plural = 'Избраное'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_recipe'
            )
        ]
        default_related_name = 'favorites'

    def __str__(self):
        return f'{self.recipe} избранный рецепт {self.user}'


class ShoppingCart(RecipesIn):
    """Модель карты покупок."""

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_in_shopping_card'
            )
        ]
        default_related_name = 'shopping_cart'

    def __str__(self):
        return f'{self.recipe} рецепт в списке покупок у {self.user}'
