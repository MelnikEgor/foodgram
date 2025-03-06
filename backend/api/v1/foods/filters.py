from django_filters import rest_framework as filters_dj

from foods.models import Recipe


class RecipeFilter(filters_dj.FilterSet):
    tags = filters_dj.CharFilter(method='filter_by_tags')
    author = filters_dj.NumberFilter(field_name='author__id')
    is_favorited = filters_dj.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters_dj.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_by_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist(name)
        return queryset.filter(tags__slug__in=tags).distinct()

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
