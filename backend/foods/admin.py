from django.contrib import admin
from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
    URLRecipe
)


admin.site.empty_value_display = 'Не задано'


@admin.register(URLRecipe)
class URLRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'full_url',
        'short_url'
    )
    search_fields = (
        'recipe',
        'full_url',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'count_is_favorite'
    )
    search_fields = (
        'name',
        'author'
    )
    list_filter = (
        'tags',
    )
    list_display_links = (
        'name',
    )

    def count_is_favorite(self, obj):
        return obj.favorites.all().count()

    count_is_favorite.short_description = 'Количество добавлений в "Избранное"'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = (
        'name',
    )


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount'
    )
    search_fields = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )
    search_fields = (
        'name',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    search_fields = (
        'user',
        'recipe'
    )
    list_filter = (
        'user',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    search_fields = (
        'user',
        'recipe'
    )
    list_filter = (
        'user',
    )
