from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.foods.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet
)
from api.v1.users.views import UserViewSet


router_api_v1 = DefaultRouter()

router_api_v1.register(r'users', UserViewSet, basename='users')
router_api_v1.register(r'tags', TagViewSet, basename='tags')
router_api_v1.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router_api_v1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_api_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
