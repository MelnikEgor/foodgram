from django.http import HttpResponse

from foods.models import IngredientRecipe


def add_ingredients(recipe, ingredients):
    """Добавление ингредиентов в рецепт."""

    for ingredient in ingredients:
        ingredient_obj = ingredient.pop('ingredient')
        amount = ingredient.pop('amount')
        IngredientRecipe.objects.create(
            amount=amount,
            recipe=recipe,
            ingredient=ingredient_obj
        )


def shopping_cart(ingredients):
    """Формирование файла списка покупок."""

    shopping = 'Список покупок:\n'
    for ingredient, measurement_unit, amount in ingredients:
        shopping += f'{ingredient} ({measurement_unit}): {amount}\n'
    response = HttpResponse(shopping, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="shopping.txt"'
    return response
