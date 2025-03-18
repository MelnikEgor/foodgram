from rest_framework.pagination import PageNumberPagination

from backend.constants import PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация."""

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = page_size
