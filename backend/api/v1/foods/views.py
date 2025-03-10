import hashlib

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from api.v1.base_funk import actions_for_view, actions_delete
from api.v1.mixins import CastomUpdateModelMixin
from api.v1.permissions import IsAuthorOrReadOnly
from api.v1.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer
)
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


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    pagination_class = None

    # def get_queryset(self):
    #     search_query = self.request.query_params.get('name')
    #     queryset = Ingredient.objects.all()
    #     if search_query:
    #         queryset = queryset.filter(name__istartswith=search_query.lower())
    #     return queryset


class RecipeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    CastomUpdateModelMixin,
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
        permission_classes=(IsAuthenticated, ),
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """Добавление рецепта в избранное."""

        return actions_for_view(request, pk, Favorite)
        # recipe = get_object_or_404(Recipe, pk=pk)
        # serializer = RecipeShortReadSerializer(recipe, data=request.data)
        # serializer.is_valid(raise_exception=True)
        # obj, created = Favorite.objects.get_or_create(
        #     recipe=recipe,
        #     user=request.user
        # )
        # if not created:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """Удаление рецепта из избраного."""

        return actions_delete(request, pk, Favorite)

        # recipe = get_object_or_404(Recipe, pk=pk)
        # favorite = Favorite.objects.filter(recipe=recipe, user=request.user)
        # if not favorite.exists():
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # favorite.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)

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
            print(name_ingredient, amount_ingredient)
            shopping += f'- {name_ingredient}: {amount_ingredient}\n'
        response = HttpResponse(shopping, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping.txt"'
        return response

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated, ),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в карту покупок."""

        return actions_for_view(request, pk, ShoppingCart)
        # recipe = get_object_or_404(Recipe, pk=pk)
        # serializer = RecipeShortReadSerializer(recipe)
        # obj, created = ShoppingCart.objects.get_or_create(
        #     recipe=recipe,
        #     user=request.user
        # )
        # if not created:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """Удаление рецепта из карты покупок."""

        return actions_delete(request, pk, ShoppingCart)
        # recipe = get_object_or_404(Recipe, pk=pk)
        # shopping_card = ShoppingCart.objects.filter(
        #     recipe=recipe,
        #     user=request.user
        # )
        # if not shopping_card.exists():
        #     return Response(status=status.HTTP_400_BAD_REQUEST)
        # shopping_card.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Генерация короткой ссылки."""

        recipe = get_object_or_404(Recipe, pk=pk)
        short_url = hashlib.md5(str(recipe.id).encode()).hexdigest()[:6]
        # current_url = f'/recipes/{pk}'
        # current_url = request.path.split('/')
        # current_url.pop()
        # current_url.pop()
        # current_url = '/'.join(current_url)
        url, _ = URLRecipe.objects.get_or_create(
            full_url=f'/recipes/{pk}',
            defaults={'short_url': short_url}
        )
        print(short_url)
        return Response({'short-link': f'{ROOT_HOST}/s/{url.short_url}'})


@api_view()
def redirect_view(request, short_link):
    """View функция для редиректа по короткой ссылке."""

    urls_recipe = get_object_or_404(URLRecipe, short_url=short_link)
    print('#', urls_recipe.full_url)
    print(redirect(urls_recipe.full_url))
    return redirect(urls_recipe.full_url)
