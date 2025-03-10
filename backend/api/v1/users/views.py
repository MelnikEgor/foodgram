from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.v1.serializers import (
    FollowSerializer,
    PasswordSerializer,
    UserAvatarSerializer,
    UserReadSerializer,
    UserWriteSerializer
)
from users.models import Follow


User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """Представление пользователя."""

    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserWriteSerializer
        return UserReadSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def me(self, request):
        """Получить свою страницу."""

        serializer = UserReadSerializer(
            request.user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['PUT'],
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar'
    )
    def me_avatar(self, request):
        """Добавление автара пользователю."""

        user = get_object_or_404(self.queryset, username=request.user)
        serializer = UserAvatarSerializer(
            user,
            data=request.data,
        )
        if serializer.is_valid(raise_exception=True):
            user.avatar = serializer.validated_data['avatar']
            user.save()
            return Response(serializer.data)

    @me_avatar.mapping.delete
    def delete_me_avatar(self, request):
        """Удаление аватара у пользователя."""

        user = get_object_or_404(self.queryset, username=request.user)
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        """Получения списка подписок."""

        subscribers = []
        for follower in request.user.followers.all():
            subscribers.append(follower.following)
        users = User.objects.filter(username__in=subscribers)
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = FollowSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = FollowSerializer(
            users,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        """Подписаться на пользователя."""

        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            return Response(
                {'errors': 'Нельзя оформить подписку на себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = FollowSerializer(
            user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        obj, created = Follow.objects.get_or_create(
            following=user,
            user=request.user
        )
        if not created:
            return Response(
                {'errors': 'Вы уже подписанны на данного пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk=None):
        """Отписаться от пользователя."""

        user = get_object_or_404(User, pk=pk)
        follow = Follow.objects.filter(following=user, user=request.user)
        if not follow.exists():
            return Response(
                {'errors': 'Вы не подписанны на данного пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=(IsAuthenticated,),
        url_path='set_password'
    )
    def set_password(self, request):
        """Смена пароля."""

        user = get_object_or_404(User, username=request.user)
        serializer = PasswordSerializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
