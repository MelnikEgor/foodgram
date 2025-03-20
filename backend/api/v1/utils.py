from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from api.v1.foods.recipe_short_serializer import RecipeShortReadSerializer
from foods.models import Recipe


def actions_add(request, pk, model):
    recipe = get_object_or_404(Recipe, pk=pk)
    serializer = RecipeShortReadSerializer(recipe, data=request.data)
    serializer.is_valid(raise_exception=True)
    obj, created = model.objects.get_or_create(
        recipe=recipe,
        user=request.user
    )
    if not created:
        return Response(
            {'errors': 'Рецепт уже добален.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def actions_delete(request, pk, model):
    recipe = get_object_or_404(Recipe, pk=pk)
    count_object = model.objects.filter(
        recipe=recipe,
        user=request.user
    ).delete()[0]
    if not count_object:
        return Response(
            {'errors': 'Рецепт уже удален.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


def check_field(self, obj):
    user = self.context.get('request').user
    return user.is_authenticated and obj.filter(user=user).exists()
