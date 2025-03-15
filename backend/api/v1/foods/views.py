import hashlib

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .base_views import ListRetrieveViewSet
from .filters import RecipeFilter
from .serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer
)
from api.v1.base_funk import actions_delete, actions_for_view
from api.v1.mixins import CustomUpdateModelMixin
from api.v1.permissions import IsAuthorOrReadOnly
from backend.constants import SHORT_URL_LENGTH
from backend.settings import ROOT_HOST
from foods.models import (
    Favorite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    URLRecipe
)


User = get_user_model()


class TagViewSet(ListRetrieveViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    CustomUpdateModelMixin,
    viewsets.GenericViewSet
):
    """Представление рецепта."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""

        return actions_for_view(request, pk, Favorite)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удаление рецепта из избраного."""

        return actions_delete(request, pk, Favorite)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """Скачивание карты покупок с необходимыми ингредиентами."""

        shopping = 'Список покупок:\n'
        shopping_cart = {}
        user = get_object_or_404(User, username=request.user)
        recipes_data = user.shopping_cart.all()
        for recipe_data in recipes_data:
            recipe_obj = recipe_data.recipe
            for ingredient_data in recipe_obj.ingredientrecipe_set.all():
                product = (ingredient_data.ingredient.name + ' ('
                           + ingredient_data.ingredient.measurement_unit + ')')
                if product not in shopping_cart.keys():
                    shopping_cart[product] = 0
                shopping_cart[product] += ingredient_data.amount
        for name_ingredient, amount_ingredient in shopping_cart.items():
            shopping += f'- {name_ingredient}: {amount_ingredient}\n'
        response = HttpResponse(shopping, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping.txt"'
        return response

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в карту покупок."""

        return actions_for_view(request, pk, ShoppingCart)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удаление рецепта из карты покупок."""

        return actions_delete(request, pk, ShoppingCart)

    @action(
        detail=True,
        permission_classes=(AllowAny,),
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Генерация короткой ссылки."""

        recipe = get_object_or_404(Recipe, pk=pk)
        short_url = hashlib.md5(
            str(recipe.id).encode()
        ).hexdigest()[:SHORT_URL_LENGTH]
        url, _ = URLRecipe.objects.get_or_create(
            recipe=recipe,
            defaults={
                'full_url': f'/recipes/{pk}',
                'short_url': short_url
            }
        )
        return Response({'short-link': f'{ROOT_HOST}/s/{url.short_url}'})


@api_view()
def redirect_view(request, short_link):
    """View функция для редиректа по короткой ссылке."""

    urls_recipe = get_object_or_404(URLRecipe, short_url=short_link)
    return redirect(urls_recipe.full_url)
