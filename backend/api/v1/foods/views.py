import hashlib

from django.contrib.auth import get_user_model
from django.db.models import Sum
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
    RecipeReadSerializer,
    RecipeWriteSerializer,
    TagSerializer
)
from .utils import shopping_cart
from api.v1.mixins import CustomUpdateModelMixin
from api.v1.permissions import IsAuthorOrReadOnly
from api.v1.utils import actions_delete, actions_add
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
    serializer_class = RecipeReadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        return super().get_serializer_class()

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

        return actions_add(request, pk, Favorite)

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

        ingredients = User.objects.filter(
            username=request.user
        ).values_list(
            'shopping_carts__recipe__ingredients__name',
            'shopping_carts__recipe__ingredients__measurement_unit'
        ).annotate(
            amount=Sum('shopping_carts__recipe__ingredientrecipe__amount')
        )
        return shopping_cart(ingredients)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в карту покупок."""

        return actions_add(request, pk, ShoppingCart)

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
