from django.contrib import admin
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


admin.site.empty_value_display = 'Не задано'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    # inlines = (
    #     TitleInline,
    # )
    list_display = (
        'name',
        'author'
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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    # inlines = (
    #     TitleInline,
    # )
    list_display = (
        'name',
        'measurement_unit'
    )
    search_fields = (
        'name',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    # inlines = (
    #     TitleInline,
    # )
    list_display = (
        'name',
        'slug'
    )
    search_fields = (
        'name',
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    # inlines = (
    #     TitleInline,
    # )
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
    # inlines = (
    #     TitleInline,
    # )
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
