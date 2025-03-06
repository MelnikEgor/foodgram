from rest_framework import mixins, permissions, viewsets
from rest_framework.filters import SearchFilter

from api.v1.mixins import CastomUpdateModelMixin
from api.v1.permissions import IsAdminOrModerOrReadOnly, IsAdminOrReadOnly


class BaseNoRetrieveAndNoUpdataViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class BaseExceptFullUpdataViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    CastomUpdateModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAdminOrModerOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
